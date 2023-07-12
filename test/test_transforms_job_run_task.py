"""
Tests for the 'toolchain' transforms.
"""
import os.path
from pprint import pprint

import pytest

from taskgraph.transforms.base import TransformConfig
from taskgraph.transforms.job import make_task_description
from taskgraph.util.templates import merge

from .conftest import FakeParameters

here = os.path.abspath(os.path.dirname(__file__))

TASK_DEFAULTS = {
    "description": "fake description",
    "label": "fake-task-label",
    "worker-type": "t-linux",
    "worker": {
        "implementation": "docker-worker",
        "os": "linux",
        "env": {},
    },
    "run": {
        "using": "run-task",
        # TODO: add some more variables to test precedence
        # direct only
        # file only
        # param only
        # direct + file
        # direct + param
        # file + param
        # direct + file + param
        # param fallback
        "command": "echo hello {direct} {file} {param} {direct_and_file} "
                   "{direct_and_param} {file_and_param} {direct_file_and_param} "
                   "{param_fallback}",
        "command-context": {
            "direct": "direct",
            "direct_and_file": "direct-overrides-file",
            "direct_and_param": "direct-overrides-param",
            "direct_file_and_param": "direct-overrides-all",
            "from-file": f"{here}/data/command_context.yaml",
            "from-parameters": {
                "param": "param",
                "direct_and_param": "direct_and_param",
                "file_and_param": "file_and_param",
                "direct_file_and_param": "direct_file_and_param",
                "param_fallback": ["missing-param", "default"],
            },
        },
    },
}


@pytest.fixture
def run_job_using(mocker, run_transform, graph_config):
    m = mocker.patch("taskgraph.util.hash._get_all_files")
    m.return_value = [
        "taskcluster/scripts/toolchain/run.sh",
        "taskcluster/scripts/toolchain/run.ps1",
    ]

    params = FakeParameters(
        {
            "param": "param",
            "direct_and_param": "ignored",
            "file_and_param": "param-overrides-file",
            "direct_file_and_param": "ignored",
            "default": "default",
            "base_repository": "http://hg.example.com",
            "build_date": 0,
            "build_number": 1,
            "enable_always_target": True,
            "head_repository": "http://hg.example.com",
            "head_rev": "abcdef",
            "head_ref": "default",
            "level": "1",
            "moz_build_date": 0,
            "next_version": "1.0.1",
            "owner": "some-owner",
            "project": "some-project",
            "pushlog_id": 1,
            "repository_type": "hg",
            "target_tasks_method": "test_method",
            "tasks_for": "hg-push",
            "try_mode": None,
            "version": "1.0.0",
        },
    )
    transform_config = TransformConfig(
        "test",
        str(here),
        {},
        params,
        {},
        graph_config,
        write_artifacts=False
    )
    def inner(task):
        task = merge(TASK_DEFAULTS, task)
        return run_transform(make_task_description, task, config=transform_config)[0]

    return inner


def assert_docker_worker(task):
    assert task == {
        "attributes": {},
        "dependencies": {},
        "description": "fake description",
        "extra": {},
        "label": "fake-task-label",
        "routes": [],
        "scopes": [],
        "soft-dependencies": [],
        "worker": {
            "caches": [
                {
                    "mount-point": "/builds/worker/checkouts",
                    "name": "checkouts-hg58",
                    "skip-untrusted": False,
                    "type": "persistent",
                }
            ],
            "command": [
                "/usr/local/bin/run-task",
                "--ci-checkout=/builds/worker/checkouts/vcs/",
                "--",
                "bash",
                "-cx",
                "echo hello direct file param direct-overrides-file "
                "direct-overrides-param param-overrides-file "
                "direct-overrides-all default",
            ],
            "env": {
                "CI_BASE_REPOSITORY": "http://hg.example.com",
                "CI_HEAD_REF": "default",
                "CI_HEAD_REPOSITORY": "http://hg.example.com",
                "CI_HEAD_REV": "abcdef",
                "CI_REPOSITORY_TYPE": "hg",
                "HG_STORE_PATH": "/builds/worker/checkouts/hg-store",
                "MOZ_SCM_LEVEL": "1",
                "REPOSITORIES": '{"ci": "Taskgraph"}',
                "VCS_PATH": "/builds/worker/checkouts/vcs",
            },
            "implementation": "docker-worker",
            "os": "linux",
            "taskcluster-proxy": True,
        },
        "worker-type": "t-linux",
    }


