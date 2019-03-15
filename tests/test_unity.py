""" test_unity.py """
from subprocess import check_output

import pytest

from unity import unity


class TestUnityCompile():
    def test_no_stan_model(self):
        """Model compile fails if file does not exist."""
        with pytest.raises(FileNotFoundError, match=r'alksufwl'):
            unity.compile('alksufwl')


# TODO: move to its own file.
class TestCLI():
    def test_installed(self):
        """Is the UNITY help menu accessible?"""
        check_output('unity --help', shell=True)