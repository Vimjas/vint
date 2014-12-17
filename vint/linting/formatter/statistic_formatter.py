from vint.linting.formatter.formatter import Formatter


class StatisticFormatter(Formatter):
    def format_violations(self, violations):
        violations_count = len(violations)

        output = super(StatisticFormatter, self).format_violations(violations) + '\n'
        return output + 'Total violations: {count}'.format(count=violations_count)
