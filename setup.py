#!/usr/bin/env python3
#
# Copyright 2017 Zegami Ltd

"""Install script for Zegami Zeg Collection Creator."""

import os

import setuptools


def readme():
    """Get Readme."""
    with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
        return f.read()


setuptools.setup(
    name="Zegami Zeg Collection Create",
    version="0.1",
    description="Create Zegami collections with Zegs",
    long_description=readme(),
    url="https://www.zegami.com",
    author="Roger Noble, Anthony Kveder, Martin Packman",
    author_email="roger@zegami.com, "
        "anthony.kveder@zegami.com, martin@zegami.com",
    packages=["zegami_zeg"],
    scripts=["upload.py"],
    install_requires=[
        "PyYAML >= 3.12",
        "requests >= 2",
    ],
)
