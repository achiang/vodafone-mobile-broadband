# -*- coding: utf-8 -*-
# Copyright (C) 2006-2007  Vodafone España, S.A.
# Author:  Pablo Martí
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fi1fth Floor, Boston, MA 02110-1301 USA.
"""
Controllers for diagnostics
"""
#from gtkmvc import Controller
from wader.bcm.contrib.gtkmvc import Controller

from wader.common.consts import CRD_INTFACE, MDM_INTFACE
from wader.common.provider import NetworkProvider
from wader.bcm.logger import logger


class DiagnosticsController(Controller):
    """Controller for the diagnostics window"""

    def __init__(self, model, parent_ctrl):
        super(DiagnosticsController, self).__init__(model)
        self.parent_ctrl = parent_ctrl

    def register_view(self, view):
        """
        Fill the label fields of the diagnostics dialog

        This will be called once the view is registered
        """
        super(DiagnosticsController, self).register_view(view)

        self.set_device_info()

        self.view.set_appVersion_info(self.model.get_app_version())
        self.view['uptime_number_label'].set_text(self.model.get_uptime())
        self.view['os_name_label'].set_text(self.model.get_os_name())
        self.view['os_version_label'].set_text(self.model.get_os_version())

    def set_device_info(self):
        device = self.model.get_device()
        if not device:
            return

        def sim_imei(sim_data):
            # ok we don't have a model the data is coming from dbus
            # from wader core lets tell the view to set the imsi value
            # in the correct place
            print "diagnostics sim_imei - IMEI number is", sim_data
            self.view.set_imei_info(sim_data)

        device.GetImei(dbus_interface=CRD_INTFACE,
                       error_handler=logger.error, reply_handler=sim_imei)

        def sim_network(sim_data):
            # let's look up what we think this SIM's network is.
            # so we want to display the country and network operator

            sim_network = NetworkProvider()
            networks_attributes = sim_network.get_network_by_id(sim_data)
            if networks_attributes:
                net_attrib = networks_attributes[0]
                print "diagnostics sim_network - country:", net_attrib.country
                print "diagnostics sim_network - network opeartor:", net_attrib.name
                print "diagnostics sim_network - sms value:", net_attrib.smsc
                print "diagnostics sim_network - password value:", net_attrib.password
                self.view.set_network_info(net_attrib.name, net_attrib.country)

        device.GetImsi(dbus_interface=CRD_INTFACE,
                       error_handler=logger.error, reply_handler=sim_network)

        def sim_imsi(sim_data):
            # ok we don't have a model the data is coming from dbus from the
            # core lets tell the view to set the imei in the correct place
            print "diagnostics sim_imsi - IMSI number is", sim_data
            self.view.set_imsi_info(sim_data)

        device.GetImsi(dbus_interface=CRD_INTFACE,
                       error_handler=logger.error, reply_handler=sim_imsi)

        def mdm_info(datacard_info):
            # ok we don't have a model the data is coming straight from
            # our core via dbus
            manufacturer = datacard_info[0]
            model = datacard_info[1]
            firmware = datacard_info[2]
            print "diagnostics mdm_info - manufacturer", manufacturer
            print "diagnostics mdm_info - model", model
            print "diagnostics mdm_info - firmware", firmware

            # XXX: Is this necessary?
            # we need to take into account when cards don't tell us the truth.
            # so for the huawei e172 reporting e17x we add an exception
            if model == 'E17X' and manufacturer == 'huawei':
                model = 'E172'

            self.view.set_datacard__info(manufacturer, model, firmware)

        device.GetInfo(dbus_interface=MDM_INTFACE,
                       error_handler=logger.error, reply_handler=mdm_info)

    # ------------------------------------------------------------ #
    #                       Signals Handling                       #
    # ------------------------------------------------------------ #

    def on_close_button_clicked(self, widget):
        self._hide_myself()

    def on_send_ussd_button_clicked(self, widget):
         device = self.model.get_device()

         # ok when the USSD message button is clicked grab the value from the ussd_message
         # box and save in the model for now.
         print "diagnostics on_send_ussd_button clicked"
         ussd_message = self.view['ussd_entry'].get_text().strip()
         self.view['ussd_entry'].set_text('')
         print "diagnostics on_send_ussd_button_clicked", ussd_message
         # self.model.ussd_message = ussd_message

         device.Initiate(ussd_message,
                         reply_handler=self.view.set_ussd_reply,
                         error_handler=logger.error)

    def _hide_myself(self):
        self.model.unregister_observer(self)
        self.view.hide()