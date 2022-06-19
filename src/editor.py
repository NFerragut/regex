"""editor.py - Read input text, transform it, and write it back."""

from argparse import ArgumentParser
import configparser
import locale
import os
import re
import sys

from regex import Regex

__version__ = '0.1.0'
_PROGRAM = os.path.basename(sys.argv[0])


def main(args):
    """The main application."""
    try:
        editor = Editor(infile=args.input, outfile=args.output)
        editor.read_config(args.config)
        if args.definition:
            editor.add_definitions(args.definition)
        for section in args.section:
            editor.edit(section)
        sys.exit()
    except configparser.ParsingError as error:
        msg = [f'{_PROGRAM}: error: configuration file "{error.source}" contains parsing errors']
        indent = ' ' * (len(_PROGRAM) + 9)
        for err in error.errors:
            msg.append(f'{indent}[line {err[0] - 1}]: {err[1]}')
        sys.exit('\n'.join(msg))
    except (FileNotFoundError, EditorError) as error:
        sys.exit(f'{_PROGRAM}: error: {str(error)}')


def parse_arguments():
    """Set up a parser for a stand-alone command-line application."""
    parser = ArgumentParser(prog=_PROGRAM)
    configure_parser(parser)
    return parser.parse_args()


def configure_parser(parser: ArgumentParser):
    """Configure command-line options and help."""
    parser.description = """Read input text, transform it, and write it back."""
    parser.add_argument('--version',
                        action='version', version=f'{parser.prog} version {__version__}',
                        help='display version number and exit')
    parser.add_argument('config',
                        metavar='CONFIG', nargs='?',
                        help='application configuration file')
    parser.add_argument('-s', '--section',
                        default=['DEFAULT'], metavar='SECTION', nargs='+',
                        help='section(s) of configuration file to apply')
    parser.add_argument('-i', '--input',
                        metavar='INFILE',
                        help='file with input text for simple configuration')
    parser.add_argument('-d', '--definition',
                        default=[], metavar='NAME:VALUE', nargs='+',
                        help='replace NAME with VALUE in regular expression(s)')
    parser.add_argument('-o', '--output',
                        metavar='OUTFILE',
                        help='output text file to create/overwrite for simple configuration')
    # parser.epilog = """..."""
    parser.set_defaults(func=main)


class Editor():
    """Read input text, transform it, and write it back."""

    def __init__(self, *, infile=None, outfile=None):
        self._config = configparser.ConfigParser(empty_lines_in_values=False)
        self._section = ''
        self._stdin = None
        self._text = ''
        self.default_infile = infile
        self.default_outfile = outfile
        self.definitions = {}

    def read_config(self, configfile: str):
        """Read the configuration file and return the config dict."""
        if configfile is None:
            return
        configdata = f'[{self._config.default_section}]\n'
        encoding = locale.getpreferredencoding(do_setlocale=False)
        with open(configfile, encoding=encoding) as fin:
            configdata += fin.read()
        self._config.read_string(configdata, configfile)

    def add_definitions(self, definitions: list[str]):
        """Add name:value pairs used to modify the regular expressions."""
        for definition in definitions:
            if found := re.fullmatch(r'(.+):(.+)', definition):
                name = found[1]
                value = found[2]
                self.definitions[name] = value

    def edit(self, section=None):
        """Convert the text using regular expressions from the configuration section."""
        self._section = '' if section is None else section
        self._read_input()
        self._convert_text()
        self._write_output()

    def _read_input(self):
        """Read the input text."""
        filename = self._config.get(self._section, 'input', fallback=self.default_infile)
        if filename is None:
            self._read_stdin()
        else:
            self._read_file(filename)
        if not self._text:
            raise EditorError('no input text provided')

    def _read_file(self, filename):
        """Read input file text."""
        encoding = locale.getpreferredencoding(False)
        self._text = ''
        with open(filename, 'rt', encoding=encoding) as fin:
            self._text = fin.read()

    def _read_stdin(self):
        """Read STDIN text or use previously read STDIN text."""
        if self._stdin is None:
            if not sys.stdin.isatty():
                self._stdin = sys.stdin.read()
            else:
                self._stdin = ''
        self._text = self._stdin

    def _convert_text(self):
        """Convert the input text using the regular expressions for the selected section."""
        regexes = self._get_regexes()
        for regex in regexes:
            self._text = regex.apply(self._text)

    def _get_regexes(self) -> list[Regex]:
        regexes = []
        config_regex_text = self._config.get(self._section, 'regex', fallback='')
        config_regex_list = config_regex_text.split('\n')
        for expression in config_regex_list:
            for name, value in self.definitions.items():
                expression = expression.replace(name, value)
            regex = Regex(expression)
            if regex.is_valid:
                regexes.append(regex)
        return regexes

    def _get_text_destination(self, section: str) -> str:
        return self._config.get(section, 'output', fallback=self.default_outfile)

    def _write_output(self):
        """Write the text to the output destination."""
        filename = self._config.get(self._section, 'output', fallback=self.default_outfile)
        if filename is None:
            print(self._text)
        else:
            self._write_file(filename)

    def _write_file(self, filename):
        previous_file_content = None
        encoding = locale.getpreferredencoding(False)
        if os.path.isfile(filename):
            with open(filename, 'rt', encoding=encoding) as fin:
                previous_file_content = fin.read()
        if self._text != previous_file_content:
            with open(filename, 'wt', encoding=encoding) as fout:
                fout.write(self._text)


class EditorError(Exception):
    """Errors generated by this application."""


if __name__ == '__main__':
    main(parse_arguments())
