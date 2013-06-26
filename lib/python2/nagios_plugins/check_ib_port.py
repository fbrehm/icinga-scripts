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

__version__ = '0.3.0'

log = logging.getLogger(__name__)

DEFAULT_RATE = 40
DEFAULT_TIMEOUT = 2
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
                version = __version__, timeout = DEFAULT_TIMEOUT,
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

        self._add_args()

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
    def _add_args(self):
        """
        Adding all necessary arguments to the commandline argument parser.
        """

        self.add_arg(
                '-H', '--hca-name',
                metavar = 'HCA',
                dest = 'hca_name',
                required = True,
                help = "The name of the HCA to check (e.g. 'mlx4_0').",
        )

        self.add_arg(
                '-P', '--hca-port',
                metavar = 'PORT',
                dest = 'hca_port',
                type = int,
                required = True,
                help = "The port number of the HCA to check (e.g. 1).",
        )

        self.add_arg(
                '--rate',
                metavar = 'RATE',
                dest = 'rate',
                type = int,
                default = DEFAULT_RATE,
                help = ("The expected transfer rate of the HCA port " +
                        "in Gb/sec (Default: %(default)d)."),
        )

    #--------------------------------------------------------------------------
    def parse_args(self, args = None):
        """
        Executes self.argparser.parse_args().

        @param args: the argument strings to parse. If not given, they are
                     taken from sys.argv.
        @type args: list of str or None

        """

        super(CheckIbStatusPlugin, self).parse_args(args)

        self._hca_name = self.argparser.args.hca_name
        self._hca_port = self.argparser.args.hca_port
        self._rate = self.argparser.args.rate

    #--------------------------------------------------------------------------
    def __call__(self):
        """
        Method to call the plugin directly.
        """

        self.parse_args()
        self.init_root_logger()

        state = nagios.state.ok
        out = "Infiniband port %s:%d seems to be okay." % (
                self.hca_name, self.hca_port)

        if self.verbose > 2:
            log.debug("Current object:\n%s", pp(self.as_dict()))

        # Checking directories in sysfs ...
        hca_dir = os.path.join(IB_BASE_DIR, self.hca_name)
        ports_dir = os.path.join(hca_dir, 'ports')
        port_dir = os.path.join(ports_dir, str(self.hca_port))

        for sysfsdir in (IB_BASE_DIR, hca_dir, ports_dir, port_dir):
            if self.verbose > 1:
                log.debug("Checking directory %r ...", sysfsdir)
            if not os.path.exists(sysfsdir):
                msg = "Directory %r doesn't exists." % (sysfsdir)
                self.exit(nagios.state.critical, msg)
            if not os.path.isdir(sysfsdir):
                msg = "%r is not a directory." % (sysfsdir)
                self.exit(nagios.state.critical, msg)

        # Checking state files
        state_file = os.path.join(port_dir, 'state')
        phys_state_file = os.path.join(port_dir, 'phys_state')
        rate_file = os.path.join(port_dir, 'rate')

        for sfile in (state_file, phys_state_file, rate_file):
            if self.verbose > 1:
                log.debug("Checking file %r ...", sfile)
            if not os.path.exists(sfile):
                msg = "File %r doesn't exists." % (sfile)
                self.exit(nagios.state.critical, msg)
            if not os.path.isfile(sfile):
                msg = "%r is not a regular file." % (sfile)
                self.exit(nagios.state.critical, msg)

        # Checking

        self.exit(state, out)

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 et
