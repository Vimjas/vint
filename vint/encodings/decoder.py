import chardet
import sys
from typing import Optional, Dict
from pprint import pformat
from pathlib import Path


SCRIPTENCODING_PREFIX = bytearray('scriptencoding', encoding='ascii')
COMMENT_START_TOKEN = bytearray('"', encoding='ascii')
LF = bytearray("\n", encoding='ascii')



class Decoder(object):
    def __init__(self, strategy):
        # type: (DecodingStrategy) -> None
        self.strategy = strategy
        self.debug_hint = dict(version=sys.version)


    def read(self, file_path):
        # type: (Path) -> str

        with file_path.open(mode='rb') as f:
            bytes_seq = f.read()
            string = self.strategy.decode(bytes_seq, debug_hint=self.debug_hint)

            if string is None:
                raise EncodingDetectionError(self.debug_hint)

            return string


    @classmethod
    def default_strategy(cls):
        # type: () -> DecodingStrategy
        return ComposedDecodingStrategy([
            DecodingStrategyForEmpty(),
            DecodingStrategyByScriptencoding(),
            DecodingStrategyByChardet(),
            DecodingStrategyForUTF8(),
        ])



class DecodingStrategy(object):
    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, str]) -> Optional[str]
        raise NotImplementedError


class ComposedDecodingStrategy(DecodingStrategy):
    def __init__(self, strategies):
        # type: ([DecodingStrategy]) -> None
        self.strategies = strategies


    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, str]) -> Optional[str]

        debug_hint['composed_strategies'] = [type(strategy).__name__ for strategy in self.strategies]

        for strategy in self.strategies:
            string_candidate = strategy.decode(bytes_seq, debug_hint)

            if string_candidate is None:
                continue

            debug_hint['selected_strategy'] = type(strategy).__name__

            return string_candidate


class DecodingStrategyForEmpty(DecodingStrategy):
    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, str]) -> Optional[str]
        if len(bytes_seq) <= 0:
            debug_hint['empty'] = 'true'
            return ''

        debug_hint['empty'] = 'false'
        return None


class DecodingStrategyForUTF8(DecodingStrategy):
    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, str]) -> Optional[str]
        try:
            string = bytes_seq.decode('utf8')

            debug_hint['utf-8'] = 'success'
            return string

        except RuntimeError as e:
            debug_hint['utf-8'] = 'failed: {}'.format(str(e))

            return None


class DecodingStrategyByChardet(DecodingStrategy):
    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, str]) -> Optional[str]
        encoding_hint = chardet.detect(bytearray(bytes_seq))
        encoding = encoding_hint['encoding']

        debug_hint['chardet_encoding'] = encoding_hint['encoding']
        debug_hint['chardet_confidence'] = encoding_hint['confidence']

        try:
            return bytes_seq.decode(encoding)

        except Exception as e:
            debug_hint['chardet_error'] = str(e)
            return None


class DecodingStrategyByScriptencoding(DecodingStrategy):
    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, str]) -> Optional[str]
        encoding_part = DecodingStrategyByScriptencoding.parse_script_encoding(bytes_seq, debug_hint)

        if encoding_part is None:
            debug_hint['scriptencoding'] = 'None'
            return None

        try:
            debug_hint['scriptencoding'] = encoding_part
            return bytes_seq.decode(encoding=encoding_part.decode(encoding='ascii'))

        except LookupError as e:
            debug_hint['scriptencoding_error'] = str(e)
            return None


    @classmethod
    def parse_script_encoding(cls, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, str]) -> Optional[bytes]
        try:
            start_index = bytes_seq.index(SCRIPTENCODING_PREFIX)
            encoding_part_start_index = start_index + len(SCRIPTENCODING_PREFIX)

            try:
                encoding_part_end_index_candidate_by_line_break = bytes_seq.index(LF, encoding_part_start_index)

                try:
                    encoding_part_end_index_candidate_by_comment = bytes_seq.index(
                        COMMENT_START_TOKEN, encoding_part_start_index)

                    # Case for :scriptencoding foo "foo
                    encoding_part_end_index = min(
                        encoding_part_end_index_candidate_by_line_break,
                        encoding_part_end_index_candidate_by_comment
                    )

                except ValueError:
                    # Case for :scriptencoding foo
                    encoding_part_end_index = encoding_part_end_index_candidate_by_line_break

            except ValueError:
                debug_hint['scriptencoding_error'] = '`scriptencoding` is found, but end token is not found'
                return None

            encoding_part_candidate = bytes_seq[encoding_part_start_index:encoding_part_end_index]
            return encoding_part_candidate.strip()

        except ValueError:
            debug_hint['scriptencoding_error'] = '`scriptencoding` is not found'
            return None




class EncodingDetectionError(Exception):
    def __init__(self, debug_hint):
        # type: (Dict[str, str]) -> None
        self.debug_hint = debug_hint


    def __str__(self):
        # type: () -> str
        return 'Cannot detect encoding (binary file?): {debug_hint}'.format(
            debug_hint=pformat(self.debug_hint)
        )
