import json
from pathlib import Path



class JSONFormatter(object):
    def __init__(self, env):
        pass


    def format_violations(self, violations):
        return json.dumps(self._normalize_violations(violations))


    def _normalize_violations(self, violations):
        line_number = lambda violation: violation['position']['line']
        sorted_violations = sorted(violations, key=line_number)

        normalized_violations = map(self._normalize_violation, sorted_violations)

        return list(normalized_violations)


    def _normalize_violation(self, violation):
        return {
            'file_path': str(Path(violation['position']['path'])),
            'line_number': violation['position']['line'],
            'column_number': violation['position']['column'],
            'severity': violation['level'].name.lower(),
            'description': violation['description'],
            'policy_name': violation['name'],
            'reference': violation['reference'],
        }
