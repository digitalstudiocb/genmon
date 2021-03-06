#!/usr/bin/env python
#-------------------------------------------------------------------------------
#    FILE: modbusbase.py
# PURPOSE: Base modbus class support
#
#  AUTHOR: Jason G Yates
#    DATE: 19-Apr-2018
#
# MODIFICATIONS:
#-------------------------------------------------------------------------------

from __future__ import print_function       # For python 3.x compatibility with print function

import datetime, threading, crcmod, sys, time
import mylog, mythread, mysupport

#------------ ModbusBase class -------------------------------------------------
class ModbusBase(mysupport.MySupport ):
    def __init__(self,
        updatecallback,
        address = 0x9d,
        name = "/dev/serial",
        rate=9600,
        config = None):

        super(ModbusBase, self).__init__()
        self.Address = address
        self.Rate = rate
        self.PortName = name
        self.config = config
        self.InitComplete = False
        self.IsStopping = False
        self.UpdateRegisterList = updatecallback
        self.RxPacketCount = 0
        self.TxPacketCount = 0
        self.ComTimoutError = 0
        self.TotalElapsedPacketeTime = 0
        self.SlaveException = 0
        self.CrcError = 0
        self.ComValidationError = 0
        self.UnexpectedData = 0
        self.SlowCPUOptimization = False
        self.UseTCP = False

        if self.config != None:
            self.loglocation = self.config.ReadValue('loglocation', default = '/var/log/')
            self.SlowCPUOptimization = self.config.ReadValue('optimizeforslowercpu', return_type = bool, default = False)
            self.UseTCP = self.config.ReadValue('use_serial_tcp', return_type = bool, default = False)
            self.Address = int(self.config.ReadValue('address', default = '9d'),16)         # modbus address
            self.AdditionalModbusTimeout = self.config.ReadValue('additional_modbus_timeout', return_type = float, default = 0.0)
        else:
            self.loglocation = default = './'


        self.CommAccessLock = threading.RLock()     # lock to synchronize access to the serial port comms
        self.ModbusStartTime = datetime.datetime.now()     # used for com metrics

        # log errors in this module to a file
        self.log = mylog.SetupLogger("mymodbus", self.loglocation + "mymodbus.log")

    #-------------ModbusBase::ProcessMasterSlaveWriteTransaction----------------
    def ProcessMasterSlaveWriteTransaction(self, Register, Length, Data):
        return

    #-------------ModbusBase::ProcessMasterSlaveTransaction--------------------
    def ProcessMasterSlaveTransaction(self, Register, Length, skipupdate = False, ReturnString = False):
        return

    #-------------ModbusProtocol::ProcessMasterSlaveFileReadTransaction---------
    def ProcessMasterSlaveFileReadTransaction(self, Register, Length, skipupdate = False, file_num = 1, ReturnString = False):
        return
    # ---------- ModbusBase::GetCommStats---------------------------------------
    def GetCommStats(self):
        SerialStats = collections.OrderedDict()

        SerialStats["Packet Count"] = "M: %d, S: %d" % (self.TxPacketCount, self.RxPacketCount)

        if self.CrcError == 0 or self.TxPacketCount == 0:
            PercentErrors = 0.0
        else:
            PercentErrors = float(self.CrcError) / float(self.TxPacketCount)

        if self.ComTimoutError == 0 or self.TxPacketCount == 0:
            PercentTimeoutErrors = 0.0
        else:
            PercentTimeoutErrors = float(self.ComTimoutError) / float(self.TxPacketCount)

        SerialStats["CRC Errors"] = "%d " % self.CrcError
        SerialStats["CRC Percent Errors"] = ("%.2f" % (PercentErrors * 100)) + "%"
        SerialStats["Packet Timeouts"] = "%d" %  self.ComTimoutError
        SerialStats["Packet Timeouts Percent Errors"] = ("%.2f" % (PercentTimeoutErrors * 100)) + "%"
        SerialStats["Modbus Exceptions"] = self.SlaveException
        SerialStats["Validation Errors"] = self.ComValidationError
        SerialStats["Invalid Data"] = self.UnexpectedData
        # Add serial stats here
        CurrentTime = datetime.datetime.now()

        #
        Delta = CurrentTime - self.ModbusStartTime        # yields a timedelta object
        PacketsPerSecond = float((self.TxPacketCount + self.RxPacketCount)) / float(Delta.total_seconds())
        SerialStats["Packets Per Second"] = "%.2f" % (PacketsPerSecond)

        if self.ModBus.RxPacketCount:
            AvgTransactionTime = float(self.TotalElapsedPacketeTime / self.RxPacketCount)
            SerialStats["Average Transaction Time"] = "%.4f sec" % (AvgTransactionTime)

        return SerialStats
    # ---------- ModbusBase::ResetCommStats-------------------------------------
    def ResetCommStats(self):
        self.RxPacketCount = 0
        self.TxPacketCount = 0
        self.CrcError = 0
        self.ComTimoutError = 0
        self.ComValidationError = 0
        self.SlaveException = 0
        self.TotalElapsedPacketeTime = 0
        self.ModbusStartTime = datetime.datetime.now()     # used for com metrics
        pass

    #------------ModbusBase::Flush----------------------------------------------
    def Flush(self):
        pass

    #------------ModbusBase::Close----------------------------------------------
    def Close(self):
        pass
