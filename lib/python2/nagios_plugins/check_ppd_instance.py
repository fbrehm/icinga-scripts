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
import socket
import textwrap
import time
import select
import signal

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

__version__ = '0.2.2'

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30
DEFAULT_PPD_PORT = 8073
DEFAULT_JOB_ID = 1
DEFAULT_POLLING_INTERVAL = 0.05
DEFAULT_BUFFER_SIZE = 8192

XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<pjd>
    <job-id>%d</job-id>
    <command>info</command>
</pjd>
"""

#==============================================================================
class SocketTransportError(NagiosPluginError):
    '''
    Base error class
    '''
    pass

#==============================================================================
class NoListeningError(SocketTransportError):
    pass

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

        self._polling_interval = DEFAULT_POLLING_INTERVAL

        self._buffer_size = DEFAULT_BUFFER_SIZE

        self._should_shutdown = False

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

    @ppd_port.setter
    def ppd_port(self, value):
        v = abs(int(value))
        if v == 0:
            raise ValueError("The port must not be zero.")
        if v >= 2 ** 16:
            raise ValueError("The port must not greater than %d." % (
                    (2 ** 16 - 1)))
        self._ppd_port = v

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

    @job_id.setter
    def job_id(self, value):
        v = int(value)
        self._job_id = abs(v)

    #------------------------------------------------------------
    @property
    def timeout(self):
        """Seconds before plugin times out."""
        if not hasattr(self, 'argparser'):
            return DEFAULT_TIMEOUT
        return self.argparser.args.timeout

    #------------------------------------------------------------
    @property
    def polling_interval(self):
        """The polling interval on network socket."""
        return self._polling_interval

    @polling_interval.setter
    def polling_interval(self, value):
        v = float(value)
        if v == 0:
            raise ValueError("The polling interval must not be zero.")
        self._polling_interval = abs(v)

    #------------------------------------------------------------
    @property
    def buffer_size(self):
        """The size of the buffer for the socket operation."""
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, value):
        v = abs(int(value))
        if v < 512:
            raise ValueError("The buffer size must be greater than 512 bytes.")
        self._buffer_size = v

    #------------------------------------------------------------
    @property
    def should_shutdown(self):
        """Should the current process shutdown by a signal from outside."""
        return self._should_shutdown

    @should_shutdown.setter
    def should_shutdown(self, value):
        self._should_shutdown = bool(value)

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
        d['timeout'] = self.timeout
        d['polling_interval'] = self.polling_interval
        d['should_shutdown'] = self.should_shutdown
        d['buffer_size'] = self.buffer_size

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

    #--------------------------------------------------------------------------
    def send(self, message):
        """
        Sends the message over network socket to the recipient.
        It waits for all replies and gives them back all.

        @raise NoListeningError: if PPD isn't listening on the given port
        @raise SocketTransportError: on some communication errors or timeouts

        @param message: the message to send over the network
        @type message: str

        @return: response from server, or None
        @rtype: str

        """

        if self.verbose > 2:
            msg = "Sending message to %r, port %d with a timeout of %d seconds."
            log.debug(msg, self.host_address, self.ppd_port, self.timeout)

        s = None
        sa = None
        for res in socket.getaddrinfo(self.host_address, self.ppd_port,
                socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except socket.error, msg:
                s = None
                continue
            try:
                s.connect(sa)
            except socket.error, msg:
                s.close()
                s = None
                continue
            break

        if s is None:
            msg = "PPD seems not to listen on %r, port %d." % (
                    self.host_address, self.ppd_port)
            raise NoListeningError(msg)

        if my_verbose > 3:
            msg = ("Got a socket address of %s." % (str(sa)))
            log.debug(msg)

        # Fileno of client socket
        s_fn = s.fileno()

        # Sending the message
        s.send(message)

        # Wait for an answer
        begin = time.time()
        data = ''
        break_on_timeout = False
        result_line = ''
        chunk = ''

        try:
            while not self.should_shutdown:

                cur_time = time.time()
                secs = cur_time - begin

                if secs > self.timeout:
                    break_on_timeout = True
                    break

                rlist, wlist, elist = select.select(
                        [s_fn], [], [], polling_interval)

                if s_fn in rlist:
                    data = s.recv(buffer_size)
                    if data == '':
                        if my_verbose > 3:
                            log.debug("Socket closed from remote.")
                        if chunk != '':
                            break
                    result_line += data
                    chunk += data
                else:
                    if chunk != '':
                        chunk = ''

        except select.error, e:
            if e[0] == 4:
                pass
            else:
                log.error("Error in select(): "  + str(e))

        s.close()

        if break_on_timeout:
            secs = time.time() - begin
            msg = 'Timeout after %0.2f seconds.' % (secs)
            raise SocketTransportError(msg)

        return result_line


#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 et sw=4
