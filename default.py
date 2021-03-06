# -*- coding: utf-8 -*-
# Plugin for Kodi mediacenter
# <<Network Manager>> is a network management software for Ethernet and Wifi network connections
# Project "Berserk" - build Kodi for the Raspberry Pi platform, autor Alexander Demachev, site https://berserk.tv
# license -  The MIT License (MIT)

import sys
import xbmc
import xbmcaddon

__id__ = 'script.berserk.network'
__addon__ = xbmcaddon.Addon(id=__id__)
from resources.lib import utils

if __name__ == '__main__':
    try:
        arg = None
        if len(sys.argv) > 1:
            arg = sys.argv[1] or False
        extra = sys.argv[2:]
        if not arg:
            sys.exit(0)

        if arg.startswith('butnetwork'):
            __addon__.openSettings()

        elif arg.startswith('scan'):
            wlans = utils.getWlanInterfaces()
            iface = utils.getNameWlan(wlans)
            utils.dialogSelectSSID(iface)

        elif arg.startswith('inputpass'):
            utils.dialogInputPass()

        elif arg.startswith('unsetpass'):
            utils.dialogUnsetPass()

        elif arg.startswith('sshapply'):
            utils.applySshConfig()

        elif arg.startswith('connectwlan'):
            wlans = utils.getWlanInterfaces()
            eths  = utils.getEthInterfaces()
            iface = utils.getNameWlan(wlans)
            utils.dialogConnectSSID(iface, eths, wlans)

        elif arg.startswith('connecteth'):
            eths  = utils.getEthInterfaces()
            wlans = utils.getWlanInterfaces()
            iface = utils.getNameEth(eths)
            utils.dialogConnectEthernet(iface, wlans)

        elif arg.startswith('iptvsimple'):
            xbmcaddon.Addon(id='pvr.iptvsimple').openSettings()

    except Exception, e:
        xbmc.executebuiltin('Notification("Berserk", "%s", 5000)' % "Exception ...")


