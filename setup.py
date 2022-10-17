#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io, os, sys, numpy
from setuptools import setup, Extension, find_packages



with open(os.path.join(__location__, 'VERSION'), "w+") as f:
    f.writelines(Version)

setup()
