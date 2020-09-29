import asyncio
import aiosnow
from snow.gather import gatherer
from snow import snowCommands
import login
import subprocess
import os
from pathlib import Path
import sys
import wmi
import requests
import time
import datetime
import winreg
import sys
from formatting.formatter import Formatter
import logging

#Global Variables
_OSVersion = ''
_version = '0.0.5' # Program's current version
_filePath = os.path.splitext(__file__)[0]+'.exe' #returns PATH/TO/scriptname.exe
_scriptname = Path(__file__).stem+'.exe' # returns scriptname.exe
_downloadDIR = '/scripts/Python' # Unused
_desktop = os.path.expanduser('~') + '\\Desktop\\' # unused
states_dict = {"state":{"open":1,"work in progress":2,"closed":3},"substate":{"":1}} # state/substate dictionary
creator = "dmcanady" # creator
contributors = [] # add anyone who assisted with the script

async def main():
    #logging.basicConfig(level=logging.DEBUG) Enabled for debugging only
    welcome = Formatter(_scriptname,_version,creator,contributors)
    welcome.header()
    username,password = login.login() #validates login info
    __instance__ = 'libertydev.service-now.com' # URL for service now
    serviceNow = aiosnow.Client(__instance__, basic_auth=(username,password)) # creates serviceNow session for creds provided
    CSNumber = input("CS Number: ")
    computerInfo = await addTicket(serviceNow,CSNumber)
    await initTicket(username,computerInfo) # sets assigned to, technician to user
    # gets what type of ticket it is
    if computerInfo.getTicket()["cat_item"] == 'Assignment':
        await __assignment__(computerInfo, computerInfo.getTicket()["requested_for"])
    elif computerInfo.getTicket()["cat_item"] == 'Return':
        await __return__(computerInfo,serviceNow)
    elif computerInfo.getTicket()["cat_item"] == 'Repair':
        await __repair__(computerInfo)
    elif computerInfo.getTicket()["cat_item"] == 'Life Cycle Management':
        await __LCM__(computerInfo)

# opens programs and features for tech
def uninstallApp(ticketType):
    print('----')
    # if ticket is a repair, it looks for non standard applications
    if ticketType == "repair":
        message = '  Please uninstall any applications not standard.'
        proType = 'non-standard'
    # if ticket is a return it looks for licensed applications
    elif ticketType == "return":
        message = '  Please uninstall any licensed applications.'
        proType = 'licensed'
    print(message)
    time.sleep(1)
    os.system('cmd /c appwiz.cpl') # opens programs and features
    # Verifies with tech that changes have been made
    removed = input("have all {0} programs been removed (y/n): ".format(proType))
    if removed == "y":
        return True

# initiates the gatherer class
async def addTicket(serviceNow,CSNumber):
    ticket = await gatherer(serviceNow,CSNumber)
    return ticket

# assigns ticket to current tech, updates state to work in progress
async def initTicket(username,computerInfo):
    accept = input("Are you accepting this this ticket as your's (y/n): ")
    if accept == "y":
        await computerInfo.updateCS("assigned_to",username)
        await computerInfo.updateCS("u_wi_primary_tech",username)
        await computerInfo.updateCS("state",2)
        await computerInfo.updateCS("u_substate", " ")
        # Will be used to verify the correct computer is being used.
        print("verifying device's serial")
        print(computerInfo.getHardware()["serial_number"])
        #print(computerInfo.__eq__())
        
# checks if warranty is expired or not.
async def warrantyCheck(hardwareDict):
    # adding support for personal devices
    if hardwareDict == {}:
        print("Personal device warranty check is currently not supported.")
        print("Please refer to specific manufacture's site to check.")
    #YYYY-MM-DD
    today = datetime.datetime.now()
    exp = datetime.datetime.strptime(hardwareDict["warranty_expiration"], "%Y-%m-%d")
    if exp > today:
        print("device's warranty expires %s" % exp)
    elif exp == today:
        print("device's warranty expires today")
    elif exp < today:
        print("device's warranty expired %s" % exp)

