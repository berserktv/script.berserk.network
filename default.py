# -*- coding: utf-8 -*-
# Very simple plugin for Kodi mediacenter
# "Network Manager" is a network management software for Ethernet and Wifi network connections
# Project "Berserk" - build Kodi for the Raspberry Pi platform, autor Alexander Demachev, site https://berserk.tv
# license -  The MIT License (MIT)

import os
import sys
import time
import xbmc
import xbmcgui
import xbmcaddon

__id__ = 'script.berserk.network'
__addon__ = xbmcaddon.Addon(id=__id__)
__path__ = __addon__.getAddonInfo('path')
_ = __addon__.getLocalizedString

sys.path.append(xbmc.translatePath(os.path.join(__path__, 'resources', 'lib')))
import utils

if __name__ == '__main__':
    #try:
        arg = None
        ETHERNET = 0
        WLAN  = 1
        if len(sys.argv) > 1:
            arg = sys.argv[1] or False
        extra = sys.argv[2:]
        if not arg:
            sys.exit(0)


        if arg.startswith('butnetwork'):
            __addon__.openSettings()

        if arg.startswith('scan'):
            wlans = utils.getWlanInterfaces()
            iface = utils.getNameWlan(wlans)
            utils.dialogSelectSSID(iface)

        if arg.startswith('inputpass'):
            utils.dialogInputPass()

        if arg.startswith('connectwlan'):
            wlans = utils.getWlanInterfaces()
            eths  = utils.getEthInterfaces()
            iface = utils.getNameWlan(wlans)
            utils.dialogConnectSSID(iface, eths)

        if arg.startswith('connecteth'):
            eths  = utils.getEthInterfaces()
            wlans = utils.getWlanInterfaces()
            iface = utils.getNameEth(eths)
            utils.dialogConnectEthernet(iface, wlans)

    #except Exception, e:
    #    xbmc.executebuiltin('Notification("Berserk", "%s", 5000)' % "Exception ...")


