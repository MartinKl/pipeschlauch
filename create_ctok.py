from argparse import ArgumentParser
import os
import re
import sys
from xml.etree import ElementTree


def read_timeline(exb):
    if int(sys.version[0]) < 3 or int(sys.version[2:4]) < 7:
        raise RuntimeError("Python version is too old. You need at least python 3.7 since this script relies on dict"
                           " insertion order.")
    tlis = exb.findall('.//common-timeline/tli')  # provides tlis in original order from python 3.7
    ordered_ids = []
    needs_time = []
    for tli in tlis:
        if not 'time' in tli.attrib:
            needs_time.append(len(ordered_ids))
        elif needs_time:
            step = (float(tli.attrib['time']) - last_time) / (len(needs_time) + 1)
            for index in needs_time:
                last_time += step
                untimed_tli = exb.find(f'.//tli[@id="{ordered_ids[index]}"]')
                untimed_tli.attrib['time'] = str(last_time)
            needs_time.clear()
            last_time = float(tli.attrib['time'])
        else:
            last_time = float(tli.attrib['time'])
        ordered_ids.append(tli.attrib['id'])
    return ordered_ids


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
    print('Starting', path, '...')
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
    if tok_tier is None:
        print(f'{path} does not have a tier `{tok_name}` and is skipped.')
        return
    forbidden_intervals = set()
    excl_tier = exb.find(f'.//tier[@category="{excl_name}"]')
    if excl_tier is None:
        print(f'{path} does not have a tier `{excl_name}` and is skipped.')
    else:
        excl_spk = excl_tier.attrib['speaker']
        excl_regions = [(event.attrib['start'], event.attrib['end']) for event in excl_tier]
        for start_id, end_id in excl_regions:
            start_i = tl.index(start_id)
            end_i = tl.index(end_id)
            forbidden_intervals.update((tl[a], tl[a + 1]) for a in range(start_i, end_i))
    tier_id = f'TIE{len(parent)}'
    add_speaker(exb,f'c{excl_spk}', f'PART_CLEAN')
    ctok_tier = ElementTree.SubElement(parent,
                                       'tier',
                                       dict(id=tier_id,
                                            speaker=f'c{excl_spk}',
                                            category=f'c{tok_name}',
                                            type='t'))
    v_tier = exb.find(f'.//tier[@category="unit"][@speaker="{excl_spk}"]')
    groups = []
    for event in v_tier:
        start = tl.index(event.attrib['start'])
        end = tl.index(event.attrib['end'])
        groups.append((set(range(start, end)), event.text))

    v_clean_tier = ElementTree.SubElement(parent,
                                          'tier',
                                          dict(id=f'TIE{len(parent)}',
                                               speaker=f'c{excl_spk}',
                                               type='a',
                                               category='unit'))
    for event in sorted(tok_tier, key=lambda e: tl.index(e.attrib['start'])):
        time_slot = (event.attrib['start'], event.attrib['end'])
        if time_slot not in forbidden_intervals and not re.match(excl_pattern, event.text.strip()):
            ElementTree.SubElement(ctok_tier, 'event', dict(start=time_slot[0], end=time_slot[1])).text = event.text
            index = tl.index(time_slot[0])
            for (g, label) in groups:
                if index in g:
                    ElementTree.SubElement(v_clean_tier, 'event', dict(start=tl[min(g)], end=tl[max(g) + 1])).text = label
                    groups.remove((g, label))
                    break
    exb.write(output_path, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    parser = ArgumentParser(description="This script creates the ctok tier from a tok and an excl tier.")
    parser.add_argument('file_or_dir', type=str, help='Path to EXMARaLDA file(s).')
    parser.add_argument('target_file_or_dir', type=str, help='Path to write output to.')
    parser.add_argument('--excl-values',
                        type=str,
                        default=r'•|([0-9][0-9]?)|(\([0-9]+\.[0-9]+\))',
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
