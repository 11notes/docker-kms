#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
import re
import sys
import socket
import uuid
import logging
import os
import threading
import socketserver
import queue as Queue
import selectors
from time import monotonic as time

import pykms_RpcBind, pykms_RpcRequest
from pykms_RpcBase import rpcBase
from pykms_Dcerpc import MSRPCHeader
from pykms_Misc import check_setup, check_lcid, check_other
from pykms_Misc import KmsParser, KmsParserException, KmsParserHelp
from pykms_Misc import kms_parser_get, kms_parser_check_optionals, kms_parser_check_positionals, kms_parser_check_connect
from pykms_Format import enco, deco, pretty_printer, justify
from pykms_Connect import MultipleListener
from pykms_Sql import sql_initialize

srv_version             = "py-kms_2020-10-01"
__license__             = "The Unlicense"
__author__              = u"Matteo ℱan <SystemRage@protonmail.com>"
__url__                 = "https://github.com/SystemRage/py-kms"
srv_description         = "py-kms: KMS Server Emulator written in Python"
srv_config = {}

##---------------------------------------------------------------------------------------------------------------------------------------------------------
class KeyServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        daemon_threads = True

        def __init__(self, server_address, RequestHandlerClass, bind_and_activate = True, want_dual = False):
                socketserver.BaseServer.__init__(self, server_address, RequestHandlerClass)
                self.__shutdown_request = False
                self.r_service, self.w_service = socket.socketpair()

                if hasattr(selectors, 'PollSelector'):
                        self._ServerSelector = selectors.PollSelector
                else:
                        self._ServerSelector = selectors.SelectSelector

                if bind_and_activate:
                        try:
                                self.multisock = MultipleListener(server_address, want_dual = want_dual)
                        except Exception as e:
                                if want_dual and str(e) == "dualstack_ipv6 not supported on this platform":
                                        try:
                                                pretty_printer(log_obj = loggersrv.warning,
                                                               put_text = "{reverse}{yellow}{bold}%s. Creating not dualstack sockets...{end}" %str(e))
                                                self.multisock = MultipleListener(server_address, want_dual = False)
                                        except Exception as e:
                                                pretty_printer(log_obj = loggersrv.error, to_exit = True,
                                                               put_text = "{reverse}{red}{bold}%s. Exiting...{end}" %str(e))
                                else:
                                        pretty_printer(log_obj = loggersrv.error, to_exit = True,
                                                       put_text = "{reverse}{red}{bold}%s. Exiting...{end}" %str(e))

                        if self.multisock.cant_dual:
                                delim = ('' if len(self.multisock.cant_dual) == 1 else ', ')
                                pretty_printer(log_obj = loggersrv.warning,
                                               put_text = "{reverse}{yellow}{bold}IPv4 [%s] can't be dualstack{end}" %delim.join(self.multisock.cant_dual))


        def pykms_serve(self):
                """ Mixing of socketserver serve_forever() and handle_request() functions,
                    without elements blocking tkinter.
                    Handle one request at a time, possibly blocking.
                    Respects self.timeout.
                """
                # Support people who used socket.settimeout() to escape
                # pykms_serve() before self.timeout was available.
                timeout = self.multisock.gettimeout()
                if timeout is None:
                        timeout = self.timeout
                elif self.timeout is not None:
                        timeout = min(timeout, self.timeout)
                if timeout is not None:
                        deadline = time() + timeout

                try:
                        # Wait until a request arrives or the timeout expires.
                        with self._ServerSelector() as selector:
                                self.multisock.register(selector)
                                # self-pipe trick.
                                selector.register(fileobj = self.r_service.fileno(), events = selectors.EVENT_READ)

                                while not self.__shutdown_request:
                                        ready = selector.select(timeout)
                                        if self.__shutdown_request:
                                                break

                                        if ready == []:
                                                if timeout is not None:
                                                        timeout = deadline - time()
                                                        if timeout < 0:
                                                                return self.handle_timeout()
                                        else:
                                                for key, mask in ready:
                                                        if key.fileobj in self.multisock.filenos():
                                                                self.socket = self.multisock.sockmap[key.fileobj]
                                                                self.server_address = self.socket.getsockname()
                                                                self._handle_request_noblock()
                                                        elif key.fileobj is self.r_service.fileno():
                                                                # only to clean buffer.
                                                                msgkill = os.read(self.r_service.fileno(), 8).decode('utf-8')
                                                                sys.exit(0)
                finally:
                        self.__shutdown_request = False

        def shutdown(self):
                self.__shutdown_request = True

        def server_close(self):
                self.multisock.close()

        def handle_timeout(self):
                pretty_printer(log_obj = loggersrv.error, to_exit = True,
                               put_text = "{reverse}{red}{bold}Server connection timed out. Exiting...{end}")

        def handle_error(self, request, client_address):
                pass


