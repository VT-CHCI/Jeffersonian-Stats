import sys
import re
import string
import codes
import os

def remove_non_verbals(txt): # (* ... *)
    nv_pattern = re.compile("\(\*[^\*\)]+\*\)")
    results = nv_pattern.subn('',txt)
    return results

def remove_timestamps(txt):
    # the dot M means multiline
    ts_pattern = re.compile("^[^\[]*\[\d\d:\d\d:\d\d\.\d\d\] ", re.M)
    results = ts_pattern.subn('', txt)
    return results

def remove_speakers(txt):
    speaker_pattern = re.compile("(?:Male|Female|Participant A|Participant B); ")
    results = speaker_pattern.subn('', txt)
    return results

def remove_codes(txt):
    all_codes = []
    for code_type in codes.codes:
        all_codes.extend(codes.codes[code_type])
    codes_pattern = re.compile("|".join(all_codes))
    results = codes_pattern.subn('', txt)
    return results

def strip_lines(txt):
    whitespace_pattern = re.compile("^\s+", re.M)
    results = whitespace_pattern.subn('', txt)
    return results

def remove_empty_brackets(txt):
    empty_pattern = re.compile("\[\]|\[\[\]\]|\[\[\[\]\]\]")
    results = empty_pattern.subn('', txt)
    return results

def get_participant_words(participant, txt):
    return get_participant_words_and_utterances(participant, txt)[participant]['words']

def get_participant_words_and_utterances(participant, txt):
    parsed_results =  strip_lines(remove_empty_brackets(remove_story_teller_markers(remove_codes(remove_timestamps(remove_non_verbals(txt)[0])[0])[0])[0])[0])[0].strip()
    total_participant_words = []
    utterances = []
    # print parsed_results
    for line in parsed_results.split('\n'):
        # print line
        words = line.split()
        # print words
        # if words[0][:len(participant)] == participant:
        if line[:len(participant)] == participant:
            total_participant_words.extend(words[1:])
            if len(words[1:]) > 0:
                utterances.append(words[1:])
    return {
        participant: {
            'words':len(total_participant_words), 
            'utterances': len(utterances)
            }
        }

def remove_story_teller_markers(txt):
    pattern_of_st_markers = re.compile("|".join(codes.story_teller_markers))
    results = pattern_of_st_markers.subn('', txt)
    return results

def determine_story_teller(txt):
    speakers = get_all_speakers(txt)
    pattern_of_st_markers = "|".join(codes.story_teller_markers)
    story_teller_pattern = re.compile(pattern_of_st_markers+".+("+"|".join(speakers)+");")
    results = story_teller_pattern.findall(txt)
    # print results
    results = [r for r in results if len(r)>0 ]
    # print results.group()
    return results[0]

def get_all_speakers(txt):
    speaker_pattern = re.compile("\d\d\] ([^;\n]+);")
    distinct_speakers = set(speaker_pattern.findall(txt))
    return distinct_speakers

def filter_out_laughs(li):
    return [elem for elem in li if elem.find('laugh') < 0]

def get_listener_nv_count(txt):
    listener_nvs = 0
    parsed = strip_lines(remove_timestamps(remove_codes(txt)[0])[0])[0].strip()
    # print parsed
    all_speakers = get_all_speakers(txt)
    simple_nv_pattern = re.compile("\(\*[^\*\)]+\*\)")
    # if listener is None:
    speaker = determine_story_teller(txt)
    listener = all_speakers.difference([speaker]).pop()
    # print all_speakers, speaker, listener

    #find the ones on participant b's line
    # find the ones without participant

    listener_nv_pattern = re.compile("\(\* ?"+listener+"[^\*\)]+\*\)")
    # print '\n'
    for line in parsed.split('\n'):
        words = line.split()
        line_results = filter_out_laughs(listener_nv_pattern.findall(line))

        # if len(line_results) > 0:
        #     print '<cond a>'
        #     print line
        #     print line_results
        listener_nvs += len(line_results)
        if len(words) > 1 and line[:len(listener)] == listener:
            # print '<cond b>'
            unid_results = filter_out_laughs(simple_nv_pattern.findall(line))
            listener_nvs += len(unid_results)
            # if len(unid_results) > 0:
            #     print unid_results
        # listener_nvs += line_results

            # noverbals may not belong to the speaker of the line, in this case the nv will start with participant's identifier
    return listener_nvs

def get_listener_lul_count(txt, listener=None):
    lul_count = 0
    lul_pattern = re.compile("LUL")
    if listener is None:
        all_speakers = get_all_speakers(txt)
        speaker = determine_story_teller(txt)
        listener = all_speakers.difference([speaker]).pop()
    parsed = strip_lines(remove_timestamps(txt)[0])[0].strip()

    for line in parsed.split('\n'):
        words = line.split()
        if len(words[0]) >= len(listener) and words[0][:len(listener)] == listener:
            lul_count += len(lul_pattern.findall(line))
    return lul_count

def get_texts(filename):
    with open(filename, 'r') as f:
        raw_text = f.read()
    # print remove_non_verbals(raw_text)
    # print remove_timestamps(raw_text)
    # print remove_speakers(raw_text)
    parsed_results =  strip_lines(remove_empty_brackets(remove_codes(remove_speakers(remove_timestamps(remove_non_verbals(raw_text)[0])[0])[0])[0])[0])[0].strip()
    # print parsed_results
    # Total Word Count (full word and disfluency instances) 
    total_word_count = len(parsed_results.split())
    total_utterances = len(parsed_results.split('\n'))
    # print total_utterances
    # print determine_story_teller(raw_text)
    # storyteller word count
    # story_teller_count = get_participant_words(determine_story_teller(raw_text), raw_text)
    # story_teller_count = get_participant_words_and_utterances(determine_story_teller(raw_text), raw_text)
    all_speakers = get_all_speakers(raw_text)
    print filename
    print 'Total Word Count (full word and disfluency instances): ', total_word_count
    print 'Total Utterance Count (full stop, continuer, try-marker, and truncated ending instances): ', total_utterances
    print 'Speaker: '+ determine_story_teller(raw_text)
    for speaker in all_speakers:
        print get_participant_words_and_utterances(speaker, raw_text)
    print 'Listener Non-verbal Count ( "(*  *)"" instances, not including laughter)', get_listener_nv_count(raw_text)
    print 'Listener Unilateral Laughter Count (LUL instances)', get_listener_lul_count(raw_text)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage: python parse.py input_dir'
    else:
        # print os.listdir(sys.argv[1])
        for fname in os.listdir(sys.argv[1]):
            print "-"*60
            # print os.path.join(sys.argv[1],fname)
            get_texts(os.path.join(sys.argv[1],fname))