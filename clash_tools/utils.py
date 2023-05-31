import logging
import re

import pyaes


def gen_aes(input_key):
    logging.info("Generating AES key", input_key)
    if len(input_key) > 32:
        key_ = input_key[:32]
    elif len(input_key) < 32:
        key_ = input_key + '=' * (32 - len(input_key))
    else:
        key_ = input_key
    key_ = key_.encode('utf-8')
    aes_ = pyaes.AESModeOfOperationCTR(key_)
    return aes_

def match_pattern(pattern, text):
    if pattern in text:
        return True
    if re.match(pattern, text):
        return True
    return False

def match_pattern_list(pattern_list, text):
    for pattern in pattern_list:
        if match_pattern(pattern, text):
            return True
    return False