class server_thread(threading.Thread):
        def __init__(self, queue, name):
                threading.Thread.__init__(self)
                self.name = name
                self.queue = queue
                self.server = None
                self.is_running_server = False
                self.checked = False
                self.is_running_thread = threading.Event()

        def terminate_serve(self):
                self.server.shutdown()
                self.server.server_close()
                self.server = None
                self.is_running_server = False

        def terminate_thread(self):
                self.is_running_thread.set()

        def terminate_eject(self):
                os.write(self.server.w_service.fileno(), u'☠'.encode('utf-8'))

        def run(self):
                while not self.is_running_thread.is_set():
                        try:
                                item = self.queue.get(block = True, timeout = 0.1)
                                self.queue.task_done()
                        except Queue.Empty:
                                continue
                        else:
                                try:
                                        if item == 'start':
                                                self.eject = False
                                                self.is_running_server = True
                                                # Check options.
                                                if not self.checked:
                                                        server_check()
                                                # Create and run server.
                                                self.server = server_create()
                                                self.server.pykms_serve()
                                except (SystemExit, Exception) as e:
                                        self.eject = True
                                        raise

##---------------------------------------------------------------------------------------------------------------------------------------------------------

loggersrv = logging.getLogger('logsrv')

def _str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ValueError('Boolean value expected.')

# 'help' string - 'default' value - 'dest' string.
srv_options = {
        'ip'         : {'help' : 'The IP address (IPv4 or IPv6) to listen on. The default is \"::\" (all interfaces).', 'def' : "::", 'des' : "ip"},
        'port'       : {'help' : 'The network port to listen on. The default is \"1688\".', 'def' : 1688, 'des' : "port"},
        'epid'       : {'help' : 'Use this option to manually specify an ePID to use. If no ePID is specified, a random ePID will be auto generated.',
                        'def' : None, 'des' : "epid"},
        'lcid'       : {'help' : 'Use this option to manually specify an LCID for use with randomly generated ePIDs. Default is \"1033\" (en-us)',
                        'def' : 1033, 'des' : "lcid"},
        'count'      : {'help' : 'Use this option to specify the current client count. A number >=25 is required to enable activation of client OSes; \
for server OSes and Office >=5', 'def' : None, 'des' : "clientcount"},
        'activation' : {'help' : 'Use this option to specify the activation interval (in minutes). Default is \"120\" minutes (2 hours).',
                        'def' : 120, 'des': "activation"},
        'renewal'    : {'help' : 'Use this option to specify the renewal interval (in minutes). Default is \"10080\" minutes (7 days).',
                        'def' : 1440 * 7, 'des' : "renewal"},
        'sql'        : {'help' : 'Use this option to store request information from unique clients in an SQLite database. Deactivated by default.', 'def' : False,
                        'file': os.path.join('.', 'pykms_database.db'), 'des' : "sqlite"},
        'hwid'       : {'help' : 'Use this option to specify a HWID. The HWID must be an 16-character string of hex characters. \
Type \"RANDOM\" to auto-generate the HWID.',
                        'def' : "RANDOM", 'des' : "hwid"},
        'time0'      : {'help' : 'Maximum inactivity time (in seconds) after which the connection with the client is closed. If \"None\" (default) serve forever.',
                        'def' : None, 'des' : "timeoutidle"},
        'time1'      : {'help' : 'Set the maximum time to wait for sending / receiving a request / response. Default is no timeout.',
                        'def' : None, 'des' : "timeoutsndrcv"},
        'asyncmsg'   : {'help' : 'Prints pretty / logging messages asynchronously. Deactivated by default.',
                        'def' : False, 'des' : "asyncmsg"},
        'llevel'     : {'help' : 'Use this option to set a log level. The default is \"WARNING\".', 'def' : "WARNING", 'des' : "loglevel",
                        'choi' : ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "MININFO"]},
        'lfile'      : {'help' : 'Use this option to set an output log file. The default is \"pykms_logserver.log\". \
Type \"STDOUT\" to view log info on stdout. Type \"FILESTDOUT\" to combine previous actions. \
Use \"STDOUTOFF\" to disable stdout messages. Use \"FILEOFF\" if you not want to create logfile.',
                        'def' : os.path.join('.', 'pykms_logserver.log'), 'des' : "logfile"},
        'lsize'      : {'help' : 'Use this flag to set a maximum size (in MB) to the output log file. Deactivated by default.', 'def' : 0, 'des': "logsize"},
        'listen'     : {'help' : 'Adds multiple listening ip address - port couples.', 'des': "listen"},
        'backlog'    : {'help' : 'Specifies the maximum length of the queue of pending connections. Default is \"5\".', 'def' : 5, 'des': "backlog"},
        'reuse'      : {'help' : 'Do not allows binding / listening to the same address and port. Reusing port is activated by default.', 'def' : True,
                        'des': "reuse"},
        'dual'       : {'help' : 'Allows listening to an IPv6 address while also accepting connections via IPv4. If used, it refers to all addresses (main and additional). Activated by default. Pass in "false" or "true" to disable or enable.',
                        'def' : True, 'des': "dual"}
        }

