from typing import Optional, Dict, Any
from vint.encodings.decoding_strategy.abstract_strategy import DecodingStrategy


class ComposedDecodingStrategy(DecodingStrategy):
    def __init__(self, strategies):
        # type: ([DecodingStrategy]) -> None
        self.strategies = strategies


    def decode(self, bytes_seq, debug_hint):
        # type: (bytes, Dict[str, Any]) -> Optional[str]

        debug_hint['composed_strategies'] = [type(strategy).__name__ for strategy in self.strategies]

        for strategy in self.strategies:
            string_candidate = strategy.decode(bytes_seq, debug_hint)

            if string_candidate is None:
                continue

            debug_hint['selected_strategy'] = type(strategy).__name__

            return string_candidate
