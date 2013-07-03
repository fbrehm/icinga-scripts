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

#---------------------------------------------
# Some module variables

__version__ = '0.1.0'

log = logging.getLogger(__name__)

#==============================================================================
class CheckMegaRaidPlugin(ExtNagiosPlugin):
    """
    A special NagiosPlugin class for checking the state of a LSI MegaRaid
    adapter and its connected enclosures, physical drives and logical volumes.
    """

    #--------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor of the CheckMegaRaidPlugin class.
        """

        usage = """\
                %(prog)s [-v] [-t <timeout>] [-a <adapter_nr> -P <HCA_port> [--rate <RATE>]
                """
        usage = textwrap.dedent(usage).strip()
        usage += '\n       %(prog)s --usage'
        usage += '\n       %(prog)s --help'

        blurb = "Copyright (c) 2013 Frank Brehm, Berlin.\n\n"
        blurb += "Checks the state of a LSI MegaRaid adapter and its connected "
        blurb += "enclosures, physical drives and logical volumes."

        super(CheckMegaRaidPlugin, self).__init__(
                usage = usage, blurb = blurb,
                version = __version__,
        )

        self._adapter_nr = 0
        """
        @ivar: the number of the MegaRaid adapter (e.g. 0)
        @type: str
        """

        self._add_args()

    #------------------------------------------------------------
    @property
    def adapter_nr(self):
        """The number of the MegaRaid adapter (e.g. 0)."""
        return self._adapter_nr

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Typecasting into a dictionary.

        @return: structure as dict
        @rtype:  dict

        """

        d = super(CheckMegaRaidPlugin, self).as_dict()

        d['adapter_nr'] = self.adapter_nr

        return d

    #--------------------------------------------------------------------------
    def _add_args(self):
        """
        Adding all necessary arguments to the commandline argument parser.
        """

        self.add_arg(
                '-a', '--adapter-nr',
                metavar = 'NR',
                dest = 'adapter_nr',
                required = True,
                type = int,
                default = 0,
                help = ("The number of the MegaRaid adapter to check " + 
                        "(Default: %(default)d)."),
        )

    #--------------------------------------------------------------------------
    def parse_args(self, args = None):
        """
        Executes self.argparser.parse_args().

        @param args: the argument strings to parse. If not given, they are
                     taken from sys.argv.
        @type args: list of str or None

        """

        super(CheckMegaRaidPlugin, self).parse_args(args)

        self._adapter_nr = self.argparser.args.adapter_nr

    #--------------------------------------------------------------------------
    def __call__(self):
        """
        Method to call the plugin directly.
        """

        self.parse_args()
        self.init_root_logger()

        state = nagios.state.ok
        out = "MegaRaid adapter %d seems to be okay." % (self.adapter_nr)

        if self.verbose > 2:
            log.debug("Current object:\n%s", pp(self.as_dict()))

        # Checking directories in sysfs ...
        self.exit(state, out)

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 et
