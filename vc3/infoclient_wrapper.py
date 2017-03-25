#!/usr/bin/env python

__version__ = '0.0.1'

import json
import os
import socket
import sys

from optparse import OptionParser
from ConfigParser import ConfigParser

from infoclient import InfoClient

class ExecWrapper(object):
    def __init__(self, executable):
        self.executable = executable

        self.parser = OptionParser(usage='''%prog [WRAPPER-OPTIONS] -- [%prog OPTIONS]''', version='0.0.1')

        self.parser.add_option("--requestid",dest="requestid",
                action="store",
                default=None,
                help='Indicate the name of the requestid %prog should work for.')

        default_conf = "~/etc/vc3/vc3-infoclient.conf"
        if 'VC3_SERVICES_HOME' in os.environ:
            default_conf = os.path.join(os.environ['VC3_SERVICES_HOME'], 'etc', 'vc3-infoclient.conf') + ',' + default_conf
        self.parser.add_option("--conf", dest="confFiles", 
                          default=default_conf,
                          action="store", 
                          metavar="FILE1[,FILE2,FILE3]", 
                          help="Load configuration from FILEs (comma separated list)")

        self.parser.add_option("--executable", dest="exec", 
                default=self.executable,
                action="store", 
                help="Path to %prog.")

        self.parseopts()
        self.__createconfig()

        self.infoclient = InfoClient(self.config)
        self.hostname = self.__my_host_address()
        super(ExecWrapper, self).__init__()

    def parseopts(self):
        (self.options, self.args) = self.parser.parse_args()
        self.options.confFiles    = self.options.confFiles.split(',')

        # ensure this wrapper knows who to work for, give preference to command
        # line argument.
        if not self.options.requestid:
            sys.stderr.write('No requestid was specified with --requestid.\n')
            sys.exit(1)

    def __my_host_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 0))
            addr = s.getsockname()[0]
        except:
            addr = '127.0.0.1'
        finally:
            s.close()
        return addr

    def __createconfig(self):
        """Create config, add in options...
        """
        if self.options.confFiles != None:
            try:
                self.config = ConfigParser()
                self.config.read(self.options.confFiles)
            except Exception, e:
                self.log.error('Config failure')
                sys.exit(1)

    def getinforequestid(self, key):
        runts = self.infoclient.getdocument(key)
        runtd = json.loads(runts)

        # drop one level
        if runtd:
            runtd = runtd[key]
            if self.options.requestid in runtd:
                return runtd[self.options.requestid]
        return None

    def preamble(self):
        # Intent: Read from the infoservice configuration for execute.
        pass

    def epilogue(self):
        # Intent: Remove from infoservice runtime information when execution ends.
        # Bug: Should be called at any exit (signals, etc.).
        pass

    def execute(self):
        # Intent: Remove from infoservice runtime information when execution ends.
        raise NotImplementedError('wrapper did not implement an execute method.')

    def run(self):
        self.preamble()
        self.execute()
        self.epilogue()