def server_options():
        server_parser = KmsParser(description = srv_description, epilog = 'version: ' + srv_version, add_help = False)
        server_parser.add_argument("ip", nargs = "?", action = "store", default = srv_options['ip']['def'], help = srv_options['ip']['help'], type = str)
        server_parser.add_argument("port", nargs = "?", action = "store", default = srv_options['port']['def'], help = srv_options['port']['help'], type = int)
        server_parser.add_argument("-e", "--epid", action = "store", dest = srv_options['epid']['des'], default = srv_options['epid']['def'],
                                   help = srv_options['epid']['help'], type = str)
        server_parser.add_argument("-l", "--lcid", action = "store", dest = srv_options['lcid']['des'], default = srv_options['lcid']['def'],
                                   help = srv_options['lcid']['help'], type = int)
        server_parser.add_argument("-c", "--client-count", action = "store", dest = srv_options['count']['des'] , default = srv_options['count']['def'],
                                   help = srv_options['count']['help'], type = str)
        server_parser.add_argument("-a", "--activation-interval", action = "store", dest = srv_options['activation']['des'],
                                   default = srv_options['activation']['def'], help = srv_options['activation']['help'], type = int)
        server_parser.add_argument("-r", "--renewal-interval", action = "store", dest = srv_options['renewal']['des'],
                                   default = srv_options['renewal']['def'], help = srv_options['renewal']['help'], type = int)
        server_parser.add_argument("-s", "--sqlite", nargs = "?", dest = srv_options['sql']['des'], const = True,
                                   default = srv_options['sql']['def'], help = srv_options['sql']['help'], type = str)
        server_parser.add_argument("-w", "--hwid", action = "store", dest = srv_options['hwid']['des'], default = srv_options['hwid']['def'],
                                   help = srv_options['hwid']['help'], type = str)
        server_parser.add_argument("-t0", "--timeout-idle", action = "store", dest = srv_options['time0']['des'], default = srv_options['time0']['def'],
                                   help = srv_options['time0']['help'], type = str)
        server_parser.add_argument("-t1", "--timeout-sndrcv", action = "store", dest = srv_options['time1']['des'], default = srv_options['time1']['def'],
                                   help = srv_options['time1']['help'], type = str)
        server_parser.add_argument("-y", "--async-msg", action = "store_true", dest = srv_options['asyncmsg']['des'],
                                   default = srv_options['asyncmsg']['def'], help = srv_options['asyncmsg']['help'])
        server_parser.add_argument("-V", "--loglevel", action = "store", dest = srv_options['llevel']['des'], choices = srv_options['llevel']['choi'],
                                   default = srv_options['llevel']['def'], help = srv_options['llevel']['help'], type = str)
        server_parser.add_argument("-F", "--logfile", nargs = "+", action = "store", dest = srv_options['lfile']['des'],
                                   default = srv_options['lfile']['def'], help = srv_options['lfile']['help'], type = str)
        server_parser.add_argument("-S", "--logsize", action = "store", dest = srv_options['lsize']['des'], default = srv_options['lsize']['def'],
                                   help = srv_options['lsize']['help'], type = float)

        server_parser.add_argument("-h", "--help", action = "help", help = "show this help message and exit")

        ## Connection parsing.
        connection_parser = KmsParser(description = "connect options", add_help = False)
        connection_subparser = connection_parser.add_subparsers(dest = "mode")

        connect_parser = connection_subparser.add_parser("connect", add_help = False)
        connect_parser.add_argument("-n", "--listen", action = "append", dest = srv_options['listen']['des'], default = [],
                                    help = srv_options['listen']['help'], type = str)
        connect_parser.add_argument("-b", "--backlog", action = "append", dest = srv_options['backlog']['des'], default = [],
                                    help = srv_options['backlog']['help'], type = int)
        connect_parser.add_argument("-u", "--no-reuse", action = "append_const", dest = srv_options['reuse']['des'], const = False, default = [],
                                    help = srv_options['reuse']['help'])
        connect_parser.add_argument("-d", "--dual", type = _str2bool, dest = srv_options['dual']['des'], default = srv_options['dual']['def'],
                                    help = srv_options['dual']['help'])

        try:
                userarg = sys.argv[1:]

                # Run help.
                if any(arg in ["-h", "--help"] for arg in userarg):
                        KmsParserHelp().printer(parsers = [server_parser, (connection_parser, connect_parser)])

                # Get stored arguments.
                pykmssrv_zeroarg, pykmssrv_onearg = kms_parser_get(server_parser)
                connect_zeroarg, connect_onearg = kms_parser_get(connect_parser)
                subdict = {
                        'connect' : (connect_zeroarg, connect_onearg, connection_parser.parse_args)
                }
                subpars = list(subdict.keys())
                pykmssrv_zeroarg += subpars # add subparsers

                exclude_kms = ['-F', '--logfile']
                exclude_dup = ['-n', '--listen', '-b', '--backlog', '-u', '--no-reuse']

                # Set defaults for server dict config.
                # example case:
                #       python3 pykms_Server.py
                srv_config.update(vars(server_parser.parse_args([])))

                subindx = sorted([(userarg.index(pars), pars) for pars in subpars if pars in userarg], key = lambda x: x[0])
                if subindx:
                        # Set `daemon options` and/or `connect options` for server dict config.
                        # example cases:
                        # 1     python3 pykms_Server.py [1.2.3.4] [1234] [--pykms_optionals] connect [--connect_optionals]
                        first = subindx[0][0]
                        # initial.
                        kms_parser_check_optionals(userarg[0 : first], pykmssrv_zeroarg, pykmssrv_onearg, exclude_opt_len = exclude_kms)
                        kms_parser_check_positionals(srv_config, server_parser.parse_args, arguments = userarg[0 : first], force_parse = True)
                        # middle.
                        for i in range(len(subindx) - 1):
                                posi, posf, typ = subindx[i][0], subindx[i + 1][0], subindx[i][1]
                                kms_parser_check_optionals(userarg[posi : posf], subdict[typ][0], subdict[typ][1], msg = 'optional %s' %typ,
                                                           exclude_opt_dup = (exclude_dup if typ == 'connect' else []))
                                kms_parser_check_positionals(srv_config, subdict[typ][2], arguments = userarg[posi : posf], msg = 'positional %s' %typ)
                        # final.
                        pos, typ = subindx[-1]
                        kms_parser_check_optionals(userarg[pos:], subdict[typ][0], subdict[typ][1], msg = 'optional %s' %typ,
                                                   exclude_opt_dup = (exclude_dup if typ == 'connect' else []))
                        kms_parser_check_positionals(srv_config, subdict[typ][2], arguments = userarg[pos:], msg = 'positional %s' %typ)

                        if len(subindx) > 1:
                                srv_config['mode'] = '+'.join(elem[1] for elem in subindx)
                else:
                        # Update `pykms options` for server dict config.
                        # example case:
                        # 2     python3 pykms_Server.py [1.2.3.4] [1234] [--pykms_optionals]
                        kms_parser_check_optionals(userarg, pykmssrv_zeroarg, pykmssrv_onearg, exclude_opt_len = exclude_kms)
                        kms_parser_check_positionals(srv_config, server_parser.parse_args)

                kms_parser_check_connect(srv_config, srv_options, userarg, connect_zeroarg, connect_onearg)

        except KmsParserException as e:
                pretty_printer(put_text = "{reverse}{red}{bold}%s. Exiting...{end}" %str(e), to_exit = True)

