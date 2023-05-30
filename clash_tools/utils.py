import logging

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