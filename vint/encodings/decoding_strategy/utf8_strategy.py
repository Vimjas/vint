from typing import Optional, Dict, Any
from vint.encodings.decoding_strategy.abstract_strategy import DecodingStrategy


class DecodingStrategyForUTF8(DecodingStrategy):
    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, Any]) -> Optional[str]
        try:
            string = bytes_seq.decode('utf8')

            debug_hint['utf-8'] = 'success'
            return string

        except Exception as e:
            debug_hint['utf-8'] = 'failed: {}'.format(str(e))

            return None
