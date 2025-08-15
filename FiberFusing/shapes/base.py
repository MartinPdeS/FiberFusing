#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydantic import ConfigDict

config_dict = ConfigDict(extra='forbid', strict=True, kw_only=True)