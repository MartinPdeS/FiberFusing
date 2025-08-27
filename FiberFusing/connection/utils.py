#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum

class TopologyType(Enum):
    """Enumeration for connection topology types."""
    CONVEX = "convex"
    CONCAVE = "concave"
    UNDEFINED = "undefined"


class ConscriptedCircleType(Enum):
    """Enumeration for conscripted circle types."""
    EXTERIOR = "exterior"
    INTERIOR = "interior"