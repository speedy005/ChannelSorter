# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
from . import plugin

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
text_type = unicode if PY2 else str

class AboutChannelSorter(Screen):
    skin = u"""
    <screen name="AboutChannelSorter" position="center,center" size="600,200" title="About Channel Sorter">
        <widget name="label" position="10,10" size="580,180" font="Regular;20" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        about_text = (
            text_type("Channel Sorter Plugin\n\n") +
            text_type("Version: {0}\n").format(plugin.PLUGIN_VERSION) +
            text_type("Author: Your Name\n\n") +
            text_type("Sort your bouquets by name, frequency, or randomly.")
        )
        self["label"] = Label(about_text)
        self["actions"] = ActionMap(
            ["OkCancelActions"],
            {
                "ok": self.close,
                "cancel": self.close
            },
            -1
        )
