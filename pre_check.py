from argparse import ArgumentParser
from collections import defaultdict
import os
from xml.etree import ElementTree


_FAIL = '❌'
_WARN = '⚠'
_PASS = '✓'
_INVALID = '?'


def check_tiers(xml, **kwargs):
    all_tiers = {(tier.get('speaker'), tier.attrib['category'], tier.attrib['type']) for tier in xml.findall('.//tier')}
    by_spk = defaultdict(set)
    for spk, cat, tpe in all_tiers:
        by_spk[spk].add((cat, tpe))
    expected_tiers = [
        # (speaker, category, type, required)
        (0, 'com', 't', False),
        (1, 'tok_part', 't', True),
        (1, 'unit', 'a', True),
        (2, 'tok_int', 't', False)
    ]
    speakers = [None]
    result = []
    has_errors = False
    for spk, cat, tpe, req in expected_tiers:
        if spk >= len(speakers):
            spk_id = None
            for s, tiers in by_spk.items():
                for c, t in tiers:
                    if c == cat:
                        spk_id = s
                        break
                if spk_id is not None:
                    break
            speakers.append(spk_id)
        speaker_id = speakers[spk]
        tier_exists = any(c == cat for _, c, _ in all_tiers)
        speaker_correct = any(c == cat for c, _ in by_spk[speaker_id])
        type_correct = (cat, tpe) in by_spk[speaker_id]
        correct = speaker_correct and type_correct
        total = tier_exists and correct
        result.append(f'{_PASS if total else (_FAIL if req or tier_exists and not correct else _PASS)} TIER `{cat}`')
        result.append(f'  {_PASS if tier_exists else (_FAIL if req else _WARN)} exists')
        result.append(f'  {_INVALID if not tier_exists else (_PASS if speaker_correct else _FAIL)}'
                      f' correct speaker')
        result.append(f'  {_INVALID if not tier_exists else (_PASS if type_correct else _FAIL)}'
                      f' correct type')
        has_errors |= False if total else (True if req and not correct else False)
    return has_errors, result


def valid_events(xml, **kwargs):
    has_errors = any([event.text is None or not event.text.strip() for event in xml.findall('.//event')])
    return has_errors, [f'{_FAIL if has_errors else _PASS} No empty events']


def assignable_spans(xml, **kwargs):
    has_errors = False
    results = []
    timeline = [tli.attrib['id'] for tli in xml.findall('.//tli')]
    for anno_tier in xml.findall(f'.//tier[@type="a"]'):
        speaker = anno_tier.get('speaker')
        cat = anno_tier.attrib['category']
        if speaker is None:
            continue
        tok_tier = xml.find(f'.//tier[@type="t"][@speaker="{speaker}"]')
        if tok_tier is None:
            has_errors = True
            results.append(f'{_FAIL} tier {cat} has no underlying transcription.')
            continue
        tier_has_errors = False
        for span in anno_tier.findall('.//event'):
            start_ix = timeline.index(span.attrib['start'])
            end_ix = timeline.index(span.attrib['end'])
            covered_tokens = any(tok_tier.find(f'./event[@start="{timeline[index]}"]') is not None
                                 for index in range(start_ix, end_ix))
            if not covered_tokens:
                tier_has_errors = True
        if tier_has_errors:
            has_errors = True
            results.append(f'{_FAIL} tier {cat} has spans'
                           f' that cover no events on tier {tok_tier.attrib["category"]}')
        else:
            results.append(f'{_PASS} tier {cat}')
    return has_errors, results


_CONSTRAINTS = {
    'correct tier configuration': check_tiers,
    'no empty events': valid_events,
    'at least one token per span': assignable_spans,
}


if __name__ == '__main__':
    parser = ArgumentParser(description='Run some checks on your data first to avoid frustrating pipeline errors.')
    parser.add_argument('directory', type=str, help='Directory containing the EXMARaLDA files.')
    args = parser.parse_args()
    errors = []
    for root, _, f_names in os.walk(args.directory):
        for f_name in filter(lambda fn: fn.endswith('.exb'), f_names):
            path = os.path.join(root, f_name)
            print('Starting', path)
            exb = ElementTree.parse(path)
            for constraint, fun in _CONSTRAINTS.items():
                failed, report = fun(exb)
                print(os.linesep.join(report), end=os.linesep * 2)
                if failed:
                    errors.append(f'{_FAIL} constraint failed for {path}: {constraint}')
    print('---------')
    print('SUMMARY :')
    print('---------')
    print(os.linesep.join(errors))
    exit(int(bool(len(errors))))
