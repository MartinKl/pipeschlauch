from argparse import ArgumentParser
import os
import re
from xml.etree import ElementTree


def read_timeline(exb):
    tlis = exb.findall('.//common-timeline/tli')
    tlis_with_t = list(map(lambda e: e.attrib['id'],
                           sorted(filter(lambda t: 'time' in t.attrib, tlis),
                                  key=lambda t: float(t.attrib['time']))))
    tlis_without_t = list(map(lambda e: e.attrib['id'],
                              sorted(filter(lambda t: 'time' not in t.attrib, tlis),
                                     key=lambda t: (tlis_with_t.index(t.attrib['id'].split('.')[0]), int(t.attrib['id'].split('.')[-1]))
                                     )
                              )
                          )
    ordered_items = []
    last_stop = 0
    needs_time_value = []
    for id_ in tlis_with_t:
        if needs_time_value:
            end_time = float(exb.find(f'.//common-timeline/tli[@id="{id_}"]').attrib['time'])
            step = (end_time - start_time) / (len(needs_time_value) + 1)
            for untimed_id in needs_time_value:
                start_time += step
                exb.find(f'.//common-timeline/tli[@id="{untimed_id}"]').attrib['time'] = str(start_time)
            needs_time_value.clear()
        ordered_items.append(id_)
        start_time = float(exb.find(f'.//common-timeline/tli[@id="{id_}"]').attrib['time'])
        while last_stop < len(tlis_without_t) and tlis_without_t[last_stop].startswith(f'{id_}.'):
            ordered_items.append(tlis_without_t[last_stop])
            needs_time_value.append(tlis_without_t[last_stop])
            last_stop += 1
    return ordered_items


def read_speaker_table(exb):
    table = exb.findall('.//speakertable/speaker')
    abbr2id = {}
    for speaker in table:
        id_ = speaker.attrib['id'].strip()
        abbr = speaker.find('abbreviation').text.strip()
        abbr2id[abbr] = id_
    return abbr2id


def add_speaker(exb, id_, abbr):
    table = exb.find('.//speakertable')
    spk = ElementTree.SubElement(table, 'speaker', dict(id=id_))
    ElementTree.SubElement(spk, 'abbreviation').text = abbr


def create_ctok(path, output_path, excl_pattern, overwrite=False):
    exb = ElementTree.parse(path)
    parent = exb.find('.//basic-body')
    tl = read_timeline(exb)
    spk_table = read_speaker_table(exb)
    tok_name = 'tok_part'
    existing_ctok = exb.find(f'.//tier[@category="c{tok_name}"]')
    if existing_ctok is not None:
        parent.remove(existing_ctok)
    excl_name = 'excl'
    tok_tier = exb.find(f'.//tier[@category="{tok_name}"]')
    excl_tier = exb.find(f'.//tier[@category="{excl_name}"]')
    excl_spk = excl_tier.attrib['speaker']
    excl_regions = [(event.attrib['start'], event.attrib['end']) for event in excl_tier]
    forbidden_intervals = set()
    for start_id, end_id in excl_regions:
        start_i = tl.index(start_id)
        end_i = tl.index(end_id)
        forbidden_intervals.update((tl[a], tl[a + 1]) for a in range(start_i, end_i))
    if parent is None:
        raise ValueError
    tier_id = f'TIE{len(parent)}'
    add_speaker(exb,f'c{excl_spk}', f'PART_CLEAN')
    ctok_tier = ElementTree.SubElement(parent,
                                       'tier',
                                       dict(id=tier_id,
                                            speaker=f'c{excl_spk}',
                                            category=f'c{tok_name}',
                                            type='t'))
    v_tier = exb.find(f'.//tier[@category="v"][@speaker="{excl_spk}"]')
    groups = []
    for event in v_tier:
        start = tl.index(event.attrib['start'])
        end = tl.index(event.attrib['end'])
        groups.append(set(range(start, end)))

    v_clean_tier = ElementTree.SubElement(parent,
                                          'tier',
                                          dict(id=f'TIE{len(parent)}',
                                               speaker=f'c{excl_spk}',
                                               type='a',
                                               category='v'))
    for event in sorted(tok_tier, key=lambda e: tl.index(e.attrib['start'])):
        time_slot = (event.attrib['start'], event.attrib['end'])
        if time_slot not in forbidden_intervals and not re.match(excl_pattern, event.text.strip()):
            ElementTree.SubElement(ctok_tier, 'event', dict(start=time_slot[0], end=time_slot[1])).text = event.text
            index = tl.index(time_slot[0])
            for g in groups:
                if index in g:
                    ElementTree.SubElement(v_clean_tier, 'event', dict(start=tl[min(g)], end=tl[max(g) + 1])).text = 'v'
                    groups.remove(g)
                    break
    exb.write(output_path, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    parser = ArgumentParser(description="This script creates the ctok tier from a tok and an excl tier.")
    parser.add_argument('file_or_dir', type=str, help='Path to EXMARaLDA file(s).')
    parser.add_argument('target_file_or_dir', type=str, help='Path to write output to.')
    parser.add_argument('--excl-values',
                        type=str,
                        default=r'•|([0-9][0-9]?)',
                        help='Regex describing further values to exclude')
    parser.add_argument('--overwrite', action='store_true', help='overwrite existing ctok tier.')
    args = parser.parse_args()
    if os.path.isdir(args.file_or_dir):
        for root, _, f_names in os.walk(args.file_or_dir):
            for f_name in filter(lambda fn: fn.endswith('.exb'), f_names):
                path = os.path.join(root, f_name)
                outpath = os.path.join(args.target_file_or_dir, os.path.basename(path))
                create_ctok(path, outpath, args.excl_values, args.overwrite)
    else:
        outpath = args.target_file_or_dir \
            if os.path.isfile(args.target_file_or_dir) \
            else os.path.join(args.target_file_or_dir, os.path.basename(args.file_or_dir))
        create_ctok(args.file_or_dir, outpath, args.excl_values, args.overwrite)
