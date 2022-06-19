"""Shared Test Fixtures"""

import pytest

from runapp import RunApp

SOURCE_FOLDER = 'src'


@pytest.fixture
def app() -> RunApp:
    """Class to run the application on the command line."""
    runapp = RunApp('editor.py')
    runapp.source_folder = SOURCE_FOLDER
    return runapp

@pytest.fixture(params=['tests/files/empty-config.ini', ''])
def no_config(request) -> str:
    """Parameter for either an empty configuration file or no configuration file."""
    return request.param

@pytest.fixture
def section_config() -> str:
    """Parameter for a config file with multiple sections."""
    return 'tests/files/section-config.ini'

@pytest.fixture
def simple_config() -> str:
    """Parameter for a simple config file with just a regex field."""
    return 'tests/files/simple-config.ini'
