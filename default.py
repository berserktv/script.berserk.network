# -*- coding: utf-8 -*-
# Very simple plugin for Kodi mediacenter
# "Network Manager" is a network management software for Ethernet and Wifi network connections
# Project "Berserk" - build Kodi for the Raspberry Pi platform, autor Alexander Demachev, site https://berserk.tv
# license -  The MIT License (MIT)

import os
import sys
import time
import xbmc
import xbmcaddon
import xbmcgui



__id__ = 'script.berserk.network'
__addon__ = xbmcaddon.Addon(id=__id__)
__path__ = __addon__.getAddonInfo('path')
_ = __addon__.getLocalizedString

sys.path.append(xbmc.translatePath(os.path.join(__path__, 'resources', 'lib')))
import utils


if __name__ == '__main__':

    #try:
        arg = None
        if len(sys.argv) > 1:
            arg = sys.argv[1] or False

        extra = sys.argv[2:]


        #he = utils.getNetworkInterfaces()
        #utils.ifconfigUp(iface)
        ###command = ["iwlist", iface, "scanning"]
        #cmdGen = ["/tmp/tools-wifi.sh", iface, "gen"]

        iface = ""
        output = ""
        ssid = "None"

        # пока при выборе WLAN, сохраняется выбранный ssid, после выбора Ethernet
        # поле сохраняется (и поэтому выводиться поля в Settings.xml = None
        # => нужно как то исправить
        #typenet = __addon__.getSetting("iface")
        #if (typenet == "Ethernet" ):
        #    __addon__.setSetting("ssid", ssid)
        #if arg and arg.startswith('choiсeTypeNet'):
        #    type_net = ["Ethernet", "WLAN"]
        #    ret = xbmcgui.Dialog().select("Select type net", type_net)


        if arg and arg.startswith('butnetwork'):
            __addon__.openSettings()

        if arg and arg.startswith('scan'):
            iface = utils.getNameWlan()
            utils.dialogSelectSSID(iface)

        if arg and arg.startswith('connect'):
            iface = utils.getNameWlan()
            utils.dialogConnectSSID(iface)

        if arg and arg.startswith('inputpass'):
            utils.dialogInputPass()


    #except Exception, e:
    #    xbmc.executebuiltin('Notification("Berserk", "%s", 5000)' % "Exception ")


