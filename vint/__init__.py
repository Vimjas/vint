from vint.bootstrap import (
    init_logger,
    init_linter,
    init_cli,
)


def main():
    init_logger()
    init_linter()
    init_cli()


if __name__ == '__main__':
    main()
