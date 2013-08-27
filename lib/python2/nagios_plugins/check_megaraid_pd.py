#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Frank Brehm
@contact: frank.brehm@profitbricks.com
@copyright: © 2010 - 2013 by Frank Brehm, Berlin
@summary: Module for a class for a nagios/icinga plugin to check the state
          of physical drives on a MegaRaid adapter
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
class CheckMegaRaidPdPlugin(CheckMegaRaidPlugin):
    """
    A special NagiosPlugin class for checking the state of physical drives
    a LSI MegaRaid adapter.
    """

    #--------------------------------------------------------------------------
    def __init__(self):
        """
        Constructor of the CheckMegaRaidPdPlugin class.
        """

        usage = """\
                %(prog)s [-v] [-a <adapter_nr>]:
                """
        usage = textwrap.dedent(usage).strip()
        usage += '\n       %(prog)s --usage'
        usage += '\n       %(prog)s --help'

        blurb = "Copyright (c) 2013 Frank Brehm, Berlin.\n\n"
        blurb += "Checks the number of the state of physical drives on a LSI MegaRaid adapter."

        super(CheckMegaRaidPdPlugin, self).__init__(
                usage = usage, blurb = blurb,
                version = __version__,
        )

        self._add_args()

        self.drive_list = []
        self.drive = {}

    #--------------------------------------------------------------------------
    def as_dict(self):
        """
        Typecasting into a dictionary.

        @return: structure as dict
        @rtype:  dict

        """

        d = super(CheckMegaRaidPdPlugin, self).as_dict()

        return d

    #--------------------------------------------------------------------------
    def _add_args(self):
        """
        Adding all necessary arguments to the commandline argument parser.
        """

        #help_c = """\
        #        The number of hotspare drives, where it becomes critical,
        #        if the number of existing hotspares is below (mandantory,
        #        default: '%(default)s').
        #        """
        #help_c = textwrap.dedent(help_c).replace('\n', ' ').strip()
        #self.add_arg(
        #        '-c', '--critical',
        #        metavar = 'DRIVES:',
        #        dest = 'critical',
        #        required = True,
        #        type = NagiosRange,
        #        default = self.critical_number,
        #        help = help_c,
        #)

        #help_w = """\
        #        The number of hotspare drives, where it becomes a warning,
        #        if the number of existing hotspares is below (mandantory,
        #        default: '%(default)s').
        #        """
        #help_w = textwrap.dedent(help_w).replace('\n', ' ').strip()
        #self.add_arg(
        #        '-w', '--warning',
        #        metavar = 'DRIVES:',
        #        dest = 'warning',
        #        required = True,
        #        type = NagiosRange,
        #        default = self.warning_number,
        #        help = help_w,
        #)

        super(CheckMegaRaidPdPlugin, self)._add_args()

    #--------------------------------------------------------------------------
    def parse_args(self, args = None):
        """
        Executes self.argparser.parse_args().

        If overridden by successors, it should be called via super().

        @param args: the argument strings to parse. If not given, they are
                     taken from sys.argv.
        @type args: list of str or None

        """

        super(CheckMegaRaidPdPlugin, self).parse_args(args)

        #crit = self.argparser.args.critical
        #if not crit.end is None:
        #    msg = ("The critical hot spare number must be given with an " +
        #            "ending colon, e.g. '1:' (given %s).") % (crit)
        #    self.die(msg)
        #self._critical_number = crit

        #warn = self.argparser.args.warning
        #if not warn.end is None:
        #    msg = ("The warning hot spare number must be given with an " +
        #            "ending colon, e.g. '2:' (given %s).") % (warn)
        #    self.die(msg)
        #self._warning_number = warn

        #if crit.start > warn.start:
        #    msg = ("The warning number must be greater than or equal to " +
        #            "the critical number (given warning: '%s', critical " +
        #            "'%s').") % (warn, crit)
        #    self.die(msg)

        #self.set_thresholds(
        #        warning = warn,
        #        critical = crit,
        #)

    #--------------------------------------------------------------------------
    def call(self):
        """
        Method to call the plugin directly.
        """

        state = nagios.state.ok
        out = "State of physical drives of MegaRaid adapter %d seems to be okay." % (
                self.adapter_nr)

        # Enclosure Device ID: 0
        re_enc = re.compile(r'^\s*Enclosure\s+Device\s+ID\s*:\s*(\d+)', re.IGNORECASE)
        # Slot Number: 23
        re_slot = re.compile(r'^\s*Slot\s+Number\s*:\s*(\d+)', re.IGNORECASE)
        # Device Id: 6
        re_dev_id = re.compile(r'^\s*Device\s+Id\s*:\s*(\d+)', re.IGNORECASE)
        # Media Error Count: 0
        re_media_errors = re.compile(r'^\s*Media\s+Error\s+Count\s*:\s*(\d+)', re.IGNORECASE)
        # Other Error Count: 0
        re_other_errors = re.compile(r'^\s*Other\s+Error\s+Count\s*:\s*(\d+)', re.IGNORECASE)
        # Predictive Failure Count: 0
        re_pred_failures = re.compile(r'^\s*Predictive\s+Failure\s+Count\s*:\s*(\d+)', re.IGNORECASE)
        # Firmware state: Online, Spun Up
        re_fw_state = re.compile(r'^\s*Firmware\s+state\s*:\s*(\S+.*)', re.IGNORECASE)
        # Foreign State: None
        re_foreign_state = re.compile(r'^\s*Foreign\s+state\s*:\s*(\S+.*)', re.IGNORECASE)

        re_good_fw_state = re.compile(r'^\s*(?:Online,\s+Spun\s+Up|Hotspare,\s+Spun\s+down|Hotspare,\s+Spun\s+Up)\s*$',
                re.IGNORECASE)

        drives_total = 0
        args = ('-PdList',)
        (stdoutdata, stderrdata, ret, exit_code) = self.megacli(args)
        if self.verbose > 3:
            log.debug("Output on StdOut:\n%s", stdoutdata)

        cur_dev = None

        for line in stdoutdata.splitlines():

            line = line.strip()
            m = re_enc.search(line)
            if m:
                if cur_dev:
                    if ('enclosure' in cur_dev) and ('slot' in cur_dev):
                        pd_id = '[%d:%d]' % (
                                cur_dev['enclosure'], cur_dev['slot'])
                        self.drive_list.append(pd_id)
                        self.drive[pd_id] = cur_dev

                cur_dev = {}
                drives_total += 1
                cur_dev = {
                        'enclosure': int(m.group(1)),
                        'media_errors': 0,
                        'other_errors': 0,
                        'predictive_failures': 0,
                        'fw_state': None,
                        'foreign_state': None,
                }
                continue

            m = re_slot.search(line)
            if m:
                if cur_dev:
                    cur_dev['slot'] = int(m.group(1))
                continue

            m = re_dev_id.search(line)
            if m:
                if cur_dev:
                    cur_dev['dev_id'] = int(m.group(1))
                continue

            m = re_media_errors.search(line)
            if m:
                if cur_dev:
                    cur_dev['media_errors'] = int(m.group(1))
                continue

            m = re_other_errors.search(line)
            if m:
                if cur_dev:
                    cur_dev['other_errors'] = int(m.group(1))
                continue

            m = re_pred_failures.search(line)
            if m:
                if cur_dev:
                    cur_dev['predictive_failures'] = int(m.group(1))
                continue

            m = re_fw_state.search(line)
            if m:
                if cur_dev:
                    cur_dev['fw_state'] = m.group(1)
                continue

            m = re_foreign_state.search(line)
            if m:
                if cur_dev:
                    cur_dev['foreign_state'] = m.group(1)
                continue

        if cur_dev:
            if ('enclosure' in cur_dev) and ('slot' in cur_dev):
                pd_id = '[%d:%d]' % (cur_dev['enclosure'], cur_dev['slot'])
                self.drive_list.append(pd_id)
                self.drive[pd_id] = cur_dev

        media_errors = 0
        other_errors = 0
        predictive_failures = 0
        fw_state_wrong = 0
        foreign_state_wrong = 0
        errors = []

        for pd_id in self.drive_list:
            cur_dev = self.drive[pd_id]
            drive_ok = True
            drv_desc = []

            if cur_dev['media_errors']:
                drive_ok = False
                drv_desc.append("has %d media errors" % (cur_dev['media_errors']))
                media_errors += 1
            if cur_dev['other_errors']:
                drive_ok = False
                drv_desc.append("has %d other errors" % (cur_dev['other_errors']))
                other_errors += 1
            if cur_dev['predictive_failures']:
                drive_ok = False
                drv_desc.append("has %d predictive failures" % (cur_dev['predictive_failures']))
                predictive_failures += 1
            if not re_good_fw_state.search(cur_dev['fw_state']):
                drive_ok = False
                drv_desc.append("has wrong firmware state %r" % (cur_dev['fw_state']))
                fw_state_wrong += 1
            if cur_dev['foreign_state'].lower() != "none":
                drive_ok = False
                drv_desc.append("has wrong foreign state %r" % (cur_dev['foreign_state']))
                foreign_state_wrong += 1
            if not drive_ok:
                state = max_state(state, nagios.state.critical)
                dd = "drive %s has " + ' and '.join(drv_desc)
                errors.append(dd)

        log.debug("Found %d drives.", drives_total)
        if self.verbose > 2:
            log.debug("Found Pds:\n%s", self.drive_list)
            log.debug("Found Pd data:\n%s", self.drive)

        if errors:
            out = ', '.join(errors)

        self.add_perfdata(
                label = 'drives_total',
                value = drives_total,
                uom = '',
        )
        self.add_perfdata(
                label = 'media_errors',
                value = media_errors,
                uom = '',
        )
        self.add_perfdata(
                label = 'other_errors',
                value = other_errors,
                uom = '',
        )
        self.add_perfdata(
                label = 'predictive_failures',
                value = predictive_failures,
                uom = '',
        )
        self.add_perfdata(
                label = 'wrong_fw_state',
                value = fw_state_wrong,
                uom = '',
        )
        self.add_perfdata(
                label = 'wrong_foreign_state',
                value = foreign_state_wrong,
                uom = '',
        )

        self.exit(state, out)

#==============================================================================

if __name__ == "__main__":

    pass

#==============================================================================

# vim: fileencoding=utf-8 filetype=python ts=4 et
