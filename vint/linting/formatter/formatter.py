from pathlib import Path
from ansicolor import Colors, colorize


DEFAULT_FORMAT = '{file_path}|{line_number} col {column_number} {severity}| {description} [{policy_name}|{reference}]'

FORMAT_COLOR_MAP = {
    'file_path': Colors.Cyan,
    'line_number': Colors.White,
    'column_number': Colors.White,
    'severity': Colors.Red,
    'description': Colors.White,
    'policy_name': Colors.White,
    'reference': Colors.White,
}


class Formatter(object):
    def __init__(self, env):
        if 'cmd_args' not in env:
            return

        cmd_args = env['cmd_args']

        self._format = cmd_args['format'] if 'format' in cmd_args else DEFAULT_FORMAT
        self._should_be_colorized = 'color' in cmd_args and cmd_args['color']


    def format_violations(self, violations):
        line_number = lambda violation: violation['position']['line']
        sorted_violations = sorted(violations, key=line_number)

        formatted_lines = map(lambda violation: self.format_violation(violation),
                              sorted_violations)

        return '\n'.join(formatted_lines) + '\n'


    def format_violation(self, violation):
        formatter_map = self._assign_violation_attribute(violation)

        if self._should_be_colorized:
            for key, value in formatter_map:
                formatter_map[key] = colorize(value, FORMAT_COLOR_MAP[key])

        formatted_line = self._format.format(**formatter_map)
        return formatted_line


    def _assign_violation_attribute(self, violation):
        file_path = Path(violation['position']['path'])

        return {
            'file_path': file_path,
            'file_name': file_path.name,
            'line_number': violation['position']['line'],
            'column_number': violation['position']['column'],
            'severity': violation['level'].name.lower(),
            'description': violation['description'],
            'policy_name': violation['name'],
            'reference': violation['reference'],
        }
