#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, Berlin
@summary: Module for CheckPpdInstancePlugin class
"""

# Standard modules
import os
import sys
import re
import logging
import textwrap

from numbers import Number

# Third party modules

from pkg_resources import parse_version

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

DEFAULT_TIMEOUT = 30
DEFAULT_PPD_PORT = 8073
DEFAULT_JOB_ID = 1

XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pjd>
    <job-id>%d</job-id>
    <command>info</command>
</pjd>
"""

#==============================================================================
class CheckPpdInstancePlugin(ExtNagiosPlugin):
    """
    A special NagiosPlugin class for checking a running instance of a PPD
    (python provisioning daemon) on a ProfitBricks storage server.
    """

    #--------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor of the CheckPpdInstancePlugin class.
        """

        usage = """\
                %(prog)s [options] -H <server_address> [-P <PPD port>]
                """
        usage = textwrap.dedent(usage).strip()
        usage += '\n       %(prog)s --usage'
        usage += '\n       %(prog)s --help'

        blurb = "Copyright (c) 2013 Frank Brehm, Berlin.\n\n"
        blurb += "Checks the state of the given Infiniband HCA port."

        super(CheckPpdInstancePlugin, self).__init__(
                usage = usage, blurb = blurb,
                version = __version__, timeout = DEFAULT_TIMEOUT,
        )

        self._host_address = None
        """
        @ivar: the DNS name or IP address of the host, running the PPD
        @type: str
        """

        self._ppd_port = DEFAULT_PPD_PORT
        """
        @ivar: the TCP port of PPD on the host to check
        @type: int
        """

        self._min_version = None
        """
        @ivar: the minimum version number of the running PPD
        @type: str or None
        """

        self._job_id = DEFAULT_JOB_ID
        """
        @ivar: the Job-Id to use in PJD to send to PPD
        @type: int
        """

        self._add_args()

    #------------------------------------------------------------
    @property
    def host_address(self):
        """The DNS name or IP address of the host, running the PPD."""
        return self._host_address

    #------------------------------------------------------------
    @property
    def ppd_port(self):
        """The TCP port of PPD on the host to check."""
        return self._ppd_port

    #------------------------------------------------------------
    @property
    def min_version(self):
        """The minimum version number of the running PPD."""
        return self._min_version

    #------------------------------------------------------------
    @property
    def job_id(self):
        """The Job-Id to use in PJD to send to PPD."""
        return self._job_id

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Typecasting into a dictionary.

        @return: structure as dict
        @rtype:  dict

        """

        d = super(CheckPpdInstancePlugin, self).as_dict()

        d['host_address'] = self.host_address
        d['ppd_port'] = self.ppd_port
        d['min_version'] = self.min_version
        d['job_id'] = self.job_id

        return d

    #--------------------------------------------------------------------------
    def _add_args(self):
        """
        Adding all necessary arguments to the commandline argument parser.
        """

        self.add_arg(
                '-H', '--host-address', '--host',
                metavar = 'ADDRESS',
                dest = 'host_address',
                required = True,
                help = ("The DNS name or IP address of the host, " +
                        "running the PPD (mandantory)."),
        )

        self.add_arg(
                '-P', '--port',
                metavar = 'PORT',
                dest = 'ppd_port',
                type = int,
                default = DEFAULT_PPD_PORT,
                help = ("The TCP port of PPD on the host to check " +
                        "(Default: %(default)d)."),
        )

        self.add_arg(
                '--min-version',
                metavar = 'VERSION',
                dest = 'min_version',
                help = ("The minimum version number of the running PPD. " +
                        "If given and the PPD version is less then this, " +
                        "a warning is generated."),
        )

        self.add_arg(
                '-J', '--job-id',
                metavar = 'ID',
                dest = 'job_id',
                type = int,
                default = DEFAULT_JOB_ID,
                help = ("The Job-Id to use in PJD to send to PPD " +
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

        super(CheckPpdInstancePlugin, self).parse_args(args)

        self._host_address = self.argparser.args.host_address
        if self.argparser.args.ppd_port:
            self._ppd_port = self.argparser.args.ppd_port
        if self.argparser.args.min_version:
            self._min_version = self.argparser.args.min_version
        if self.argparser.args.job_id:
            self._job_id = self.argparser.args.job_id

    #--------------------------------------------------------------------------
    def __call__(self):
        """
        Method to call the plugin directly.
        """

        self.parse_args()
        self.init_root_logger()

        state = nagios.state.ok
        out = "PPD on %r port %d seems to be okay." % (
                self.host_address, self.ppd_port)

        if self.verbose > 2:
            log.debug("Current object:\n%s", pp(self.as_dict()))

        self.exit(state, out)

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 et sw=4
