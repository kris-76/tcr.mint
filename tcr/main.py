#
# Copyright 2021-2023 The Card Room
#
# MIT License:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import threading
import time
import traceback
import os
import threading

from functools import *
from tkinter import *
from tkinter import ttk
import customtkinter as ctk


from tcr.block_frost_node import BlockFrostNode
from tcr.project_data import ProjectData
from tcr.configuration import Configuration
from tcr.ui.gui_main import GuiMain
from tcr.ui.edit_configuration_dialog import EditConfigurationDialog

def update_status_thread(node, application: GuiMain):
    while True:
        status = node.get_status()
        timestamp = int(time.time())
        #print(f'    Healthy = {status.is_healthy}')
        #print(f'     Height = {status.height}')
        #print(f'   Tip Slot = {status.slot}')
        #print(f'Server Time = {int(status.server_time/1000)}')
        #print(f' Local Time = {timestamp}')
        application.update_status(healthy=status.is_healthy, slot=status.slot)
        time.sleep(15)

def main():
    settings = Configuration('settings.json')
    if len(settings.get_blockfrost_node_project_id()) == 0 or len(settings.get_data_file()) == 0:
        app = ctk.CTk()
        dialog_box = EditConfigurationDialog(app, settings)
        app.wait_window(dialog_box)
        settings.save()
        user = ProjectData(settings.get_data_file(), settings.get_blockfrost_node_project_id())
        user.set_network(dialog_box.get_network())
        user.save()

    user = ProjectData(settings.get_data_file(), settings.get_blockfrost_node_project_id())
    node = BlockFrostNode(user.get_network(), settings.get_blockfrost_node_project_id())
    application = GuiMain(settings, user, node)
    status_thread = threading.Thread(target=update_status_thread,
                                     args=(node, application),
                                     daemon=True)

    status_thread.start()
    application.mainloop()
    user.save()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('')
        print('')
        print('EXCEPTION: {}'.format(e))
        print('')
        traceback.print_exc()
