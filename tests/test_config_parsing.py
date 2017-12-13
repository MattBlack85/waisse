# coding: utf-8 -*-
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from waisse.client import APIClient
from waisse.exceptions import InvalidConfig

HERE = Path('./')


class ConfigParsingTestCase(unittest.TestCase):
    """
    Test that the config is parsed as expected
    """

    def tearDown(self):
        # Linux only
        _, _, os_user, *_ = os.getcwd().split('/')
        storage = f'/home/{os_user}/.waisse'
        if os.path.exists(storage):
            shutil.rmtree(storage)

    def test_conf_parsed_correctly_from_path(self):
        APIClient(config='example_config.json')

    def test_invalid_config_raises_error(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(b'This is not\a JSON file.\n')
            with self.assertRaises(InvalidConfig):
                APIClient(config=f.name)
