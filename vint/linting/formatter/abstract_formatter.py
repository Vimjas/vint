from typing import List, Dict, Any  # noqa: F401


class AbstractFormatter(object):
    def format_violations(self, violations):  # type: (List[Dict[str, Any]]) -> str
        raise NotImplementedError