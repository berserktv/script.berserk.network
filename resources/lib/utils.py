# -*- coding: utf-8 -*-
# Plugin for Kodi mediacenter
# <<Network Manager>> is a network management software for Ethernet and Wifi network connections
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
kodi_eths_dir = "/home/root/.kodi/userdata/eths/"
kodi_wlans_dir = "/home/root/.kodi/userdata/wlans/"
dropbear_config = "/etc/default/dropbear"
first_run="/tmp/first.bs.run"


# общие методы плагина 'script.berserk.network'
def log(message):
    xbmc.log ('{}: {}'.format(__id__, message), xbmc.LOGNOTICE)

def debug(message):
    xbmc.log ('{}: {}'.format (__id__, message), xbmc.LOGDEBUG)

def wlanON():
    f = kodi_wlans_dir+"off"
    if (os.path.isfile(f)):
        os.remove(f)

def wlanOFF():
    open(kodi_wlans_dir+"off", 'a').close()

def ethernetON():
    f = kodi_eths_dir+"off"
    if (os.path.isfile(f)):
        os.remove(f)

def ethernetOFF():
    open(kodi_eths_dir+"off", 'a').close()

def checkFirstRun():
    if (os.path.isfile(first_run)):
        xbmcgui.Dialog().ok( "Greetings" , "Welcome !!!" )
        __addon__.openSettings()
        os.remove(first_run)