def assert_generic_worker(task):
    assert task == {
        "attributes": {},
        "dependencies": {},
        "description": "fake description",
        "extra": {},
        "label": "fake-task-label",
        "routes": [],
        "scopes": [],
        "soft-dependencies": [],
        "worker": {
            "command": [
                "C:/mozilla-build/python3/python3.exe run-task "
                '--ci-checkout=./build/src/ -- bash -cx "echo hello '
                'direct file param direct-overrides-file '
                'direct-overrides-param param-overrides-file '
                'direct-overrides-all default"',
            ],
            "env": {
                "CI_BASE_REPOSITORY": "http://hg.example.com",
                "CI_HEAD_REF": "default",
                "CI_HEAD_REPOSITORY": "http://hg.example.com",
                "CI_HEAD_REV": "abcdef",
                "CI_REPOSITORY_TYPE": "hg",
                "HG_STORE_PATH": "y:/hg-shared",
                "MOZ_SCM_LEVEL": "1",
                "REPOSITORIES": '{"ci": "Taskgraph"}',
                "VCS_PATH": "./build/src",
            },
            "implementation": "generic-worker",
            "mounts": [
                {"cache-name": "checkouts", "directory": "./build"},
                {
                    "content": {
                        "url": "https://tc-tests.localhost/api/queue/v1/task/<TASK_ID>/artifacts/public/run-task"  # noqa
                    },
                    "file": "./run-task",
                },
            ],
            "os": "windows",
        },
        "worker-type": "b-win2012",
    }


def assert_exec_with(task):
    assert task["worker"]["command"] == [
        "/usr/local/bin/run-task",
        "--ci-checkout=/builds/worker/checkouts/vcs/",
        "--",
        "powershell.exe",
        "-ExecutionPolicy",
        "Bypass",
        "echo hello direct file param direct-overrides-file "
        "direct-overrides-param param-overrides-file "
        "direct-overrides-all default",
    ]


def assert_run_task_command_docker_worker(task):
    assert task["worker"]["command"] == [
        "/foo/bar/python3",
        "run-task",
        "--ci-checkout=/builds/worker/checkouts/vcs/",
        "--",
        "bash",
        "-cx",
        "echo hello direct file param direct-overrides-file "
        "direct-overrides-param param-overrides-file "
        "direct-overrides-all default",
    ]


def assert_run_task_command_generic_worker(task):
    assert task["worker"]["command"] == [
        ["chmod", "+x", "run-task"],
        [
            "/foo/bar/python3",
            "run-task",
            "--ci-checkout=./checkouts/vcs/",
            "--",
            "bash",
            "-cx",
            "echo hello direct file param direct-overrides-file "
            "direct-overrides-param param-overrides-file "
            "direct-overrides-all default",
        ],
    ]


@pytest.mark.parametrize(
    "task",
    (
        pytest.param(
            {},
            id="docker_worker",
        ),
        pytest.param(
            {
                "worker-type": "b-win2012",
                "worker": {
                    "os": "windows",
                    "implementation": "generic-worker",
                },
            },
            id="generic_worker",
        ),
        pytest.param(
            {
                "run": {
                    "exec-with": "powershell",
                },
            },
            id="exec_with",
        ),
        pytest.param(
            {
                "run": {"run-task-command": ["/foo/bar/python3", "run-task"]},
            },
            id="run_task_command_docker_worker",
        ),
        pytest.param(
            {
                "run": {"run-task-command": ["/foo/bar/python3", "run-task"]},
                "worker": {
                    "implementation": "generic-worker",
                },
            },
            id="run_task_command_generic_worker",
        ),
    ),
)
def test_run_task(request, run_job_using, task):
    taskdesc = run_job_using(task)
    print("Task Description:")
    pprint(taskdesc)
    param_id = request.node.callspec.id
    assert_func = globals()[f"assert_{param_id}"]
    assert_func(taskdesc)
