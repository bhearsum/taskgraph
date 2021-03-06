from setuptools import setup, find_packages

with open("requirements/base.in", "r") as fp:
    requirements = fp.read().splitlines()

setup(
    name="taskgraph",
    version="0.0.1",
    description="Build taskcluster taskgraphs",
    url="https://hg.mozilla.org/ci/taskgraph",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=requirements,
    classifiers=(
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3.6",
    ),
    entry_points={"console_scripts": ["taskgraph = taskgraph.main:main"]},
    package_data={
        "taskgraph": [
            "run-task/run-task",
            "run-task/fetch-content",
            "run-task/hgrc",
            "run-task/robustcheckout.py",
        ],
        "taskgraph.test": ["automationrelevance.json"],
    },
)
