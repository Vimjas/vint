from pathlib import Path
from ansicolor import Colors, colorize


DEFAULT_FORMAT = '{file_path}:{line_number}:{column_number}: {description} (see {reference})'

FORMAT_COLOR_MAP = {
    'file_path': Colors.Red,
    'file_name': Colors.Red,
    'line_number': Colors.White,
    'column_number': Colors.White,
    'severity': Colors.Red,
    'description': Colors.White,
    'policy_name': Colors.White,
    'reference': Colors.White,
}


class Formatter(object):
    def __init__(self, config_dict):
        if 'cmdargs' in config_dict:
            cmdargs = config_dict['cmdargs']
        else:
            cmdargs = {}

        if 'format' in cmdargs and cmdargs['format'] is not None:
            self._format = cmdargs['format']
        else:
            self._format = DEFAULT_FORMAT

        if 'color' in cmdargs and cmdargs['color'] is not None:
            self._should_be_colorized = cmdargs['color']
        else:
            self._should_be_colorized = False


    def _sort_violations(self, violations):
        return sorted(violations, key=lambda violation: (violation['position']['path'],
                                                         violation['position']['line']))


    def format_violations(self, violations):
        sorted_violations = self._sort_violations(violations)
        formatted_lines = map(self.format_violation, sorted_violations)

        return '\n'.join(formatted_lines)


    def format_violation(self, violation):
        if self._should_be_colorized:
            formatter_map = self._get_colorize_formatter_map(violation)
        else:
            formatter_map = self._get_formatter_map(violation)

        formatted_line = self._format.format(**formatter_map)
        return formatted_line


    def _get_colorize_formatter_map(self, violation):
        formatter_map = self._get_formatter_map(violation)
        colorized_formatter_map = {}

        for key, value in formatter_map.items():
            if key in FORMAT_COLOR_MAP:
                Color = FORMAT_COLOR_MAP[key]
                colorized_formatter_map[key] = colorize(str(value), Color())
            else:
                colorized_formatter_map[key] = value

        return colorized_formatter_map


    def _get_formatter_map(self, violation):
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
