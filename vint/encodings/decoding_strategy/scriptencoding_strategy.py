from typing import Optional, Dict, Any
from vint.encodings.decoding_strategy.abstract_strategy import DecodingStrategy


SCRIPTENCODING_PREFIX = bytearray('scriptencoding', encoding='ascii')
COMMENT_START_TOKEN = bytearray('"', encoding='ascii')
LF = bytearray("\n", encoding='ascii')


class DecodingStrategyByScriptencoding(DecodingStrategy):
    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, Any]) -> Optional[str]
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
        # type: (bytes, Dict[str, Any]) -> Optional[bytes]
        try:
            start_index = bytes_seq.index(SCRIPTENCODING_PREFIX)
            encoding_part_start_index = start_index + len(SCRIPTENCODING_PREFIX)

            try:
                encoding_part_end_index_candidate_by_line_break = bytes_seq.index(LF, encoding_part_start_index)

                try:
                    encoding_part_end_index_candidate_by_comment = bytes_seq.index(
                        COMMENT_START_TOKEN, encoding_part_start_index)

                    # Case for :scriptencoding foo "foo\n
                    encoding_part_end_index = min(
                        encoding_part_end_index_candidate_by_line_break,
                        encoding_part_end_index_candidate_by_comment
                    )

                except ValueError:
                    # Case for :scriptencoding foo\n
                    encoding_part_end_index = encoding_part_end_index_candidate_by_line_break

            except ValueError:
                try:
                    # Case for :scriptencoding foo "foo<EOF>
                    encoding_part_end_index_candidate_by_comment = bytes_seq.index(
                        COMMENT_START_TOKEN, encoding_part_start_index)
                    encoding_part_end_index = encoding_part_end_index_candidate_by_comment

                except ValueError:
                    encoding_part_end_index = len(bytes_seq) - 1
                    # Case for :scriptencoding foo<EOF>

            encoding_part_candidate = bytes_seq[encoding_part_start_index:encoding_part_end_index]
            return encoding_part_candidate.strip()

        except ValueError:
            debug_hint['scriptencoding_error'] = '`scriptencoding` is not found'
            return None
