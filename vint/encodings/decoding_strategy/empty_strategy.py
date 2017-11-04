from typing import Optional, Dict, Any
from vint.encodings.decoding_strategy.abstract_strategy import DecodingStrategy


class DecodingStrategyForEmpty(DecodingStrategy):
    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, Any]) -> Optional[str]
        if len(bytes_seq) <= 0:
            debug_hint['empty'] = 'true'
            return ''

        debug_hint['empty'] = 'false'
        return None
