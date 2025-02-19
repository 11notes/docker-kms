#!/usr/bin/env python3

import binascii
import logging
import time
import uuid

from pykms_Structure import Structure
from pykms_DB2Dict import kmsDB2Dict
from pykms_PidGenerator import epidGenerator
from pykms_Filetimes import filetime_to_dt
from pykms_Sql import sql_update, sql_update_epid
from pykms_Format import justify, byterize, enco, deco, pretty_printer

#--------------------------------------------------------------------------------------------------------------------------------------------------------

loggersrv = logging.getLogger('logsrv')

class UUID(Structure):
        commonHdr = ()
        structure = (
                ('raw', '16s'),
        )

        def get(self):
                return uuid.UUID(bytes_le = enco(str(self), 'latin-1'))

class kmsBase:
        def __init__(self, data, srv_config):
                self.data = data
                self.srv_config = srv_config
                
        class kmsRequestStruct(Structure):
                commonHdr = ()
                structure = (
                        ('versionMinor',            '<H'),
                        ('versionMajor',            '<H'),
                        ('isClientVm',              '<I'),
                        ('licenseStatus',           '<I'),
                        ('graceTime',               '<I'),
                        ('applicationId',           ':', UUID),
                        ('skuId',                   ':', UUID),
                        ('kmsCountedId' ,           ':', UUID),
                        ('clientMachineId',         ':', UUID),
                        ('requiredClientCount',     '<I'),
                        ('requestTime',             '<Q'),
                        ('previousClientMachineId', ':', UUID),
                        ('machineName',             'u'),
                        ('_mnPad',                  '_-mnPad', '126-len(machineName)'),
                        ('mnPad',                   ':'),
                )

                def getMachineName(self):
                        return self['machineName'].decode('utf-16le')
                
                def getLicenseStatus(self):
                        return kmsBase.licenseStates[self['licenseStatus']] or "Unknown"

        class kmsResponseStruct(Structure):
                commonHdr = ()
                structure = (
                        ('versionMinor',         '<H'),
                        ('versionMajor',         '<H'),
                        ('epidLen',              '<I=len(kmsEpid)+2'),
                        ('kmsEpid',              'u'),
                        ('clientMachineId',      ':', UUID),
                        ('responseTime',         '<Q'),
                        ('currentClientCount',   '<I'),
                        ('vLActivationInterval', '<I'),
                        ('vLRenewalInterval',    '<I'),
                )

        class GenericRequestHeader(Structure):
                commonHdr = ()
                structure = (
                        ('bodyLength1',  '<I'),
                        ('bodyLength2',  '<I'),
                        ('versionMinor', '<H'),
                        ('versionMajor', '<H'),
                        ('remainder',    '_'),
                )

        licenseStates = {
                0 : "Unlicensed",
                1 : "Activated",
                2 : "Grace Period",
                3 : "Out-of-Tolerance Grace Period",
                4 : "Non-Genuine Grace Period",
                5 : "Notifications Mode",
                6 : "Extended Grace Period",
        }

        licenseStatesEnum = {
                'unlicensed' : 0,
                'licensed' : 1,
                'oobGrace' : 2,
                'ootGrace' : 3,
                'nonGenuineGrace' : 4,
                'notification' : 5,
                'extendedGrace' : 6
        }

        
        def getPadding(self, bodyLength):
                ## https://forums.mydigitallife.info/threads/71213-Source-C-KMS-Server-from-Microsoft-Toolkit?p=1277542&viewfull=1#post1277542
                return 4 + (((~bodyLength & 3) + 1) & 3)

        def serverLogic(self, kmsRequest):
                pretty_printer(num_text = 15, where = "srv")
                kmsRequest = byterize(kmsRequest)
                loggersrv.debug("KMS Request Bytes: \n%s\n" % justify(deco(binascii.b2a_hex(enco(str(kmsRequest), 'latin-1')), 'latin-1')))                         
                loggersrv.debug("KMS Request: \n%s\n" % justify(kmsRequest.dump(print_to_stdout = False)))
                                        
                clientMachineId = kmsRequest['clientMachineId'].get()
                applicationId = kmsRequest['applicationId'].get()
                skuId = kmsRequest['skuId'].get()
                requestDatetime = filetime_to_dt(kmsRequest['requestTime'])
                                
                # Localize the request time, if module "tzlocal" is available.
                try:
                        from datetime import datetime
                        from tzlocal import get_localzone
                        from pytz.exceptions import UnknownTimeZoneError
                        try:
                                local_dt = datetime.fromisoformat(str(requestDatetime)).astimezone(get_localzone())
                        except UnknownTimeZoneError:
                                pretty_printer(log_obj = loggersrv.warning,
                                               put_text = "{reverse}{yellow}{bold}Unknown time zone ! Request time not localized.{end}")
                                local_dt = requestDatetime
                except ImportError:
                        pretty_printer(log_obj = loggersrv.warning,
                                       put_text = "{reverse}{yellow}{bold}Module 'tzlocal' or 'pytz' not available ! Request time not localized.{end}")
                        local_dt = requestDatetime
                except Exception as e:
                    # Just in case something else goes wrong
                    loggersrv.warning('Okay, something went horribly wrong while localizing the request time (proceeding anyways): ' + str(e))
                    local_dt = requestDatetime
                    pass

                # Activation threshold.
                # https://docs.microsoft.com/en-us/windows/deployment/volume-activation/activate-windows-10-clients-vamt                
                MinClients = kmsRequest['requiredClientCount'] 
                RequiredClients = MinClients * 2
                if self.srv_config["clientcount"] != None:
                        if 0 < self.srv_config["clientcount"] < MinClients:
                                # fixed to 6 (product server) or 26 (product desktop)
                                currentClientCount = MinClients + 1
                                pretty_printer(log_obj = loggersrv.warning,
                                               put_text = "{reverse}{yellow}{bold}Not enough clients ! Fixed with %s, but activated client \
could be detected as not genuine !{end}" %currentClientCount)
                        elif MinClients <= self.srv_config["clientcount"] < RequiredClients:
                                currentClientCount = self.srv_config["clientcount"]
                                pretty_printer(log_obj = loggersrv.warning,
                                               put_text = "{reverse}{yellow}{bold}With count = %s, activated client could be detected as not genuine !{end}" %currentClientCount)
                        elif self.srv_config["clientcount"] >= RequiredClients:
                                # fixed to 10 (product server) or 50 (product desktop)
                                currentClientCount = RequiredClients
                                if self.srv_config["clientcount"] > RequiredClients:
                                        pretty_printer(log_obj = loggersrv.warning,
                                                       put_text = "{reverse}{yellow}{bold}Too many clients ! Fixed with %s{end}" %currentClientCount)
                else:
                        # fixed to 10 (product server) or 50 (product desktop)
                        currentClientCount = RequiredClients     

                        
                # Get a name for SkuId, AppId.        
                kmsdb = kmsDB2Dict()
                appName, skuName = str(applicationId), str(skuId)
 
                appitems = kmsdb[2]
                for appitem in appitems:
                        kmsitems = appitem['KmsItems']
                        for kmsitem in kmsitems:                                       
                                skuitems = kmsitem['SkuItems']
                                for skuitem in skuitems:
                                        try:
                                                if uuid.UUID(skuitem['Id']) == skuId:
                                                        skuName = skuitem['DisplayName']
                                                        break
                                        except:
                                                skuName = skuId
                                                pretty_printer(log_obj = loggersrv.warning,
                                                               put_text = "{reverse}{yellow}{bold}Can't find a name for this product !{end}")
                                    
                        try:
                                if uuid.UUID(appitem['Id']) == applicationId:
                                        appName = appitem['DisplayName']
                        except:
                                appName = applicationId
                                pretty_printer(log_obj = loggersrv.warning,
                                               put_text = "{reverse}{yellow}{bold}Can't find a name for this application group !{end}")

                infoDict = {
                        "machineName" : kmsRequest.getMachineName(),
                        "clientMachineId" : str(clientMachineId),
                        "appId" : appName,
                        "skuId" : skuName,
                        "licenseStatus" : kmsRequest.getLicenseStatus(),
                        "requestTime" : int(time.time()),
                        "kmsEpid" : None,
                        "machineIp"  : self.srv_config['raddr']
                }

                loggersrv.info("Machine Name: %s" % infoDict["machineName"])
                loggersrv.info("Machine IP: %s" % infoDict["machineIp"])
                loggersrv.info("Client Machine ID: %s" % infoDict["clientMachineId"])
                loggersrv.info("Application ID: %s" % infoDict["appId"])
                loggersrv.info("SKU ID: %s" % infoDict["skuId"])
                loggersrv.info("License Status: %s" % infoDict["licenseStatus"])
                loggersrv.info("Request Time: %s" % local_dt.strftime('%Y-%m-%d %H:%M:%S %Z (UTC%z)'))
                
                if self.srv_config['loglevel'] == 'MININFO':
                        loggersrv.mininfo("", extra = {'host': self.srv_config['raddr'],
                                                       'status' : infoDict["licenseStatus"],
                                                       'product' : infoDict["skuId"]})
                # Create database.
                if self.srv_config['sqlite']:
                        sql_update(self.srv_config['sqlite'], infoDict)

                return self.createKmsResponse(kmsRequest, currentClientCount, appName)

        def createKmsResponse(self, kmsRequest, currentClientCount, appName):
                response = self.kmsResponseStruct()
                response['versionMinor'] = kmsRequest['versionMinor']
                response['versionMajor'] = kmsRequest['versionMajor']
                
                if not self.srv_config["epid"]:
                        response["kmsEpid"] = epidGenerator(kmsRequest['kmsCountedId'].get(), kmsRequest['versionMajor'],
                                                            self.srv_config["lcid"]).encode('utf-16le')
                else:
                        response["kmsEpid"] = self.srv_config["epid"].encode('utf-16le')

                response['clientMachineId'] = kmsRequest['clientMachineId']
                # rule: timeserver - 4h <= timeclient <= timeserver + 4h, check if is satisfied (TODO).
                response['responseTime'] = kmsRequest['requestTime']
                response['currentClientCount'] = currentClientCount
                response['vLActivationInterval'] = self.srv_config["activation"]
                response['vLRenewalInterval'] = self.srv_config["renewal"]

                # Update database epid.
                if self.srv_config['sqlite']:
                        sql_update_epid(self.srv_config['sqlite'], kmsRequest, response, appName)

                loggersrv.info("Server ePID: %s" % response["kmsEpid"].decode('utf-16le'))
                        
                return response


import pykms_RequestV4, pykms_RequestV5, pykms_RequestV6, pykms_RequestUnknown

def generateKmsResponseData(data, srv_config):
        version = kmsBase.GenericRequestHeader(data)['versionMajor']
        currentDate = time.strftime("%a %b %d %H:%M:%S %Y")

        if version == 4:
                loggersrv.info("Received V%d request on %s." % (version, currentDate))
                messagehandler = pykms_RequestV4.kmsRequestV4(data, srv_config)     
        elif version == 5:
                loggersrv.info("Received V%d request on %s." % (version, currentDate))
                messagehandler = pykms_RequestV5.kmsRequestV5(data, srv_config)
        elif version == 6:
                loggersrv.info("Received V%d request on %s." % (version, currentDate))
                messagehandler = pykms_RequestV6.kmsRequestV6(data, srv_config)
        else:
                loggersrv.info("Unhandled KMS version V%d." % version)
                messagehandler = pykms_RequestUnknown.kmsRequestUnknown(data, srv_config)
                
        return messagehandler.executeRequestLogic()