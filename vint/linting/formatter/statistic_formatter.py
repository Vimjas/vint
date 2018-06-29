from typing import List, Dict, Any
from vint.linting.formatter.formatter import Formatter


class StatisticFormatter(Formatter):
    def format_violations(self, violations): # type: (List[Dict[str, Any]]) -> str
        violations_count = len(violations)

        output = super(StatisticFormatter, self).format_violations(violations) + '\n'
        return output + 'Total violations: {count}'.format(count=violations_count)
