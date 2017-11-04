from typing import Optional, Dict


class DecodingStrategy(object):
    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, str]) -> Optional[str]
        raise NotImplementedError