# Checks to see if computer needs to have an IPU ran
async def reimage():
    global _OSVersion
    key = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    val = r"ReleaseID"

    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as key:
        _OSVersion = int(winreg.QueryValueEx(key,val)[0])
    if _OSVersion < 1909:
        print("Please run IPUInstaller.exe to update to newest version.")
    elif _OSVersion >=1909:
        print("This computer is 1909 or newer!")

# Restarts device
async def restart():
    for i in reversed(range(11)):
        print("This device will restart in: {:02}".format(i))
        time.sleep(1)
    print("Restarting for reimaging...")
    time.sleep(1)
    os.system("shutdown /r /t 10") # set to restart computer after 10 seconds

async def setInUse(computerInfo,__sysid__):
    # changes status to in use
    user = computerInfo.getTicket()["requested_for"]
    await computerInfo.updateHardware(__sysid__,"install_status",1)
    # Sets substatus to None
    await computerInfo.updateHardware(__sysid__,"substatus","")
    # Assigns customer as assigned to
    await computerInfo.updateHardware(__sysid__,"assigned_to",user)

async def setInStorage(computerInfo,__sysid__):
    # Sets status to in IT Storage
    await computerInfo.updateHardware(__sysid__,"install_status",16)
    # Sets substate to None
    await computerInfo.updateHardware(__sysid__,"substatus"," ")
    # Supposed to set stockroom to IT Helpdesk Walkin Support - needs further testing
    await computerInfo.updateHardware(__sysid__,"stockroom","IT Helpdesk Walkin Support")

async def setLCMed(computerInfo,__sysid__):
    # Sets status to in IT Storage
    await computerInfo.updateHardware(__sysid__,"install_status",6)
    # Sets substate to None
    await computerInfo.updateHardware(__sysid__,"substatus","pending_transfer")
    # Supposed to set stockroom to IT Helpdesk Walkin Support - needs further testing
    await computerInfo.updateHardware(__sysid__,"stockroom","IT Helpdesk Walkin Support")

async def __assignment__(computerInfo,user):
    print("I am an assignment")
    await setInUse(computerInfo.getHardware()["sys_id"])
    # Requested steps to take after
    print("Please run auto-assign")
    print("Check to make sure drivers have been updated.")
    
async def __return__(computerInfo,serviceNow):
    print("I am a return")
    setInStorage(computerInfo,computerInfo.getHardware()["sys_id"])
    # Returns true if tech states they uninstalled all licensed programs
    if uninstallApp("return"):
        assoc = input("Is there an associated assignment Ticket (y/n): ")
        # if there is an associated assignment, reboots with intent of reimage
        if assoc == "y":
            await computerInfo.updateCS("work_notes",
                                        "System checked for licensed applications.")
            print("Please ensure an ethernet cable is securely connected before proceeding.")
            await computerInfo.updateCS("work_notes",
                                        "begin Win 10 1909 Fac/Staff imaging process via IPv4 PXE")
        # Otherwise reboots with intent to erase all data
        print("Computer will restart shortly to erase data.")
        decide = input("continue (y/n): ")
        if decide == "y":
            await restart()
    
async def __repair__(computerInfo):
    print("I am a repair")
    await reimage() # Checks current OS
    await warrantyCheck(computerInfo.getHardware()) # Checks warranty status
    # Checks for unauthorized programs
    if uninstallApp("repair"):
        await computerInfo.updateCS("work_notes",
                                    "System checked for nonstandard applications.")
        print("Check to make sure drivers have been updated.")

# NOT SETUP YET
async def __LCM__(computerInfo):
    print("I am an LCM")
    await setInUse(computerInfo,computerInfo.getHardware()["sys_id"])
    await setLCMed(computerInfo,computerInfo.getLCM()["sys_id"])
        

# Starts loop
asyncio.run(main())
