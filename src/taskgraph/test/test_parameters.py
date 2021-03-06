# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import datetime
import unittest

from taskgraph.parameters import (
    Parameters,
    ParameterMismatch,
    load_parameters_file,
)

from .mockedopen import MockedOpen


class TestParameters(unittest.TestCase):

    vals = {
        "base_repository": "repository",
        "build_date": 0,
        "do_not_optimize": [],
        "existing_tasks": {},
        "filters": ["target_tasks_method"],
        "head_ref": "ref",
        "head_repository": "repository",
        "head_rev": "rev",
        "head_tag": "",
        "level": "3",
        "moz_build_date": "20191008095500",
        "optimize_target_tasks": True,
        "owner": "nobody@mozilla.com",
        "project": "project",
        "pushdate": 0,
        "pushlog_id": "0",
        "repository_type": "hg",
        "target_tasks_method": "default",
        "tasks_for": "github-push",
    }

    def test_Parameters_immutable(self):
        p = Parameters(**self.vals)

        def assign():
            p["owner"] = "nobody@example.test"

        self.assertRaises(Exception, assign)

    def test_Parameters_missing_KeyError(self):
        p = Parameters(**self.vals)
        self.assertRaises(KeyError, lambda: p["z"])

    def test_Parameters_invalid_KeyError(self):
        """even if the value is present, if it's not a valid property, raise KeyError"""
        p = Parameters(xyz=10, strict=True, **self.vals)
        self.assertRaises(ParameterMismatch, lambda: p.check())

    def test_Parameters_get(self):
        p = Parameters(owner="nobody@example.test", level=20)
        self.assertEqual(p["owner"], "nobody@example.test")

    def test_Parameters_check(self):
        p = Parameters(**self.vals)
        p.check()  # should not raise

    def test_Parameters_check_missing(self):
        p = Parameters()
        self.assertRaises(ParameterMismatch, lambda: p.check())

        p = Parameters(strict=False)
        p.check()  # should not raise

    def test_Parameters_check_extra(self):
        p = Parameters(xyz=10, **self.vals)
        self.assertRaises(ParameterMismatch, lambda: p.check())

        p = Parameters(strict=False, xyz=10, **self.vals)
        p.check()  # should not raise

    def test_Parameters_file_url_git_remote(self):
        vals = self.vals.copy()
        vals["repository_type"] = "git"

        vals["head_repository"] = "git@bitbucket.com:owner/repo.git"
        p = Parameters(**vals)
        self.assertRaises(ParameterMismatch, lambda: p.file_url(""))

        vals["head_repository"] = "git@github.com:owner/repo.git"
        p = Parameters(**vals)
        self.assertTrue(
            p.file_url("", pretty=True).startswith(
                "https://github.com/owner/repo/blob/"
            )
        )

        vals["head_repository"] = "https://github.com/mozilla-mobile/reference-browser"
        p = Parameters(**vals)
        self.assertTrue(
            p.file_url("", pretty=True).startswith(
                "https://github.com/mozilla-mobile/reference-browser/blob/"
            )
        )

        vals["head_repository"] = "https://github.com/mozilla-mobile/reference-browser/"
        p = Parameters(**vals)
        self.assertTrue(
            p.file_url("", pretty=True).startswith(
                "https://github.com/mozilla-mobile/reference-browser/blob/"
            )
        )

    def test_load_parameters_file_yaml(self):
        with MockedOpen({"params.yml": "some: data\n"}):
            self.assertEqual(load_parameters_file("params.yml"), {"some": "data"})

    def test_load_parameters_file_json(self):
        with MockedOpen({"params.json": '{"some": "data"}'}):
            self.assertEqual(load_parameters_file("params.json"), {"some": "data"})

    def test_load_parameters_override(self):
        """
        When ``load_parameters_file`` is passed overrides, they are included in
        the generated parameters.
        """
        self.assertEqual(
            load_parameters_file("", overrides={"some": "data"}), {"some": "data"}
        )

    def test_load_parameters_override_file(self):
        """
        When ``load_parameters_file`` is passed overrides, they overwrite data
        loaded from a file.
        """
        with MockedOpen({"params.json": '{"some": "data"}'}):
            self.assertEqual(
                load_parameters_file("params.json", overrides={"some": "other"}),
                {"some": "other"},
            )

    def test_moz_build_date_time(self):
        p = Parameters(**self.vals)
        self.assertEqual(p["moz_build_date"], "20191008095500")
        self.assertEqual(p.moz_build_date, datetime.datetime(2019, 10, 8, 9, 55, 0))
