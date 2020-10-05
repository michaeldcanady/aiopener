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
        self.man = {"6d41df2061e7600070465324a3b29797":"Acer",
                    "547a681f010341c05af1fad06158f2db":"Amazon",
                    "a341df2061e7600070465324a3b29799":"Apple",
                    "da41df2061e7600070465324a3b2979c":"Asus",
                    "f341df2061e7600070465324a3b2979f":"Compaq",
                    "f941df2061e7600070465324a3b297a1":"Dell",
                    "5741136061e7600070465324a3b29708":"E-Machine",
                    "b67a681f010341c05af1fad06158f2bb":"Fujitsu",
                    "4d41136061e7600070465324a3b2970a":"Gateway",
                    "58f8fd9edb52ccd03c425ab8dc9619ea":"Google",
                    "ee41136061e7600070465324a3b2970d":"HP",
                    "f741136061e7600070465324a3b29710":"Lenovo",
                    "498aa81f010341c05af1fad06158f29b":"LG",
                    "ba8a2c1f010341c05af1fad06158f25f":"Microsoft",
                    "3441136061e7600070465324a3b297ce":"Other",
                    "049ae81f010341c05af1fad06158f2fa":"Samsung",
                    "d541136061e7600070465324a3b29776":"Sony",
                    "4f419b2c61a7600070465324a3b29758":"Toshiba"}
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
            for key,value in response.data.items():
                if key == 'u_device_type':
                    value = self.deviceTypeDic[value]
                if key == 'cat_item':
                    value = self.catItemDict[value]
                    print(value)
                if key == 'u_serial_number' and value != None:
                    key = "serial_number"
                setattr(self, key, value)

    # updates or add values in the specified field in the computer support ticket
    async def updateCS(self,field, values):
        payload = dict(zip(field, values))
        print("payload",payload)
        async with CompSupModel(self.serviceNow, table_name="u_computer_support") as CS:
            response = await CS.update(CompSupModel.number == self.CSNumber, payload)
        for key in field:
            setattr(self,key,response[key])
            
    def __eq__(self,other):
        if self.__class__ != other.__class__:
            return False
        return self.__dict__ == other

    
