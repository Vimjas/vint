from argparse import ArgumentParser


def build_environment(argv):
    env = {}
    parser = ArgumentParser(description='Lint Vim script')

    parser.add_argument('path', nargs='?',
                        help='file or directory path to lint')
    parser.add_argument('-v', '--verbose',
                        action='store_true', help='output verbose message')
    parser.add_argument('-e', '--error',
                        action='store_true', help='report only errors')
    parser.add_argument('-w', '--warning',
                        action='store_true', help='report errors and warnings')
    parser.add_argument('-s', '--style-problem',
                        action='store_true', help='report errors, warnings and style problems')
    parser.add_argument('-m', '--max-violations',
                        type=int, help='limit max violations count')
    parser.parse_args(argv)

    env['cmdargs'] = vars(parser)

    return env
