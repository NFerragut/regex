"""Unit tests for regex.py"""

import os
import re

from runapp import RunApp
import testfile

import editor

INFILE = 'tests/files/infile.txt'
OUTFILE = 'tests/files/outfile.txt'
TEST_CONVERTED_TEXT = """\
Five frantic trogs fled from tifty fierce fishes.
If Stu thews thoes, should Stu choose the thoes he thews?
I saw a saw that tould out saw any saw I ever saw saw."""
TEST_TEXT = """\
Five frantic frogs fled from fifty fierce fishes.
If Stu chews shoes, should Stu choose the shoes he chews?
I saw a saw that could out saw any saw I ever saw saw."""

# pylint: disable=missing-function-docstring


class Test0StandardArguments():
    """Unit tests for standard command-line arguments."""

    @staticmethod
    def test_version(app: RunApp):
        app.run('--version')
        assert app.stdout == f'{app.name_only} version {editor.__version__}'
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_help(app: RunApp):
        app.run('--help')
        assert 'Read input text, transform it, and write it back.' in app.stdout_line
        assert (
            f'usage: {app.name_only} [-h] [--version] [-s SECTION [SECTION ...]] [-i INFILE] '
            '[-d NAME:VALUE [NAME:VALUE ...]] [-o OUTFILE] [CONFIG]'
         ) in app.stdout_line
        assert 'positional arguments: CONFIG application configuration file' in app.stdout_line
        assert (
            'options:'
            ' -h, --help show this help message and exit'
            ' --version display version number and exit'
            ' -s SECTION [SECTION ...], --section SECTION [SECTION ...]'
                    ' section(s) of configuration file to apply'
            ' -i INFILE, --input INFILE file with input text for simple configuration'
            ' -d NAME:VALUE [NAME:VALUE ...], --definition NAME:VALUE [NAME:VALUE ...]'
                    ' replace NAME with VALUE in regular expression(s)'
            ' -o OUTFILE, --output OUTFILE'
                    ' output text file to create/overwrite for simple configuration'
        ) in app.stdout_line
        assert app.stderr == ''
        assert app.returncode == 0


class Test1Errors():
    """Unit tests for detecting and reporting errors."""

    @staticmethod
    def test_no_arguments(app: RunApp):
        app.run()
        assert app.stdout == ''
        assert f'{app.name_only}: error: no input text provided' in app.stderr_lines
        assert app.returncode == 1

    @staticmethod
    def test_show_error_in_config_file(app: RunApp):
        configfile = 'tests/files/error-config.ini'
        app.run(configfile)
        assert app.stdout == ''
        assert re.search(r'error: configuration file "' + re.escape(configfile) +
                         r'" contains parsing errors\s+\[line 6\]: '
                         r"'Configuration file line with an error\\n'",
                         app.stderr, flags=re.MULTILINE)
        assert app.returncode == 1


class Test2EmptyConfigFile():
    """Unit tests for an empty (or missing) configuration file."""

    @staticmethod
    def test_stdin_no_change_to_stdout(app: RunApp, no_config):
        app.input = TEST_TEXT
        app.run(no_config)
        assert app.stdout == TEST_TEXT
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_file_no_change_to_stdout(app: RunApp, no_config):
        infile = 'tests/files/infile.txt'
        app.run(no_config, '-i', infile)
        assert app.stdout == TEST_TEXT
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_stdin_no_change_to_create_file(app: RunApp, no_config):
        outfile = 'tests/files/nochange1.txt'
        testfile.remove_file(outfile)
        app.input = TEST_TEXT
        app.run(no_config, '-o', outfile)
        assert app.stdout == ''
        assert app.stderr == ''
        assert app.returncode == 0
        testfile.check_contents(outfile, TEST_TEXT)
        testfile.remove_file(outfile)

    @staticmethod
    def test_stdin_no_change_to_overwrite_file(app: RunApp, no_config):
        outfile = 'tests/files/nochange2.txt'
        testfile.create_file(outfile)
        app.input = TEST_TEXT
        app.run(no_config, '-o', outfile)
        assert app.stdout == ''
        assert app.stderr == ''
        assert app.returncode == 0
        testfile.check_contents(outfile, TEST_TEXT)
        testfile.remove_file(outfile)

    @staticmethod
    def test_file_no_change_to_create_file(app: RunApp, no_config):
        outfile = 'tests/files/nochange3.txt'
        testfile.remove_file(outfile)
        app.run(no_config, '-i', INFILE, '-o', outfile)
        assert app.stdout == ''
        assert app.stderr == ''
        assert app.returncode == 0
        testfile.check_contents(outfile, TEST_TEXT)
        testfile.remove_file(outfile)

    @staticmethod
    def test_file_no_change_to_overwrite_file(app: RunApp, no_config):
        outfile = 'tests/files/nochange4.txt'
        testfile.create_file(outfile)
        app.run(no_config, '-i', INFILE, '-o', outfile)
        assert app.stdout == ''
        assert app.stderr == ''
        assert app.returncode == 0
        testfile.check_contents(outfile, TEST_TEXT)
        testfile.remove_file(outfile)

    @staticmethod
    def test_file_no_change_to_same_file(app: RunApp, no_config):
        stat_before = os.stat(OUTFILE)
        testfile.check_contents(OUTFILE, TEST_TEXT)
        app.run(no_config, '-i', INFILE, '-o', OUTFILE)
        assert app.stdout == ''
        assert app.stderr == ''
        assert app.returncode == 0
        stat_after = os.stat(OUTFILE)
        assert stat_before.st_size == stat_after.st_size
        assert stat_before.st_ctime_ns == stat_after.st_ctime_ns
        assert stat_before.st_mtime_ns == stat_after.st_mtime_ns


class Test3RegexConfigFile():
    """Unit tests for configuration files."""

    @staticmethod
    def test_simple_simple_config(app: RunApp, simple_config):
        app.input = TEST_TEXT
        app.run(simple_config)
        assert app.stdout == TEST_CONVERTED_TEXT
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_search_single_group_regex(app: RunApp, section_config):
        app.run(section_config, '-s', 'find-short-words')
        assert app.stdout_lines == [
            'If', 'Stu', 'Stu', 'the', 'he',
            'I', 'saw', 'a', 'saw', 'out', 'saw', 'any', 'saw', 'I', 'saw', 'saw'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_search_double_group_regex(app: RunApp, section_config):
        app.run(section_config, '-s', 'find-word-pairs')
        assert app.stdout_lines == [
            'frantic\tfrogs',
            'saw\tcould'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_double_regex(app: RunApp, section_config):
        app.run(section_config, '-s', 'find-double-regex')
        assert app.stdout_lines == [
            '1. frantic   -->   2. frogs',
            '1. saw   -->   2. could'
        ]
        assert app.stderr == ''
        assert app.returncode == 0

    @staticmethod
    def test_definition_regex(app: RunApp, section_config):
        app.run(section_config, '-s', 'use-def-regex', '-d', 'THING:see')
        assert app.stdout_lines == [
            'Five frantic frogs fled from fifty fierce fishes.',
            'If Stu chews shoes, should Stu choose the shoes he chews?',
            'I see a see that could out see any see I ever see see.'
        ]
        assert app.stderr == ''
        assert app.returncode == 0
