#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, Berlin
@summary: Module for CheckMegaRaidPlugin class for a nagios/icinga plugin
          to check a LSI MegaRaid adapter and volumes
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

#==============================================================================
class CheckMegaRaidBBUPlugin(CheckMegaRaidPlugin):
    """
    A special NagiosPlugin class for checking the state of the BBU of a
    LSI MegaRaid adapter.
    """

    #--------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor of the CheckMegaRaidBBUPlugin class.
        """

        usage = """\
                %(prog)s [-v] [-t <timeout>] [-a <adapter_nr>]
                """
        usage = textwrap.dedent(usage).strip()
        usage += '\n       %(prog)s --usage'
        usage += '\n       %(prog)s --help'

        blurb = "Copyright (c) 2013 Frank Brehm, Berlin.\n\n"
        blurb += "Checks the state of the BBU of a LSI MegaRaid adapter."

        super(CheckMegaRaidBBUPlugin, self).__init__(
                usage = usage, blurb = blurb,
                version = __version__,
        )

        self._add_args()

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Typecasting into a dictionary.

        @return: structure as dict
        @rtype:  dict

        """

        d = super(CheckMegaRaidBBUPlugin, self).as_dict()

        #d['adapter_nr'] = self.adapter_nr

        return d

    #--------------------------------------------------------------------------
    def call(self):
        """
        Method to call the plugin directly.
        """

        state = nagios.state.ok
        out = "BBU of MegaRaid adapter %d seems to be okay." % (self.adapter_nr)

        args = ('-AdpBbuCmd', '-GetBbuStatus')
        (stdoutdata, stderrdata, ret, exit_code) = self.megacli(args)
        if self.verbose > 2:
            log.debug("Output on StdOut:\n%s", stdoutdata)

        self.exit(state, out)


#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 et
