import asyncio
import aiosnow
#from gather import gatherer
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
import time
from formatting.formatter import Formatter
import logging
from snow.ComputerSupport import CompSup
from snow.computer import Computer
from snow.user import User
import wmi

#Settings
_version = '0.0.8' # Program's current version
_filePath = os.path.splitext(__file__)[0]+'.exe' #returns PATH/TO/scriptname.exe
_scriptname = Path(__file__).stem+'.exe' # returns scriptname.exe
creator = "dmcanady" # creator
contributors = [] # add anyone who assisted with the script

async def main():
    start_time = time.time()
    welcome = Formatter(_scriptname,_version,creator,contributors)
    welcome.header()
    username,password = login.login() #validates login info
    __instance__ = 'libertydev.service-now.com' # URL for service now
    serviceNow = aiosnow.Client(__instance__, basic_auth=(username,password)) # creates serviceNow session for creds provided
    CSNumber = input("CS Number: ")
    ticket = await genTicket(serviceNow,CSNumber)
    await initTicket(username,ticket)
    ticketTypes = {"Assignment":__assignment__,"Return":__return__,"Repair":__repair__,"Life Cycle Management":__LCM__}
    await ticketTypes[ticket["CS"].cat_item](ticket)
    print(time.time()-start_time)

async def initTicket(username,computerInfo):
    accept = input("Are you accepting this this ticket as your's (y/n): ")
    if accept == "y":
        await computerInfo["CS"].updateCS("assigned_to",username)
        await computerInfo["assigned"].__init__(computerInfo["CS"].serviceNow,computerInfo["CS"].assigned_to)
        await computerInfo["CS"].updateCS("u_wi_primary_tech",username)
        await computerInfo["technician"].__init__(computerInfo["CS"].serviceNow,computerInfo["CS"].u_wi_primary_tech)
        await computerInfo["CS"].updateCS("state",2)
        await computerInfo["CS"].updateCS("u_substate", " ")
        #Will be used to verify the correct computer is being used.
        print("verifying device's serial")
        c = wmi.WMI()
        serial = computerInfo["computer"].serial_number
        cSerial = c.Win32_ComputerSystem()[0].Name
        if(serial != cSerial):
            print("Please run me on {0}.".format(serial))
            print("Exiting...")
            input("Press any key to continue")
            #sys.exit(0)

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

async def genTicket(serviceNow,CSNumber):
    CS = await CompSup(serviceNow,CSNumber)
    Comp = await Computer(serviceNow,CS.u_asset)
    assigned = await User(serviceNow,CS.assigned_to)
    tech = await User(serviceNow,CS.u_wi_primary_tech)
    customer = await User(serviceNow,CS.requested_for)
    LCMComp = await Computer(serviceNow,CS.u_asset_returned)
    ticket = {"CS":CS,"computer":Comp,"assigned":assigned,"technician":tech,"Customer":customer,"LCM computer": LCMComp}
    return ticket

async def setState(computerInfo,state,__sysid__ = ""):
    if __sysid__ == "":
        __sysid__ = computerInfo["computer"].sys_id
    states = {
        "In Use" : {"install_status":1,"substatus":"","assigned_to":computerInfo["CS"].requested_for},
        "Return" : {"install_status":16,"substatus":"","stockroom":"IT Helpdesk Walkin Support"},
        "LCMed" : {"install_status":6,"substatus":"pending_transfer","stockroom":"IT Helpdesk Walkin Support"}
        }
    if state == "In Use":
         # Assigns customer as assigned to
        await computerInfo["computer"].updateHardware(__sysid__,"assigned_to", states[state]["assigned_to"])
    else:
        await computerInfo["computer"].updateHardware(__sysid__,"stockroom",states[state]["stockroom"])    
    # changes status to in use
    await computerInfo["computer"].updateHardware(__sysid__,"install_status",states[state]["install_status"])
    # Sets substatus to None
    await computerInfo["computer"].updateHardware(__sysid__,"substatus",states[state]["substatus"])

# checks if warranty is expired or not.
async def warrantyCheck(computerInfo):
    # adding support for personal devices
    #if hardwareDict == {}:
    #    print("Personal device warranty check is currently not supported.")
    #    print("Please refer to specific manufacture's site to check.")
    #YYYY-MM-DD
    today = datetime.datetime.now()
    exp = datetime.datetime.strptime(computerInfo["computer"].warranty_expiration, "%Y-%m-%d")
    if exp > today:
        print("device's warranty expires %s" % exp)
    elif exp == today:
        print("device's warranty expires today")
    elif exp < today:
        print("device's warranty expired %s" % exp)

#Processes by ticket type
async def __assignment__(computerInfo):
    print("I am an assignment")
    await setState(computerInfo = computerInfo,state = "In Use")
    # Requested steps to take after
    print("Please run auto-assign")
    print("Check to make sure drivers have been updated.")

async def __return__(computerInfo):
    print("I am a return")
    await setState(computerInfo = computerInfo,state = "Return")
    # Returns true if tech states they uninstalled all licensed programs
    if uninstallApp("return"):
        assoc = input("Is there an associated assignment Ticket (y/n): ")
        # if there is an associated assignment, reboots with intent of reimage
        if assoc == "y":
            await computerInfo["CS"].updateCS("work_notes",
                                        "System checked for licensed applications.")
            print("Please ensure an ethernet cable is securely connected before proceeding.")
            await computerInfo["CS"].updateCS("work_notes",
                                        "begin Win 10 1909 Fac/Staff imaging process via IPv4 PXE")
        # Otherwise reboots with intent to erase all data
        print("Computer will restart shortly to erase data.")
        decide = input("continue (y/n): ")
        if decide == "y":
            await restart()
        else:
            pass
            
async def __repair__(computerInfo):
    print("I am a repair")
    await reimage() # Checks current OS
    await warrantyCheck(computerInfo) # Checks warranty status
    # Checks for unauthorized programs
    if uninstallApp("repair"):
        await computerInfo["CS"].updateCS("work_notes",
                                    "System checked for nonstandard applications.")
        print("Check to make sure drivers have been updated.")


async def __LCM__(computerInfo):
    print("I am an LCM")
    await setState(computerInfo = computerInfo,__sysid__ = computerInfo["computer"].sys_id,state = "In Use")
    await setState(computerInfo = computerInfo,__sysid__ = computerInfo["LCM computer"].sys_id,state = "LCMed")
    

# Starts loop
asyncio.run(main())