def server_check():
        # Setup and some checks.
        check_setup(srv_config, srv_options, loggersrv, where = "srv")

        # Random HWID.
        if srv_config['hwid'] == "RANDOM":
                randomhwid = uuid.uuid4().hex
                srv_config['hwid'] = randomhwid[:16]
           
        # Sanitize HWID.
        hexstr = srv_config['hwid']
        # Strip 0x from the start of hexstr
        if hexstr.startswith("0x"):
            hexstr = hexstr[2:]

        hexsub = re.sub(r'[^0-9a-fA-F]', '', hexstr)
        diff = set(hexstr).symmetric_difference(set(hexsub))

        if len(diff) != 0:
                diff = str(diff).replace('{', '').replace('}', '')
                pretty_printer(log_obj = loggersrv.error, to_exit = True,
                               put_text = "{reverse}{red}{bold}HWID '%s' is invalid. Digit %s non hexadecimal. Exiting...{end}" %(hexstr.upper(), diff))
        else:
                lh = len(hexsub)
                if lh % 2 != 0:
                        pretty_printer(log_obj = loggersrv.error, to_exit = True,
                                       put_text = "{reverse}{red}{bold}HWID '%s' is invalid. Hex string is odd length. Exiting...{end}" %hexsub.upper())
                elif lh < 16:
                        pretty_printer(log_obj = loggersrv.error, to_exit = True,
                                       put_text = "{reverse}{red}{bold}HWID '%s' is invalid. Hex string is too short. Exiting...{end}" %hexsub.upper())
                elif lh > 16:
                        pretty_printer(log_obj = loggersrv.error, to_exit = True,
                                       put_text = "{reverse}{red}{bold}HWID '%s' is invalid. Hex string is too long. Exiting...{end}" %hexsub.upper())
                else:
                        srv_config['hwid'] = binascii.a2b_hex(hexsub)

        # Check LCID.
        srv_config['lcid'] = check_lcid(srv_config['lcid'], loggersrv.warning)
                                
        # Check sqlite.
        if srv_config['sqlite']:
                if srv_config['sqlite'] is True: # Resolve bool to the default path
                        srv_config['sqlite'] = srv_options['sql']['file']
                if os.path.isdir(srv_config['sqlite']):
                        pretty_printer(log_obj = loggersrv.warning,
                                put_text = "{reverse}{yellow}{bold}You specified a folder instead of a database file! This behavior is not officially supported anymore, please change your start parameters soon.{end}")
                        srv_config['sqlite'] = os.path.join(srv_config['sqlite'], 'pykms_database.db')

                try:
                        import sqlite3
                        sql_initialize(srv_config['sqlite'])
                except ImportError:
                        pretty_printer(log_obj = loggersrv.warning,
                                put_text = "{reverse}{yellow}{bold}Module 'sqlite3' not installed, database support disabled.{end}")
                        srv_config['sqlite'] = False

        # Check other specific server options.
        opts = [('clientcount', '-c/--client-count'),
                ('timeoutidle', '-t0/--timeout-idle'),
                ('timeoutsndrcv', '-t1/--timeout-sndrcv')]
        check_other(srv_config, opts, loggersrv, where = 'srv')

        # Check further addresses / ports.
        if 'listen' in srv_config:
                addresses = []
                for elem in srv_config['listen']:
                        try:
                                addr, port = elem.split(',')
                        except ValueError:
                                pretty_printer(log_obj = loggersrv.error, to_exit = True,
                                               put_text = "{reverse}{red}{bold}argument `-n/--listen`: %s not well defined. Exiting...{end}" %elem)
                        try:
                                port = int(port)
                        except ValueError:
                                pretty_printer(log_obj = loggersrv.error, to_exit = True,
                                               put_text = "{reverse}{red}{bold}argument `-n/--listen`: port number '%s' is invalid. Exiting...{end}" %port)

                        if not (1 <= port <= 65535):
                                pretty_printer(log_obj = loggersrv.error, to_exit = True,
                                               put_text = "{reverse}{red}{bold}argument `-n/--listen`: port number '%s' is invalid. Enter between 1 - 65535. Exiting...{end}" %port)

                        addresses.append((addr, port))
                srv_config['listen'] = addresses

