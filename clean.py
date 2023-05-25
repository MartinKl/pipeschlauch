from glob import iglob
import os
import re
from xml.etree import ElementTree

TOK = 'tok'
INTERVIEWEE_T_CAT = 'tok_part'  # kannst du anfangs noch ändern
INTERVIEWER_T_CAT = 'tok_int'  # das auch
tok_tier_cats = {INTERVIEWEE_T_CAT, INTERVIEWER_T_CAT}
INTERVIEWER_SPK = 'INT'
INTERVIEWEE_SPK = 'PART'
COM_SPK = 'SPKCOM'
COM_ABBR = 'COM'

ATTR_ID = 'id'
ATTR_CAT = 'category'
ATTR_SPK = 'speaker'
ATTR_TYPE = 'type'

IN_DIR = 'data/original'
OUT_DIR = 'data/0/SeiKo/'


def is_interviewee(abbr):
    if abbr is None:
        return False
    return re.match(r'[AB][0-9][0-9]', abbr.strip())


def get_fixed_speaker_map(xml):
    spk_map = {}
    # add com speaker
    parent = xml.find(f'.//speakertable')
    if parent.find(f'./speaker[@id="{COM_SPK}"]') is None:
        spk = ElementTree.SubElement(parent, 'speaker', {'id': COM_SPK})
        ElementTree.SubElement(spk, 'abbreviation').text = COM_ABBR
        ElementTree.SubElement(spk, 'sex').text = 'u'
        spk_map[''] = COM_ABBR
    # collect
    for speaker in xml.findall(f'.//speakertable/speaker'):
        abbr = speaker.find('abbreviation')
        if abbr is not None:
            if is_interviewee(abbr.text):
                abbr.text = INTERVIEWEE_SPK
            spk_map[speaker.attrib[ATTR_ID]] = abbr.text
    return spk_map


if __name__ == '__main__':
    if not os.path.exists(OUT_DIR):
        os.mkdir(OUT_DIR)
    for path in iglob(f'{IN_DIR}/**exb', recursive=True):
        xml = ElementTree.parse(path)
        project_name = xml.find('.//project-name')
        if project_name is not None:
            project_name.text = ''
        speaker_map = get_fixed_speaker_map(xml)
        tok_tiers = xml.findall(f'.//tier[@{ATTR_CAT}="{TOK}"]') \
                  + xml.findall(f'.//tier[@{ATTR_CAT}="{INTERVIEWEE_T_CAT}"]') \
                  + xml.findall(f'.//tier[@{ATTR_CAT}="{INTERVIEWER_T_CAT}"]')
        if tok_tiers is None:
            print('No tok tiers in', path)
            continue
        for tier in tok_tiers:
            spk_id = tier.attrib[ATTR_SPK]
            if spk_id not in speaker_map:
                continue
            spk_name = speaker_map[spk_id]
            if spk_name.strip() == INTERVIEWER_SPK:
                # is interviewer tier
                tier.attrib[ATTR_CAT] = INTERVIEWER_T_CAT
            else:
                # is interviewee / participant tier
                tier.attrib[ATTR_CAT] = INTERVIEWEE_T_CAT
            tier.attrib[ATTR_TYPE] = 't'
            tier.attrib['display-name'] = f'{spk_name} [{tier.attrib["category"]}]'
        for tier in xml.findall('.//tier'):
            if tier.attrib[ATTR_CAT] in tok_tier_cats:
                tier.attrib[ATTR_TYPE] = 't'
                continue
            tier.attrib[ATTR_TYPE] = 'a'
            k = tier.attrib[ATTR_SPK] if ATTR_SPK in tier.attrib else ''
            spk_name = speaker_map[k]
            tier.attrib['display-name'] = f'{spk_name} [{tier.attrib["category"]}]'
        out_path = os.path.join(OUT_DIR, os.path.basename(path))
        xml.write(out_path, encoding='utf-8', xml_declaration=True)
