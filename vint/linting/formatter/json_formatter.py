from typing import List, Dict, Any
import json
from pathlib import Path
from vint.linting.formatter.abstract_formatter import AbstractFormatter



class JSONFormatter(AbstractFormatter):
    def __init__(self): # type: () -> None
        super(JSONFormatter, self).__init__()
        pass


    def format_violations(self, violations): # type: (List[Dict[str, Any]]) -> str
        return json.dumps(_normalize_violations(violations))



def _normalize_violations(violations): # type: (List[Dict[str, Any]]) -> List[Dict[str, Any]]
    line_number = lambda violation: violation['position']['line']
    sorted_violations = sorted(violations, key=line_number)

    normalized_violations = map(_normalize_violation, sorted_violations)

    return list(normalized_violations)



def _normalize_violation(violation): # type: (Dict[str, Any]) -> Dict[str, Any]
    return {
        'file_path': str(Path(violation['position']['path'])),
        'line_number': violation['position']['line'],
        'column_number': violation['position']['column'],
        'severity': violation['level'].name.lower(),
        'description': violation['description'],
        'policy_name': violation['name'],
        'reference': violation['reference'],
    }