def runCommand(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    (stdoutdata, stderrdata) = process.communicate();
    output = stdoutdata
    error = stderrdata
    rc = process.returncode
    if (rc == 0):
        return (rc,output,error)
    else:
        debug("ERROR COMMAND => {}, error={}, output={}".format(command,error,output))
        return (rc,"",error)

def checkPluged(iface):
    cmdPluged = [tools_script, iface, "check_pluged"]
    rc,output,error = runCommand(cmdPluged)
    if (rc == 0): return True
    return False

def getWlanInterfaces():
    wifaces=[]
    cmd = ["iwconfig"]
    rc,output,error = runCommand(cmd)
    if (rc != 0):
        dialogNotFindWlan()
        return wifaces

    # Wifi интерфейсов может быть несколько ( :-)понатыкали тут, RPI не резиновая)
    strings = output.splitlines()
    for s in strings:
        if(s.find("IEEE 802.11")!=-1):
            wifaces.append(s.split()[0])
    return wifaces


def getEthInterfaces():
    efaces=[]
    cmd = ["iwconfig"]
    rc,output,error = runCommand(cmd)
    if (rc != 0):
        dialogNotFindEth()
        return efaces

    # смотрим только интерфейсы не WiFi
    strings = error.splitlines()
    # сетевых плат также может быть несколько
    for s in strings:
        if(s.find("no wireless extensions")!=-1):
            name = s.split()[0]
            if(name != "lo"): efaces.append(name)
    return efaces

def dialogNotFindWlan():
    xbmcgui.Dialog().ok( "Not find WLAN" , "Make sure the adapter Wi-Fi is plugged" )
    __addon__.openSettings()

def dialogNotFindEth():
    xbmcgui.Dialog().ok( "Not find Ethernet" , "Check ethernet network" )

def dialogPassError():
    xbmcgui.Dialog().ok( "Error password" , "Password not set or length less than 8 symbols" )

def dialogIpError():
    xbmcgui.Dialog().ok( "Error ip" , "IP address is not set" )

def dialogIfaceNotReady(iface):
    xbmcgui.Dialog().ok( "Dialog Error" , "Interface {} - not ready".format(iface) )


def checkReadyInterface(iface):
    cmdUp = ["ifconfig", iface, "up"]
    rc,output,error = runCommand(cmdUp)
    if (rc != 0):
        dialogIfaceNotReady(iface)
        return False
    if not checkPluged(iface):
        xbmcgui.Dialog().ok( "Dialog Error" , "Network cable is not pluged")
        return False
    return True

def getNameWlan(wlans):
    iface = ""
    l = len(wlans)
    if (l > 1):
        ret = xbmcgui.Dialog().select("Select WLAN interface", wlans)
        if (ret != -1): iface = wlans[ret]
        else: dialogNotFindWlan()
    else:
        if (l == 1): iface = wlans[0]
    return iface

def getNameEth(eths):
    iface = ""
    l = len(eths)
    if (l > 1):
        ret = xbmcgui.Dialog().select("Select Ethernet interface", eths)
        if (ret != -1): iface = eths[ret]
        else: dialogNotFindEth()
    else:
        if (l == 1): iface = eths[0]
    return iface


def dialogSelectSSID(iface):
    if (iface==""): return False

    cmdUp = ["ifconfig", iface, "up"]
    rc,output,error = runCommand(cmdUp)
    if (rc != 0):
        dialogIfaceNotReady(iface)
        return False

    cmdScan = [tools_script, iface, "scan"]
    # так как основное окно settings.xml будет закрыто (для корректного обновления полей)
    # вывожу сообщение о состоянии
    xbmc.executebuiltin('Notification("WLAN network", "%s", 7000)' % "Scanning ...")
    rc,output,error = runCommand(cmdScan)
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
        rc,output,error = runCommand(cmdGen)
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
            # реальный пароль не сохраняю, только хеш (:-)прям безопасная я вся такая - "Вайфая")
            __addon__.setSetting("pass", "save")
    else: dialogPassError()
    __addon__.openSettings()


def disconnectEths(eths):
    for i in eths:
        if checkPluged(i):
            xbmc.executebuiltin('Notification("Ethernet", "%s", 5000)' % "interface - {} OFF".format(i))
        # выключаю в любом случае, мало ли кабель отвалился
        cmdDisconnect = ["/etc/network/eth-manual", i, "down"]
        runCommand(cmdDisconnect)

def disconnectWlans(wlans):
    for i in wlans:
        if checkPluged(i):
            xbmc.executebuiltin('Notification("WLAN", "%s", 5000)' % "interface - {} OFF".format(i))
        cmdDisconnect = ["/etc/network/wlan", i, "down"]
        runCommand(cmdDisconnect)


def dialogConnectSSID(iface, eths):
    if (iface==""): return False
    ssid = __addon__.getSetting("ssid")
    str1 = __addon__.getSetting("pass")
    if (ssid == "" or str1 == ""):
        dialogPassError()
        return False

    wlanON()
    disconnectEths(eths)
    cmdDisconnect = ["/etc/network/wlan", iface, "down"]
    cmdConnect = ["/etc/network/wlan", iface, "up"]
    # полный вариант переинициализации с выключением dhclient (если запущен)
    runCommand(cmdDisconnect)
    xbmc.executebuiltin('Notification("WLAN network", "%s", 10000)' % "waiting to connect ...")
    rc,output,error = runCommand(cmdConnect)
    if (rc == 0):
        ethernetOFF()
        xbmc.executebuiltin('Notification("WLAN network", "%s", 5000)' % "Connected")
        return True
    else:
        # не смогли подключиться, возможно неправильно задан пароль ...
        xbmcgui.Dialog().ok( "Dialog Error" , "Could not connect. Probably not correctly set the password")
        __addon__.openSettings()
        return False


def saveConfigEthernet(iface, ip, mask, gateway, dns1, dns2):
    cfg = open(kodi_eths_dir+iface, 'w')
    cfg.write("ETH_IP=\"{}\"\n".format(ip))
    cfg.write("ETH_NETMASK=\"{}\"\n".format(mask))
    cfg.write("ETH_GATEWAY=\"{}\"\n".format(gateway))
    cfg.write("ETH_DNS1=\"{}\"\n".format(dns1))
    cfg.write("ETH_DNS2=\"{}\"\n".format(dns2))
    cfg.close()


def dialogConnectEthernet(iface, wlans):
    if (iface==""): return False
    ip = __addon__.getSetting("ip")
    mask = __addon__.getSetting("netmask")
    gateway = __addon__.getSetting("gateway")
    dns1 = __addon__.getSetting("dns1")
    dns2 = __addon__.getSetting("dns2")
    dhcp = __addon__.getSetting("dhcp")

    if (dhcp == "true"): ip = "dhcp"
    elif (ip == "" ):
        dialogIpError()
        __addon__.openSettings()
        return False

    saveConfigEthernet(iface, ip, mask, gateway, dns1, dns2)
    if not checkReadyInterface(iface):
        __addon__.openSettings()
        return False

    ethernetON()
    disconnectWlans(wlans)
    # полный вариант переинициализации, с выключением dhclient (если запущен)
    cmdDisconnect = ["/etc/network/eth-manual", iface, "down"]
    cmdConnect = ["/etc/network/eth-manual", iface, "up"]
    xbmc.executebuiltin('Notification("Ethernet network", "%s", 5000)' % "waiting to connect ...")
    runCommand(cmdDisconnect)
    rc,output,error = runCommand(cmdConnect)
    if (rc == 0):
        wlanOFF()
        xbmc.executebuiltin('Notification("Ethernet network", "%s", 5000)' % "Connected")
        return True
    else:
        # не смогли подключиться
        xbmcgui.Dialog().ok( "Dialog Error" , "Could not connect ...")
        __addon__.openSettings()
        return False


def applySshConfig():
    res = False
    mess = ""
    cmdSsh = []
    sshon = __addon__.getSetting("sshon")
    start = (sshon == "true")
    is_ssh = os.path.isfile("/etc/init.d/ssh")
    is_dropbear = os.path.isfile("/etc/init.d/dropbear")

    if (is_dropbear): cmdSsh.append("/etc/init.d/dropbear")
    elif (is_ssh): cmdSsh.append("/etc/init.d/ssh")

    if (start):
        cmdSsh.append("start")
        mess = "start"
    else:
        cmdSsh.append("stop")
        mess = "stop"

    xbmc.executebuiltin('Notification("Ssh service", "%s", 5000)' % mess)
    rc,output,error = runCommand(cmdSsh)
    if (rc == 0): res = True
    else: xbmc.executebuiltin('Notification("Ssh service", "%s", 5000)' % "Failed")

    if (is_dropbear): configDropbear(start)
    return res


def configDropbear(start):
    if (os.path.isfile(dropbear_config)):
        cfg = open(dropbear_config,'r')
        filedata = cfg.read()
        newdata = filedata
        cfg.close()
        if (filedata.find("NO_START=") != -1):
            if (start): newdata = filedata.replace("NO_START=1","NO_START=0")
            else: newdata = filedata.replace("NO_START=0","NO_START=1")
        else:
            if (start): newdata += "NO_START=0\n"
            else: newdata += "NO_START=1\n"

        cfg = open(dropbear_config,'w')
        cfg.write(newdata)
        cfg.close()
    else:
        cfg = open(dropbear_config,'w')
        cfg.write("DROPBEAR_EXTRA_ARGS=\"-B\"\n")
        if (start): cfg.write("NO_START=0\n")
        else: cfg.write("NO_START=1\n")
        cfg.close()


