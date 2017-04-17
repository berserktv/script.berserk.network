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
kodi_eths_dir = "/home/root/.kodi/userdata/eths/"
kodi_wlans_dir = "/home/root/.kodi/userdata/wlans/"



#he = utils.getNetworkInterfaces()
#utils.ifconfigUp(iface)


# общие методы плагина 'script.berserk.network'
def log(message):
    xbmc.log ('{}: {}'.format(__id__, message), xbmc.LOGNOTICE)

def debug(message):
    xbmc.log ('{}: {}'.format (__id__, message), xbmc.LOGDEBUG)

def wlanON():
    os.remove(kodi_wlans_dir+"off")

def wlanOFF():
    open(kodi_wlans_dir+"off", 'a').close()

def ethernetON():
    os.remove(kodi_eths_dir+"off")

def ethernetOFF():
    open(kodi_eths_dir+"off", 'a').close()


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
        return (rc,output,error)
    else:
        debug("ERROR COMMAND => {}, error={}, output={}".format(command,error,output))
        return (rc,"",error)

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

def getNameEth():
    iface = ""
    eths = getEthInterfaces()
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
    cmdScan = [tools_script, iface, "scan"]
    # так как основное окно settings.xml будет закрыто (для корректного обновления полей)
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

    wlanON()
    xbmc.executebuiltin('Notification("WLAN network", "%s", 10000)' % "Connection ...")
    # cmdDisconnect = ["/etc/network/wlan", iface, "down"]
    # runCommand(cmdDisconnect)
    # скрипт wlan по команде up проверяет запущен ли wpa_supplicant, и если запущен вначале останавливает его (простой перезапуск)
    cmdConnect = ["/etc/network/wlan", iface, "up"]
    ethDisconn = ["/etc/network/eth-manual", "eth0", "down"] # FIXME: eth0
    rc,output = runCommand(cmdConnect)
    if (rc == 0):
        ethernetOFF()
        runCommand(ethDisconn)
        xbmc.executebuiltin('Notification("WLAN network", "%s", 5000)' % "connected")
        #xbmcgui.Dialog().ok( "Dialog Connect" , "connected")
        return True
    else:
        # не смогли подключиться, возможно неправильно задан пароль ...
        xbmcgui.Dialog().ok( "Dialog Error" , "Could not connect. Probably not correctly set the password ...")
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


def dialogConnectEthernet(iface):
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

    ethernetON()
    cmdConnect = ["/etc/network/eth-manual", iface, "up"]
    wlanDisconn = ["/etc/network/wlan", "wlan0", "down"] # FIXME: wlan0
    rc,output = runCommand(cmdConnect)
    if (rc == 0):
        wlanOFF()
        runCommand(wlanDisconn)
        xbmc.executebuiltin('Notification("Ethernet network", "%s", 5000)' % "connected")
        #xbmcgui.Dialog().ok( "Dialog Connect" , "connected")
        return True
    else:
        # не смогли подключиться
        xbmcgui.Dialog().ok( "Dialog Error" , "Could not connect ...")
        __addon__.openSettings()
        return False

