# Copyright (C) 2014  Niklas Rosenstein
# All rights reserved.

import sys
PY2 = sys.version_info[0] < 3
PY3 = not PY2

if PY2:
    string_types = (basestring,)
else:
    string_types = (str, bytes)

