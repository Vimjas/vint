import sys
from typing import Dict, Any
from pprint import pformat
from pathlib import Path
from vint.encodings.decoding_strategy import DecodingStrategy


SCRIPTENCODING_PREFIX = bytearray('scriptencoding', encoding='ascii')



class Decoder(object):
    def __init__(self, strategy):
        # type: (DecodingStrategy) -> None
        self.strategy = strategy
        self.debug_hint = dict(version=sys.version)


    def read(self, file_path):
        # type: (Path) -> str

        with file_path.open(mode='rb') as f:
            bytes_seq = f.read()
            strings = []

            for (loc, hunk) in _split_by_scriptencoding(bytes_seq):
                debug_hint_for_the_loc = dict()
                self.debug_hint[loc] = debug_hint_for_the_loc

                string = self.strategy.decode(hunk, debug_hint=debug_hint_for_the_loc)

                if string is None:
                    raise EncodingDetectionError(self.debug_hint)

                strings.append(string)

            return ''.join(strings)


def _split_by_scriptencoding(bytes_seq):
    # type: (bytes) -> [(str, bytes)]
    max_end_index = len(bytes_seq)
    start_index = 0
    bytes_seq_and_loc_list = []

    while True:
        end_index = bytes_seq.find(SCRIPTENCODING_PREFIX, start_index + 1)

        if end_index < 0:
            end_index = max_end_index

        bytes_seq_and_loc_list.append((
            "{start_index}:{end_index}".format(start_index=start_index, end_index=end_index),
            bytes_seq[start_index:end_index]
        ))

        if end_index < max_end_index:
            start_index = end_index
            continue

        return bytes_seq_and_loc_list


class EncodingDetectionError(Exception):
    def __init__(self, debug_hint):
        # type: (Dict[str, Any]) -> None
        self.debug_hint = debug_hint


    def __str__(self):
        # type: () -> str
        return 'Cannot detect encoding (binary file?): {debug_hint}'.format(
            debug_hint=pformat(self.debug_hint)
        )
