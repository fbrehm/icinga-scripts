#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, Berlin
@summary: Module for a class for a nagios/icinga plugin to check the number
          of hotspare drives on a LSI MegaRaid adapter
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

__version__ = '0.2.0'

log = logging.getLogger(__name__)

#==============================================================================
class CheckMegaRaidHotsparePlugin(CheckMegaRaidPlugin):
    """
    A special NagiosPlugin class for checking the number of hotspare drives on
    a LSI MegaRaid adapter.
    """

    #--------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor of the CheckMegaRaidHotsparePlugin class.
        """

        usage = """\
                %(prog)s [-v] [-a <adapter_nr>] -c <critical_hotspares> -w <warning_hotspares>
                """
        usage = textwrap.dedent(usage).strip()
        usage += '\n       %(prog)s --usage'
        usage += '\n       %(prog)s --help'

        blurb = "Copyright (c) 2013 Frank Brehm, Berlin.\n\n"
        blurb += "Checks the number of hotspare drives on a LSI MegaRaid adapter."

        super(CheckMegaRaidHotsparePlugin, self).__init__(
                usage = usage, blurb = blurb,
                version = __version__,
        )

        self._critical_number = NagiosRange('1:')

        self._warning_number = NagiosRange('2:')

        self._add_args()

    #------------------------------------------------------------
    @property
    def critical_number(self):
        """The number of hotspare drives, where it becomes critical, if
        the number of existing hotspares is below."""
        return self._critical_number

    #------------------------------------------------------------
    @property
    def warning_number(self):
        """The number of hotspare drives, where it becomes a warning, if
        the number of existing hotspares is below."""
        return self._warning_number

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Typecasting into a dictionary.

        @return: structure as dict
        @rtype:  dict

        """

        d = super(CheckMegaRaidHotsparePlugin, self).as_dict()

        d['critical_number'] = self.critical_number
        d['warning_number'] = self.warning_number

        return d


#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 et
