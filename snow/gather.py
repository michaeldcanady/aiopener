import asyncio
import aiosnow
from snow.declare.Computer import *
from snow.declare.ComputerSupport import *
from snow.declare.Hardware import *
from snow.declare.SysUsers import *
from aiosnow.models import fields
from asyncinit import asyncinit

@asyncinit
class gatherer():
    async def __init__(self,serviceNow,CSNumber):
        self.CSNumber = CSNumber
        self.serviceNow = serviceNow
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
        self.ticketDict = await self.CSLookup()
        self.hardwareDict = await self.HardwareLookup(self.ticketDict["serial_number"])
        self.lcmDict = await self.HardwareLookup(self.ticketDict["u_asset_returned"])
        self.customerDict = await self.UserLookup(self.ticketDict["requested_for"])
        self.techDict = await self.UserLookup(self.ticketDict["u_wi_primary_tech"])
        self.assignedDict = await self.UserLookup(self.ticketDict["assigned_to"])

    async def __aenter__(self):
        self.ticketDict = await self.CSLookup()
    # Updates ticketDict to reflect current Ticket
    async def CSLookup(self):
        async with CompSupModel(self.serviceNow, table_name="u_computer_support") as CS:
            # Fetches ticket with specified CS
            response = await CS.get_one(CompSupModel.number == self.CSNumber)
            TicketInfo = {}
            for key,value in response.data.items():
                if key == 'u_device_type':
                    value = self.deviceTypeDic[value]
                TicketInfo[key] = value
                if key == 'u_serial_number' and value != None or key == 'u_asset' and value != None:
                    TicketInfo["serial_number"] = value
                if key == 'cat_item':
                    TicketInfo[key] = self.catItemDict[TicketInfo[key]]
        return TicketInfo

    def __aiter__(self):
        return self
        
    # updates or add values in the specified field in the computer support ticket
    async def updateCS(self,field, value):
        async with CompSupModel(self.serviceNow, table_name="u_computer_support") as CS:
            response = await CS.update(CompSupModel.number == self.CSNumber, {field : value})

        await self.reset()
        print("updated {0} is {1}".format(field,response[field]))

    def getTicket(self):
        return self.ticketDict
    
    def getHardware(self):
        return self.hardwareDict

    def getLCM(self):
        return self.lcmDict

    def getCustomer(self):
        return self.customerDict

    def getTech(self):
        return self.techDict

    def getAssigned(self):
        return self.assignedDict

    async def reset(self):
        await self.setTicket()
        await self.setHardware()
        await self.setLCM()
        await self.setCustomer()
        await self.setTech()
        await self.setAssigned()

    def __eq__(self, value, other):
        return self.value == other

    async def setTicket(self):
        self.ticketDict = await self.CSLookup()
    
    async def setHardware(self):
        self.hardwareDict = await self.HardwareLookup(self.ticketDict["serial_number"])
        
    async def setLCM(self):
        self.lcmDict = await self.HardwareLookup(self.ticketDict["u_asset_returned"])

    async def setCustomer(self):
        self.customerDict = await self.UserLookup(self.ticketDict["requested_for"])

    async def setTech(self):
        self.techDict = await self.UserLookup(self.ticketDict["u_wi_primary_tech"])

    async def setAssigned(self):
        self.assignedDict = await self.UserLookup(self.ticketDict["assigned_to"])

    # Updates hardwareDict to reflect current 
    async def HardwareLookup(self,__sysid__):
        async with HardwareModel(self.serviceNow, table_name="alm_hardware") as Hardware:
            response = await Hardware.get_one(HardwareModel.sys_id == __sysid__)
            hardwareInfo = {key:value for key,value in response.data.items()}
            return hardwareInfo

    # updates or add values in the specified field in the hardware table
    async def updateHardware(self,__sysid__,field, value):
        async with HardwareModel(self.serviceNow, table_name="alm_hardware") as Hardware:
            response = await Hardware.update(__sysid__, {field : value})
        await self.reset()
        print("updated {0} is {1}".format(field,response[field]))

    async def updateLCM(self,__sysid__,field, value):
        async with HardwareModel(self.serviceNow, table_name="u_asset_returned") as Hardware:
            response = await Hardware.update(__sysid__, {field : value})
        await self.reset()
        print("updated {0} is {1}".format(field,response[field]))
    

    #async def updateStockRoom(self,field,value):
        

    # Returns the user table for specified sys_id
    async def UserLookup(self,userID):
        if userID == None:
            return {}
        async with SysUserModel(self.serviceNow, table_name="sys_user") as User:
            response = await User.get_one(SysUserModel.sys_id == userID)
            Userdict = {key:value for key,value in response.data.items()}
            return Userdict
