#!/usr/bin/python
# mysqltuner.py - Version 0.1
# High Performance MySQL Tuning Script
# Copyright (C) 2006-2011 Major Hayden - major@mhtx.net
#
# Git repository available: 
#   https://github.com/rackerhacker/mysqltuner-python
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This project would not be possible without help from:
#   Matthew Montgomery     Paul Kehrer          Dave Burgess
#   Jonathan Hinds         Mike Jackson         Nils Breunese
#   Shawn Ashlee           Luuk Vosslamber      Ville Skytta
#   Trent Hornibrook       Jason Gill           Mark Imbriaco
#   Greg Eden              Aubin Galinotti      Giovanni Bechis
#   Bill Bradford          Ryan Novosielski     Michael Scheidell
#   Blair Christensen      Hans du Plooy        Victor Trac
#   Everett Barnes         Tom Krouper          Gary Barrueto
#   Simon Greenaway        Adam Stein           Isart Montane
#   Baptiste M.            Matt Dietz           Ed Leafe
#
# This script is ported over (and improved) from mysqltuner.pl:
#   http://github.com/rackerhacker/MySQLTuner-perl
#
# Much of the work done on this script (as well as the python version) was 
# inspired by Matthew Montgomery's tuning-primer.sh script:
#   http://forge.mysql.com/projects/view.php?id=44
#

import os
import re

def run(cmd):
    return os.popen(cmd).read().strip()

def print_bytes(bytes):
    bytes = float(bytes)
    label = { 1: 'K', 2: 'M', 3: 'G', 4:'T' }
    for x in range(4,0,-1):
        if bytes >= pow(1024,x):
            return '%.1f%s' % (bytes/pow(1024,x), label[x])

class MySQLTalker:
    
    def __init__(self):
        self.get_uname_data()
        

    def get_uname_data(self):
        """ Gets the server's OS type for calculations later. """
        unamedata = os.uname()
        self.server_os = unamedata[0]
        self.server_arch = unamedata[4]

    def get_ram_count(self):
        """ Retrieves the total physical and swap memory in the server 
            (in bytes). """
        os = self.server_os
        if re.match('Linux',os):
            self.physical_memory = run(r"free -b | grep Mem | " \
                "awk '{print $2}'")
            self.swap_memory = run(r"free -b | grep Swap | " \
                "awk '{print $2}'")
        elif re.match('Darwin',os):
            self.physical_memory = run(r'sysctl -n hw.memsize')
            self.swap_memory = run(r"sysctl -n vm.swapusage | " \
                "awk '{print $3}' | sed 's/\..*$//'`")
        elif re.match('NetBSD|OpenBSD',os):
            self.physical_memory = run(r'sysctl -n hw.physmem')
            if self.physical_memory < 0:
                self.physical_memory = run(r'sysctl -n hw.physmem64')
            self.swap_memory = run(r"swapctl -l | grep '^/' | " \
                "awk '{ s+= $2 } END { print s }'")
        elif re.match('BSD',os):
            self.physical_memory = run(r'sysctl -n hw.realmem')
            self.swap_memory = run(r"swapinfo | grep '^/' | " \
                "awk '{ s+= $2 } END { print s }'")
        elif re.match('SunOS',os):
            self.physical_memory = run(r"/usr/sbin/prtconf | grep Memory | " \
                "cut -f 3 -d ' '")
            self.physical_memory *= 1024*1024;
            self.swap_memory = 0
        elif re.match('AIX',os):
            self.physical_memory = run(r"lsattr -El sys0 | grep realmem | " \
                "awk '{print $2}'")
            self.physical_memory *= 1024
            self.swap_memory = run(r'lsps -as | awk -F"(MB| +)" "/MB ' \
                '/{print $2}"')
            self.swap_memory *= 1024*1024