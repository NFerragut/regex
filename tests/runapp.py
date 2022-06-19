"""RunApp class helps test command-line applications."""

import locale
import os
import re
import subprocess

TEST_ROOT = os.path.abspath(os.curdir)


class RunApp:
    """Run applications and return results."""

    def __init__(self, name='', command=''):
        self.name_only = name
        self.command = command
        self.result = None
        self.source_folder = ''
        self.input = None

    @property
    def filename(self) -> str:
        """Get the path and filename of the application script being tested."""
        filename = os.path.join(self.source_folder, self.name_only)
        return filename

    @property
    def name(self) -> str:
        """Get the name of the application with the optional command appended."""
        if self.command:
            return f'{self.name_only} {self.command}'
        return self.name_only

    @property
    def returncode(self) -> int:
        """Get the return code after running the application."""
        return self.result.returncode

    @property
    def stderr(self) -> str:
        """Get the STDERR text."""
        return str(self.result.stderr).rstrip()

    @property
    def stderr_line(self) -> str:
        """Get the STDERR text as a single line."""
        return re.sub(r'\s+', ' ', self.stderr.lstrip())

    @property
    def stderr_lines(self) -> str:
        """Get the STDERR text as a list of lines."""
        return self.stderr.splitlines()

    @property
    def stdout(self) -> str:
        """Get the STDOUT text."""
        return str(self.result.stdout).rstrip()

    @property
    def stdout_line(self) -> str:
        """Get the STDOUT text as a single line."""
        return re.sub(r'\s+', ' ', self.stdout.strip())

    @property
    def stdout_lines(self) -> str:
        """Get the STDOUT text as a list of lines."""
        return self.stdout.splitlines()

    def run(self, *args):
        """Run an application and capture the output."""
        cmd = ['python', self.filename, *[arg for arg in args if arg]]
        if self.command:
            cmd.insert(2, self.command)
        self.result = subprocess.run(cmd, cwd=TEST_ROOT,
                                     input=self.input, encoding=locale.getpreferredencoding(False),
                                     capture_output=True, check=False, timeout=5000)
