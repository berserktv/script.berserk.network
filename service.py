# -*- coding: utf-8 -*-
# Plugin for Kodi mediacenter
# <<Network Manager>> is a network management software for Ethernet and Wifi network connections
# Project "Berserk" - build Kodi for the Raspberry Pi platform, autor Alexander Demachev, site https://berserk.tv
# license -  The MIT License (MIT)

import os
import sys
import xbmcaddon

__id__ = 'script.berserk.network'
__addon__ = xbmcaddon.Addon(id=__id__)
__path__ = __addon__.getAddonInfo('path')

sys.path.append(xbmc.translatePath(os.path.join(__path__, 'resources', 'lib')))
import utils


if __name__ == "__main__":
    utils.checkFirstRun()

