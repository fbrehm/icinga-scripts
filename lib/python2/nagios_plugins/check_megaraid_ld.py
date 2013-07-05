#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, Berlin
@summary: Module for a class for a nagios/icinga plugin to check a particular
          logical drive on a LSI MegaRaid adapter
"""

# Standard modules
import os
import sys
import re
import logging
import textwrap

from numbers import Number

# Third party modules

# Own modules

import nagios
from nagios import BaseNagiosError

from nagios.common import pp, caller_search_path

from nagios.plugin import NagiosPluginError

from nagios.plugin.functions import max_state

from nagios.plugin.range import NagiosRange

from nagios.plugin.threshold import NagiosThreshold

from nagios.plugins import ExtNagiosPluginError
from nagios.plugins import ExecutionTimeoutError
from nagios.plugins import CommandNotFoundError
from nagios.plugins import ExtNagiosPlugin

import nagios_plugins.check_megaraid
from nagios_plugins.check_megaraid import CheckMegaRaidPlugin

#---------------------------------------------
# Some module variables

__version__ = '0.1.0'

log = logging.getLogger(__name__)

# Example output
"""
0 storage208:~ # megacli -LdInfo -L 0 -a0
                                     

Adapter 0 -- Virtual Drive Information:
Virtual Drive: 0 (Target Id: 0)
Name                :
RAID Level          : Primary-1, Secondary-0, RAID Level Qualifier-0
Size                : 55.375 GB
Sector Size         : 512
Is VD emulated      : No
Mirror Data         : 55.375 GB
State               : Optimal
Strip Size          : 256 KB
Number Of Drives    : 2
Span Depth          : 1
Default Cache Policy: WriteBack, ReadAdaptive, Direct, No Write Cache if Bad BBU
Current Cache Policy: WriteBack, ReadAdaptive, Direct, No Write Cache if Bad BBU
Default Access Policy: Read/Write
Current Access Policy: Read/Write
Disk Cache Policy   : Enabled
Encryption Type     : None
PI type: No PI

Is VD Cached: No



Exit Code: 0x00
0 storage208:~ # megacli -LdInfo -L 3 -a0
                                     

Adapter 0 -- Virtual Drive Information:
Virtual Drive: 3 (Target Id: 3)
Name                :
RAID Level          : Primary-1, Secondary-0, RAID Level Qualifier-0
Size                : 2.728 TB
Sector Size         : 512
Is VD emulated      : No
Mirror Data         : 2.728 TB
State               : Optimal
Strip Size          : 256 KB
Number Of Drives    : 2
Span Depth          : 1
Default Cache Policy: WriteBack, ReadAdaptive, Direct, No Write Cache if Bad BBU
Current Cache Policy: WriteBack, ReadAdaptive, Direct, No Write Cache if Bad BBU
Default Access Policy: Read/Write
Current Access Policy: Read/Write
Disk Cache Policy   : Enabled
Encryption Type     : None
PI type: No PI

Is VD Cached: Yes
Cache Cade Type : Read Only



Exit Code: 0x00
"""



#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 et
