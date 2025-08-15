# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigSelection, getConfigListEntry
from Components.Label import Label
from Components.ActionMap import ActionMap

from .sorter import sort_services
from . import ui

# Python2 / Python3 Flags
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

PLUGIN_VERSION = "1.6"

# Plugin-Konfiguration
config.plugins.channelsorter = ConfigSubsection()
config.plugins.channelsorter.sort_order = ConfigSelection(default="alphabetical", choices=[
    ("alphabetical", "Alphabetical"),
    ("frequency", "By Frequency"),
    ("random", "Random")
])
config.plugins.channelsorter.channel_type = ConfigSelection(default="TV", choices=[
    ("TV", "TV"),
    ("Radio", "Radio"),
    ("Data", "Data")
])

# Python2/3 kompatibles open
if PY2:
    import codecs
    open_file = lambda f, mode: codecs.open(f, mode, encoding='utf-8')
else:
    open_file = lambda f, mode: open(f, mode, encoding='utf-8', errors='replace')

class ChannelSorterScreen(ConfigListScreen, Screen):
    skin = u"""
    <screen name="ChannelSorterScreen" position="center,center" size="600,400" title="Channel Sorter v{0}">
        <widget name="config" position="10,10" size="580,150" />
        <widget name="status" position="10,170" size="580,200" font="Regular;20" />
    </screen>
    """.format(PLUGIN_VERSION)

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self["status"] = Label("Press OK to sort the current bouquet.")
        self.list = [
            getConfigListEntry("Sort Order", config.plugins.channelsorter.sort_order),
            getConfigListEntry("Channel Type", config.plugins.channelsorter.channel_type)
        ]
        ConfigListScreen.__init__(self, self.list)
        self["actions"] = ActionMap(["OkCancelActions"], {
            "ok": self.select_bouquet,
            "cancel": self.close
        }, -1)

    def select_bouquet(self):
        bouquets = self.get_all_bouquets()
        if not bouquets:
            self["status"].setText("No bouquets found for the selected channel type.")
            return

        if len(bouquets) == 1:
            # Nur ein Bouquet, direkt sortieren
            self.sort_current_bouquet(bouquets[0])
        else:
            # Mehrere Bouquets: Auswahl anzeigen (nur lesbarer Name)
            choices = [(os.path.basename(b), b) for b in bouquets]
            self.session.openWithCallback(self.sort_current_bouquet, ChoiceBox, title="Select Bouquet", list=choices)

    def sort_current_bouquet(self, bouquet):
        if not bouquet:
            self["status"].setText("No bouquet selected.")
            return

        try:
            metadata, services = self.get_services_from_bouquet(bouquet)
            method = config.plugins.channelsorter.sort_order.value
            services = sort_services(services, method)
            self.write_services_to_bouquet(bouquet, metadata, services)
            self["status"].setText("{0} channels sorted by {1}.".format(len(services), method))
        except Exception as e:
            self["status"].setText("Error: {0}".format(str(e)))

    def get_all_bouquets(self):
        channel_type = config.plugins.channelsorter.channel_type.value.lower()
        path = "/etc/enigma2/"
        bouquets = []
        for filename in os.listdir(path):
            if filename.startswith("userbouquet.") and filename.endswith(".{0}".format(channel_type)):
                bouquets.append(os.path.join(path, filename))
        return bouquets

    def get_services_from_bouquet(self, bouquet):
        services = []
        metadata = []
        try:
            with open_file(bouquet, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#SERVICE"):
                        services.append(line)
                    else:
                        metadata.append(line)
        except IOError:
            self["status"].setText("Error: Unable to read bouquet file.")
            return [], []
        return metadata, services

    def write_services_to_bouquet(self, bouquet, metadata, services):
        try:
            with open_file(bouquet, "w") as f:
                for line in metadata:
                    f.write(line + "\n")
                for s in services:
                    f.write(s + "\n")
        except IOError:
            self["status"].setText("Error: Unable to write to bouquet file.")

def main(session, **kwargs):
    session.open(ChannelSorterScreen)

def about(session, **kwargs):
    session.open(ui.AboutChannelSorter)

def Plugins(**kwargs):
    return [
        PluginDescriptor(
            name="Channel Sorter v{0}".format(PLUGIN_VERSION),
            description="Sort bouquet channels by name, frequency, or randomly (Version {0})".format(PLUGIN_VERSION),
            where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
            fnc=main
        ),
        PluginDescriptor(
            name="About Channel Sorter",
            description="About Channel Sorter (Version {0})".format(PLUGIN_VERSION),
            where=[PluginDescriptor.WHERE_PLUGINMENU],
            fnc=about
        )
    ]
