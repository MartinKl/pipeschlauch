from glob import iglob
import os
from xml.etree import ElementTree

TOK = 'tok'
INTERVIERWEE_NAME = 'tok_part'  # kannst du anfangs noch ändern
INTERVIEWER_NAME = 'tok_int'  # das auch
INTERVIEWER_SPK = 'INT'

ATTR_ID = 'id'
ATTR_CAT = 'category'
ATTR_SPK = 'speaker'
ATTR_TYPE = 'type'

IN_DIR = 'data/original'
OUT_DIR = 'data/0/SeiKo/'


def get_speaker_map(xml):
    spk_map = {}
    for speaker in xml.findall(f'.//speaker'):
        abbr = speaker.find('abbreviation')
        if abbr is not None:
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
        speaker_map = get_speaker_map(xml)
        xpath_tok = f'.//tier[@{ATTR_CAT}="{TOK}"]'
        tok_tiers = xml.findall(xpath_tok)
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
                tier.attrib[ATTR_CAT] = INTERVIEWER_NAME
            else:
                # is interviewee / participant tier
                tier.attrib[ATTR_CAT] = INTERVIERWEE_NAME
            tier.attrib[ATTR_TYPE] = 't'
            tier.attrib['display-name'] = f'{spk_name} [{tier.attrib["category"]}]'
        for tier in set(xml.findall('.//tier')).difference(tok_tiers):
            tier.attrib[ATTR_TYPE] = 'a'
        out_path = os.path.join(OUT_DIR, os.path.basename(path))
        xml.write(out_path, encoding='utf-8', xml_declaration=True)
