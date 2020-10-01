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
class CompSup():
    async def __init__(self,serviceNow:object,CSNumber:str):
        self.deviceTypeDic = {"973d8e71e52f20007046ad720a5e1aed":"Liberty Desktop",
                         "e83dc271e52f20007046ad720a5e1a3a":"Liberty Laptop",
                         "e83dc271e52f20007046ad720a5e1a3d":"Liberty Tablet",
                         "a23dce71e52f20007046ad720a5e1a99":"Other Liberty Device",
                         "cd3d02b1e52f20007046ad720a5e1a24":"Other Personal Device",
                         "903dce71e52f20007046ad720a5e1a9e":"Personal Desktop",
                         "a83dce71e52f20007046ad720a5e1a9b":"Personal Laptop",
                         "8f3d02b1e52f20007046ad720a5e1a21":"Personal Tablet"}
        self.catItemDict = {"cd13f3032b7892001235717bf8da1580":"Repair",
                       "a6b3bfcf2b3892001235717bf8da1530":"Life Cycle Management",
                       "de733bcf2b3892001235717bf8da152d":"Quick help",
                       "e604f7032b7892001235717bf8da153c":"Assignment",
                       "f2343b032b7892001235717bf8da1507":"Return"}
        # Commonly modified and used entries
        self.CSNumber = CSNumber
        self.serviceNow = serviceNow
        await self.setVar()

    async def setVar(self):
        if self.CSNumber == None:
            return {}
        async with CompSupModel(self.serviceNow, table_name="u_computer_support") as CS:
            # Fetches ticket with specified CS
            response = await CS.get_one(CompSupModel.number == self.CSNumber)
            TicketInfo = {}
            for key,value in response.data.items():
                if key == 'u_device_type':
                    value = self.deviceTypeDic[value]
                if key == 'cat_item':
                    value = self.catItemDict[value]
                TicketInfo[key] = value
                if key == 'u_serial_number' and value != None or key == 'u_asset' and value != None:
                    TicketInfo["serial_number"] = value
                setattr(self, key, value)

    # updates or add values in the specified field in the computer support ticket
    async def updateCS(self,field, value):
        async with CompSupModel(self.serviceNow, table_name="u_computer_support") as CS:
            response = await CS.update(CompSupModel.number == self.CSNumber, {field : value})
            setattr(self,field,response[field])
            print("updated {0} is {1}".format(field,response[field]))
            
    def __eq__(self,other):
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other

    
