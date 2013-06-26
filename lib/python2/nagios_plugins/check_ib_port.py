#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, Berlin
@summary: Module for CheckIbStatusPlugin class
"""

# Standard modules
import os
import sys
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

__version__ = '0.2.0'

log = logging.getLogger(__name__)

DEFAULT_SPEED = 40
IB_BASE_DIR = os.sep + os.path.join('sys', 'class', 'infiniband')

#==============================================================================
class CheckIbStatusPlugin(ExtNagiosPlugin):
    """
    A special NagiosPlugin class for checking the state of a particular
    infiniband HCA and port.
    """

    #--------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor of the CheckIbStatusPlugin class.
        """

        usage = """\
                %(prog)s [-v] [-t <timeout>] -H <HCA_name> -P <HCA_port> [--rate <RATE>]
                """
        usage = textwrap.dedent(usage).strip()
        usage += '\n       %(prog)s --usage'
        usage += '\n       %(prog)s --help'

        blurb = "Copyright (c) 2013 Frank Brehm, Berlin.\n\n"
        blurb += "Checks the state of the given Infiniband HCA port."

        super(CheckIbStatusPlugin, self).__init__(
                usage = usage, blurb = blurb,
                version = __version__
        )

        self._hca_name = None
        """
        @ivar: the name of the HCA to check (e.g. 'mlx4_0')
        @type: str
        """

        self._hca_port = None
        """
        @ivar: the port number of the HCA to check (e.g. 1)
        @type: int
        """

        self._rate = 40
        """
        @ivar: the expected transfer rate of the HCA port in Gb/sec
        @type: int
        """

    #------------------------------------------------------------
    @property
    def hca_name(self):
        """The name of the HCA to check (e.g. 'mlx4_0')."""
        return self._hca_name

    #------------------------------------------------------------
    @property
    def hca_port(self):
        """The port number of the HCA to check (e.g. 1)."""
        return self._hca_port

    #------------------------------------------------------------
    @property
    def rate(self):
        """The expected transfer rate of the HCA port in Gb/sec."""
        return self._rate

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Typecasting into a dictionary.

        @return: structure as dict
        @rtype:  dict

        """

        d = super(CheckIbStatusPlugin, self).as_dict()

        d['hca_name'] = self.hca_name
        d['hca_port'] = self.hca_port
        d['rate'] = self.rate

        return d

    #--------------------------------------------------------------------------
    def __call__(self):
        """
        Method to call the plugin directly.
        """

        self.parse_args()
        self.init_root_logger()



#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 et
