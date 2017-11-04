import chardet
from typing import Optional, Dict, Any
from vint.encodings.decoding_strategy.abstract import DecodingStrategy


class DecodingStrategyByChardet(DecodingStrategy):
    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, Any]) -> Optional[str]
        encoding_hint = chardet.detect(bytearray(bytes_seq))
        encoding = encoding_hint['encoding']

        debug_hint['chardet_encoding'] = encoding_hint['encoding']
        debug_hint['chardet_confidence'] = encoding_hint['confidence']

        try:
            return bytes_seq.decode(encoding)

        except Exception as e:
            debug_hint['chardet_error'] = str(e)
            return None
