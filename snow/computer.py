import asyncio
import aiosnow
from snow.declare.Computer import *
from snow.declare.ComputerSupport import *
from snow.declare.Hardware import *
from snow.declare.SysUsers import *
from aiosnow.models import fields
from asyncinit import asyncinit
import time

@asyncinit
class Computer():
    async def __init__(self,serviceNow:object,__sysid__:str=None):
        self.sys_id = __sysid__
        self.serviceNow = serviceNow
        await self.setVar()

    async def setVar(self):
        if self.sys_id == None:
            return {}
        async with HardwareModel(self.serviceNow, table_name="alm_hardware") as Hardware:
            response = await Hardware.get_one(HardwareModel.sys_id == self.sys_id)
            data = response.data
            hardwareInfo = {key:value for key,value in data.items()}
        for key, value in hardwareInfo.items():
            setattr(self, key, value)
            
    async def setHardware(self):
        self.hardwareDict = await self.HardwareLookup(self.ticketDict["serial_number"])

    # updates or add values in the specified field in the hardware table
    async def updateHardware(self,__sysid__,field, values):
        payload = dict(zip(field, values))
        async with HardwareModel(self.serviceNow, table_name="alm_hardware") as Hardware:
            response = await Hardware.update(__sysid__, payload)
        for key in field:
            setattr(self,key,response[key])

    def __eq__(self,other):
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other

    