def server_create():
        # Create address list (when the current user indicates execution inside the Windows Sandbox,
        # then we wont allow port reuse - it is not supported).
        all_address = [(
                        srv_config['ip'], srv_config['port'],
                        (srv_config['backlog_main'] if 'backlog_main' in srv_config else srv_options['backlog']['def']),
                        (srv_config['reuse_main'] if 'reuse_main' in srv_config else srv_options['reuse']['def'])
                        )]
        log_address = "TCP server listening at %s on port %d" %(srv_config['ip'], srv_config['port'])

        if 'listen' in srv_config:
                for l, b, r in zip(srv_config['listen'], srv_config['backlog'], srv_config['reuse']):
                        all_address.append(l + (b,) + (r,))
                        log_address += justify("at %s on port %d" %(l[0], l[1]), indent = 56)

        server = KeyServer(all_address, kmsServerHandler, want_dual = (srv_config['dual'] if 'dual' in srv_config else srv_options['dual']['def']))
        server.timeout = srv_config['timeoutidle']

        loggersrv.info(log_address)
        loggersrv.info("HWID: %s" % deco(binascii.b2a_hex(srv_config['hwid']), 'utf-8').upper())

        return server

def server_terminate(generic_srv, exit_server = False, exit_thread = False):
        if exit_server:
                generic_srv.terminate_serve()
        if exit_thread:
                generic_srv.terminate_thread()

