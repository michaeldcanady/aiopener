import asyncio
import aiosnow
from snow.declare.Computer import *
from snow.declare.ComputerSupport import *
from snow.declare.Hardware import *
from snow.declare.SysUsers import *
from aiosnow.models import fields
from asyncinit import asyncinit

@asyncinit
class User(object):
    async def __init__(self,serviceNow:object,__sysid__:str = None):
        self.sys_id = __sysid__
        self.serviceNow = serviceNow
        await self.setVar()

    async def setVar(self):
        print("username:",self.sys_id)
        if self.sys_id == None:
            return {}
        async with SysUserModel(self.serviceNow, table_name="sys_user") as User:
            response = await User.get_one(SysUserModel.sys_id == self.sys_id)
            data = response.data
            Userdict = {key:value for key,value in data.items()}
        for key, value in Userdict.items():
            setattr(self, key, value)        

    async def updateUser(self, field, values):
        payload = dict(zip(field, values))
        async with SysUserModel(self.serviceNow, table_name="u_asset_returned") as User:
            response = await User.update(self.sys_id, payload)
        for key in field:
            setattr(self,key,response[key])

    def __eq__(self,other):
        if self.__class__ != other.__class__:
            return False
        return self.dict == other
