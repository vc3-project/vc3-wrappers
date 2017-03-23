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


        cluster_default = None
        if 'VC3_REQUEST_NAME' in os.environ:
            cluster_default = os.environ['VC3_REQUEST_NAME']

        conf_default = '/etc/vc3/core.conf'
        if 'VC3_REQUEST_MAIN_CONF' in os.environ:
            conf_default = os.environ['VC3_REQUEST_MAIN_CONF']

        self.parser = OptionParser(usage='''%prog [WRAPPER-OPTIONS] -- [%prog OPTIONS]''', version='0.0.1')
        self.parser.add_option("--cluster",dest="cluster",
                action="store",
                default=cluster_default,
                help='Indicate to which cluster %prog should report its port.')
        self.parser.add_option("--conf", dest="confFiles", 
                default=conf_default,
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

        if not self.options.cluster:
            sys.stderr.write('No cluster was specified with --cluster.\n')
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

    def get_runtime_info(self):
        runts = self.infoclient.getdocument('runtime')
        runtd = json.loads(runts)

        if runtd and self.options.cluster in runtd:
            return runtd[self.options.cluster]

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