class ServerWithoutGui(object):
        def start(self):
                import queue as Queue
                daemon_queue = Queue.Queue(maxsize = 0)
                daemon_serverthread = server_thread(daemon_queue, name = "Thread-Srv-Daemon")
                daemon_serverthread.setDaemon(True)
                # options already checked in `server_main_terminal`.
                daemon_serverthread.checked = True
                daemon_serverthread.start()
                daemon_queue.put('start')
                return 0, daemon_serverthread

        def join(self, daemon_serverthread):
                while daemon_serverthread.is_alive():
                        daemon_serverthread.join(timeout = 0.5)

        def clean(self, daemon_serverthread):
                server_terminate(daemon_serverthread, exit_server = True, exit_thread = True)

def server_main_terminal():
        # Parse options.
        server_options()
        # Check options.
        server_check()
        serverthread.checked = True

        # Run threaded server.
        serverqueue.put('start')
        # Wait to finish.
        try:
                while serverthread.is_alive():
                        serverthread.join(timeout = 0.5)
        except (KeyboardInterrupt, SystemExit):
                server_terminate(serverthread, exit_server = True, exit_thread = True)

class kmsServerHandler(socketserver.BaseRequestHandler):
        def setup(self):
                loggersrv.info("Connection accepted: %s:%d" %(self.client_address[0], self.client_address[1]))
                srv_config['raddr'] = str(self.client_address[0])

        def handle(self):
                self.request.settimeout(srv_config['timeoutsndrcv'])
                while True:
                        # self.request is the TCP socket connected to the client
                        try:
                                self.data = self.request.recv(1024)
                                if self.data == '' or not self.data:
                                        pretty_printer(log_obj = loggersrv.debug, # use debug, as the healthcheck will spam this
                                                       put_text = "{reverse}{yellow}{bold}No data received.{end}")
                                        break
                        except socket.error as e:
                                pretty_printer(log_obj = loggersrv.error,
                                               put_text = "{reverse}{red}{bold}While receiving: %s{end}" %str(e))
                                break
                        
                        packetType = MSRPCHeader(self.data)['type']
                        if packetType == rpcBase.packetType['bindReq']:
                                loggersrv.info("RPC bind request received.")
                                pretty_printer(num_text = [-2, 2], where = "srv")
                                handler = pykms_RpcBind.handler(self.data, srv_config)
                        elif packetType == rpcBase.packetType['request']:
                                loggersrv.info("Received activation request.")
                                pretty_printer(num_text = [-2, 13], where = "srv")
                                handler = pykms_RpcRequest.handler(self.data, srv_config)
                        else:
                                pretty_printer(log_obj = loggersrv.error,
                                               put_text = "{reverse}{red}{bold}Invalid RPC request type %s.{end}" %packetType)
                                break

                        res = enco(str(handler.populate()), 'latin-1')

                        if packetType == rpcBase.packetType['bindReq']:
                                loggersrv.info("RPC bind acknowledged.")
                                pretty_printer(num_text = [-3, 5, 6], where = "srv")
                        elif packetType == rpcBase.packetType['request']:
                                loggersrv.info("Responded to activation request.")
                                pretty_printer(num_text = [-3, 18, 19], where = "srv")

                        try:
                                self.request.send(res)
                                if packetType == rpcBase.packetType['request']:
                                        break
                        except socket.error as e:
                                pretty_printer(log_obj = loggersrv.error,
                                               put_text = "{reverse}{red}{bold}While sending: %s{end}" %str(e))
                                break

        def finish(self):
                self.request.close()
                loggersrv.info("Connection closed: %s:%d" %(self.client_address[0], self.client_address[1]))


serverqueue = Queue.Queue(maxsize = 0)
serverthread = server_thread(serverqueue, name = "Thread-Srv")
serverthread.daemon = True
serverthread.start()

if __name__ == "__main__":
        server_main_terminal()