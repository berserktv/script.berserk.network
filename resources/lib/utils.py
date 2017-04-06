# -*- coding: utf-8 -*-
# Very simple plugin for Kodi mediacenter
# "Network Manager" is a network management software for Ethernet and Wifi network connections
# Project "Berserk" - build Kodi for the Raspberry Pi platform, autor Alexander Demachev, site https://berserk.tv
# license -  The MIT License (MIT)

import os
import xbmc
import xbmcgui
import xbmcaddon
import subprocess

__id__ = 'script.berserk.network'
__addon__ = xbmcaddon.Addon(id=__id__)
tools_script = "/etc/network/tools-wifi.sh"
kodi_wlans_dir = "/home/root/.kodi/userdata/wlans/"

# общие методы плагина 'script.berserk.network'
def log(message):
    xbmc.log ('{}: {}'.format(__id__, message), xbmc.LOGNOTICE)

def debug(message):
    xbmc.log ('{}: {}'.format (__id__, message), xbmc.LOGDEBUG)


def ifconfigUp(iface):
    output = ""
    if(iface!=None):
        command = ["ifconfig", iface, "up"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        (stdoutdata, stderrdata) = process.communicate();
        output =  stdoutdata
        # ошибка с правами выполнения команды
        if (stderrdata.find("SIOCSIFFLAGS:")>-1):
            log("ERROR COMMAND => ifconfig {} up => {}".format(iface,stderrdata))

def runCommand(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    (stdoutdata, stderrdata) = process.communicate();
    output = stdoutdata
    error = stderrdata
    rc = process.returncode

    if (rc == 0):
        return (rc,output)
    else:
        debug("ERROR COMMAND => {}, error={}, output={}".format(command,error,output))
        return (rc,"")

def getWlanInterfaces():
    wifaces=[]
    cmd = ["iwconfig"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    (stdoutdata, stderrdata) = process.communicate();
    res = stdoutdata
    # Wifi интерфейсов может быть несколько ( :-)понатыкали тут, RPI не резиновая)
    strings = res.splitlines()
    for s in strings:
        if(s.find("IEEE 802.11")!=-1):
                wifaces.append(s.split()[0])
    return wifaces


def dialogNotFindWlan():
    xbmcgui.Dialog().ok( "Not find WLAN" , "Make sure the adapter Wi-Fi is plugged" )
    __addon__.openSettings()

def dialogPassError():
    xbmcgui.Dialog().ok( "Error password" , "Password not set or length less than 8 symbols" )



def getNameWlan():
    iface = ""
    wlans = getWlanInterfaces()
    l = len(wlans)
    if (l > 1):
        ret = xbmcgui.Dialog().select("Select WLAN interface", wlans)
        if (ret != -1): iface = wlans[ret]
        else: dialogNotFindWlan()
    else:
        if (l == 1): iface = wlans[0]
    return iface


def dialogSelectSSID(iface):
    if (iface==""): return False
    cmdScan = [tools_script, iface, "scan"]
    # так как основное окно settings.xml будет закрыто (для корректного обновления полей окна settings)
    # вывожу сообщение о состоянии
    xbmc.executebuiltin('Notification("WLAN network", "%s", 7000)' % "Scanning ...")
    rc,output = runCommand(cmdScan)
    if (rc == 0):
        wlanlist = output.splitlines()
        ret = xbmcgui.Dialog().select("Find WLAN network", wlanlist)
        ssid = "None"
        security = "None"
        if (ret != -1):
            strinf = wlanlist[ret].split()
            ssid = strinf[0]
            security = strinf[3]

        conf = kodi_wlans_dir+ssid
        __addon__.setSetting("ssid", ssid)
        __addon__.setSetting("security", security)
        if (os.path.isfile(conf)): __addon__.setSetting("pass", "save")
        else: __addon__.setSetting("pass", "")

        __addon__.openSettings()
        return True
    else:
        dialogNotFindWlan()
        return False

def dialogGenSSID(str1):
    iface = "not_use"
    ssid = __addon__.getSetting("ssid")
    if (ssid == ""): dialogNotFindWlan()
    elif (str1 == ""): dialogPassError()
    else:
        # command iface gen ssid pass /path/file
        cmdGen = [tools_script, iface, "gen", ssid, str1, kodi_wlans_dir+ssid]
        xbmc.executebuiltin('Notification("WLAN network", "%s", 10000)' % "Generate and save password {}".format(cmdGen[5]) )
        rc,output = runCommand(cmdGen)
        if (rc == 0):
            xbmcgui.Dialog().ok( "Password Generate" , "saved:   {}".format(cmdGen[5]))
            return True
        else:
            dialogPassError()

    return False



def dialogInputPass():
    str1 = xbmcgui.Dialog().input("Input Password (min length 8 simbols)")
    if( len(str1) >= 8 ):
        if (dialogGenSSID(str1)):
            # реальный пароль не сохраняем, только хеш
            __addon__.setSetting("pass", "save")
    else: dialogPassError()
    __addon__.openSettings()



def dialogConnectSSID(iface):
    if (iface==""): return False
    ssid = __addon__.getSetting("ssid")
    str1 = __addon__.getSetting("pass")
    if (ssid == "" or str1 == ""):
        dialogPassError()
        return False

    cmdDisconnect = ["/etc/network/wlan", iface, "down"]
    cmdConnect = ["/etc/network/wlan", iface, "up"]
    runCommand(cmdDisconnect)
    rc,output = runCommand(cmdConnect)
    if (rc == 0):
        xbmcgui.Dialog().ok( "Dialog Connect" , "connected")
        return True
    else:
        # не смогли подключиться, возможно неправильно задан пароль ...
        xbmcgui.Dialog().ok( "Dialog Connect" , "Could not connect. Probably not correctly set the password ...")
        return False



