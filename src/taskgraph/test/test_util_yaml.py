# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import unittest

from taskgraph.util import yaml

from .mockedopen import MockedOpen

FOO_YML = """\
prop:
    - val1
"""


class TestYaml(unittest.TestCase):
    def test_load(self):
        with MockedOpen({"/dir1/dir2/foo.yml": FOO_YML}):
            self.assertEqual(
                yaml.load_yaml("/dir1/dir2", "foo.yml"), {"prop": ["val1"]}
            )
