from glob import iglob
import os
import re
from xml.etree import ElementTree

TOK = 'tok'
INTERVIEWEE_T_CAT = 'tok_part'
INTERVIEWER_T_CAT = 'tok_int'
INTERVIEWEE_T_CAT_CLEAN = 'tok_part_clean'
INTERVIEWER_T_CAT_CLEAN = 'tok_int_clean'
tok_tier_cats = {INTERVIEWEE_T_CAT, INTERVIEWER_T_CAT}
INTERVIEWER_SPK = 'INT'
INTERVIEWER_SPK_CLEAN = 'INT_CLEAN'
INTERVIEWEE_SPK = 'PART'
INTERVIEWEE_SPK_CLEAN = 'PART_CLEAN'
COM_SPK = 'SPKCOM'
COM_ABBR = 'COM'

ATTR_ID = 'id'
ATTR_CAT = 'category'
ATTR_SPK = 'speaker'
ATTR_TYPE = 'type'

IN_DIR = 'data/original'
OUT_DIR = 'data/0/SeiKo/'

REQUIREMENTS = [  # the final boolean value is a requirement flag -- this flag is problematic, just use it for now
    ('t', None, INTERVIEWEE_T_CAT, True),
    ('t', INTERVIEWEE_SPK_CLEAN, INTERVIEWEE_T_CAT_CLEAN, True),
    ('t', None, INTERVIEWER_T_CAT, False),
    ('t', INTERVIEWER_SPK_CLEAN, INTERVIEWER_T_CAT_CLEAN, False),
    ('t', COM_ABBR, COM_ABBR, False)
]


def is_interviewee(abbr):
    if abbr is None:
        return False
    return re.match(r'[AB][0-9][0-9]', abbr.strip())


def add_speaker(xml, speaker_id, speaker_abbr):
    parent = xml.find(f'.//speakertable')
    spk = ElementTree.SubElement(parent, 'speaker', {'id': speaker_id})
    ElementTree.SubElement(spk, 'abbreviation').text = speaker_abbr    


def get_fixed_speaker_map(xml):
    spk_map = {}
    speaker_table = xml.find(f'.//speakertable')
    # add missing speakers
    existing_speaker_abbrs = {s.text for s in xml.find(f'.//speakertable/speaker/abbreviation')}
    for (speaker_id, speaker_abbr) in [(COM_SPK, COM_ABBR), 
                                       (INTERVIEWEE_SPK_CLEAN, INTERVIEWEE_SPK_CLEAN),
                                       (INTERVIEWER_SPK_CLEAN, INTERVIEWER_SPK_CLEAN)]:
        if speaker_abbr not in existing_speaker_abbrs:
            add_speaker(xml, speaker_id, speaker_abbr)
    spk_map[''] = COM_ABBR  # default speaker, we should soon get rid of this dirty workaround
    # collect
    for speaker in xml.findall(f'.//speakertable/speaker'):
        abbr = speaker.find('abbreviation')
        if abbr is not None:
            if is_interviewee(abbr.text):
                abbr.text = INTERVIEWEE_SPK
            spk_map[speaker.attrib[ATTR_ID]] = abbr.text
    # add interviewer    
    if INTERVIEWER_SPK not in set(spk_map.values()):
        add_speaker(xml, INTERVIEWER_SPK, INTERVIEWER_SPK)
        spk_map[INTERVIEWER_SPK] = INTERVIEWER_SPK
    return spk_map


if __name__ == '__main__':
    if not os.path.exists(OUT_DIR):
        os.mkdir(OUT_DIR)
    for path in iglob(f'{IN_DIR}/**exb', recursive=True):
        print('Starting', path, '...')
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
        has_interviewer = False
        for tier in tok_tiers:            
            spk_id = tier.attrib[ATTR_SPK]
            if spk_id not in speaker_map:
                continue
            spk_name = speaker_map[spk_id]
            if spk_name.strip() == INTERVIEWER_SPK:
                # is interviewer tier
                tier.attrib[ATTR_CAT] = INTERVIEWER_T_CAT
                has_interviewer = True
            else:
                # is interviewee / participant tier
                tier.attrib[ATTR_CAT] = INTERVIEWEE_T_CAT
            tier.attrib[ATTR_TYPE] = 't'
            tier.attrib['display-name'] = f'{spk_name} [{tier.attrib["category"]}]'
        if not has_interviewer:            
            interviewer_speaker_id = {v: k for k, v in speaker_map.items()}[INTERVIEWER_SPK]
            parent = xml.find('.//basic-body')
            ElementTree.SubElement(parent, 'tier', {
                ATTR_SPK: interviewer_speaker_id,
                ATTR_TYPE: 't',
                'display_name': 'INT [tok_int]',
                ATTR_CAT: INTERVIEWER_T_CAT,
                ATTR_ID: 'TIER_INT_EMPTY'
            })
        com_tier = xml.find(f'.//tier[@{ATTR_CAT}="COM"]')
        if com_tier is not None:
            com_tier.attrib['speaker'] = COM_SPK        
        for tier in xml.findall('.//tier'):
            if tier.attrib[ATTR_CAT] in tok_tier_cats:
                tier.attrib[ATTR_TYPE] = 't'
                continue
            tier.attrib[ATTR_TYPE] = 'a'            
            if ATTR_SPK not in tier.attrib:
                tier.attrib[ATTR_SPK] = ''
            tier.attrib['display-name'] = f'{speaker_map[tier.attrib[ATTR_SPK]]} [{tier.attrib["category"]}]'        
        if com_tier is not None:
            com_tier.attrib['type'] = 't'
        for tier_type, speaker, category, required in REQUIREMENTS:
            tier = xml.find(f'.//tier[@{ATTR_CAT}="{category}"]')
            if tier is None:
                print('WARNING: Tier', category, 'does not exist!')
                if required:
                    exit(1)            
                continue
            if speaker is not None:
                tier.attrib[ATTR_SPK] = speaker
            tier.attrib[ATTR_TYPE] = tier_type
        # rewrite v
        for old_speaker in ('SPK0', 'SPK1', 'SPK2'):
            if old_speaker not in speaker_map:
                continue
            new_speaker = f'{speaker_map[old_speaker]}_CLEAN'
            tier = xml.find(f'.//tier[@{ATTR_CAT}="v"][@{ATTR_SPK}="{old_speaker}"]')
            if tier is None:
                print('No v tier for', old_speaker, '/', speaker_map[old_speaker])
            else:
                tier.attrib[ATTR_SPK] = new_speaker
        out_path = os.path.join(OUT_DIR, os.path.basename(path))
        xml.write(out_path, encoding='utf-8', xml_declaration=True)
