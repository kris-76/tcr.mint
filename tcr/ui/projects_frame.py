
import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import time
import threading
import json

from functools import partial

from tcr.wallet import Wallet
from tcr.project_data import ProjectData
from tcr.project import Project
from tcr.command import TempFile
from tcr.ui.create_project_dialog import CreateProjectDialog
from tcr.ui.define_nfts_dialog import DefineNftsDialog
from tcr.ui.list_frame import ListFrame
import blockfrost
"""
    "output-width": 1200,
    "output-height": 1680,
    "max_per_tx": 25,
    "prices": {
        "35000000": 1,
        "70000000": 2,
        "105000000": 3,
        "130000000": 4,
        "260000000": 8,
        "300000000": 10,
        "600000000": 20
    },
    "presale": {
        "30000000": 1,
        "60000000": 2,
        "90000000": 3,
        "110000000": 4
    },
"""
class ProjectView(ctk.CTkFrame):
    def __init__(self, parent, project:Project):
        ctk.CTkFrame.__init__(self, parent)

        self.project = project
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=1)

        try:
            with open(project.get_nft_data(), 'r') as file:
                self.data = json.loads(file.read())
        except FileNotFoundError as fnfe:
            self.data = {'definitions': []}
        print(json.dumps(self.data, indent=4))

        def add_field(master, label:str, value:tk.StringVar, row:int, column:int) -> None:
            master.rowconfigure(row, weight=0)
            label = ctk.CTkLabel(master=master, text=label)
            label.grid(column=column, row=row, padx=5, pady=0, sticky=tk.E)

            label = ctk.CTkLabel(master=master, textvariable=value)
            label.grid(column=column+1, row=row, padx=0, pady=0, sticky=tk.W)

        add_field(master=self,
                  label='Project:',
                  value=tk.StringVar(value=project.get_name()),
                  row=0, column=0)
        add_field(master=self,
                  label='Policy:',
                  value=tk.StringVar(value=project.get_policy_name()),
                  row=0, column=2)
        add_field(master=self,
                  label='NFT Data:',
                  value=tk.StringVar(value=project.get_nft_data()),
                  row=0, column=4)

        self.rowconfigure(1, weight=1)
        frame = ctk.CTkFrame(master=self)
        frame.grid(row=1, column=0, columnspan=6, padx=0, pady=0, sticky=tk.NSEW)


        def field_changed(var_name:str, var_index:str, operation:str, val, fxn):
            try:
                fxn(val.get())
            except:
                pass

        def add_int_setting(master, row:int, column:int, label:str, max:int, value:int, set_fxn):
            iv = tk.IntVar(value=value)
            iv.trace_add('write', partial(field_changed, val=iv, fxn=set_fxn))
            label = ctk.CTkLabel(master=master, text=label)
            label.grid(row=row, column=column,  padx=5, pady=0, sticky=tk.E)
            value = tk.Spinbox(master=master, from_=0, to=max, textvariable=iv, font='lucida 30')
            value.grid(row=row, column=column+1, sticky=tk.EW, padx=0, pady=5)

        def add_str_setting(master, row:int, column:int, label:str, value:str, set_fxn):
            sv = tk.StringVar(value=value)
            sv.trace_add('write', partial(field_changed, val=sv, fxn=set_fxn))
            label = ctk.CTkLabel(master=master, text=label)
            label.grid(row=row, column=column,  padx=5, pady=0, sticky=tk.E)
            value = ctk.CTkEntry(master=master, width=100, textvariable=sv)
            value.grid(row=row, column=column+1, sticky=tk.EW, padx=0, pady=5)

        add_int_setting(master=frame, row=0, column=0, label='Series Number:', max=100,
                        value=self.project.get_series_number(),
                        set_fxn=self.project.set_series_number)
        add_int_setting(master=frame, row=1, column=0, label='Initial ID:', max=1000000,
                        value=self.project.get_initial_id(),
                        set_fxn=self.project.set_initial_id)
        add_int_setting(master=frame, row=2, column=0, label='Total NFTs:', max=20000,
                        value=self.project.get_total_nfts(),
                        set_fxn=self.project.set_total_nfts)
        add_int_setting(master=frame, row=3, column=0, label='Output Width:', max=8192,
                        value=self.project.get_output_width(),
                        set_fxn=self.project.set_output_width)
        add_int_setting(master=frame, row=4, column=0, label='Output Height:', max=8192,
                        value=self.project.get_output_height(),
                        set_fxn=self.project.set_output_height)
        add_str_setting(master=frame, row=5, column=0, label='Token Name:',
                        value=self.project.get_token_name(),
                        set_fxn=self.project.set_token_name)
        add_str_setting(master=frame, row=6, column=0, label='NFT Name:',
                        value=self.project.get_nft_name(),
                        set_fxn=self.project.set_nft_name)

        self.rowconfigure(2, weight=0)
        button_frame = ctk.CTkFrame(master=self)
        button_frame.grid(column=0, row=2,
                          padx=5, pady=0,
                          columnspan=6, sticky=tk.SW)

        nfts_button = ctk.CTkButton(master=button_frame,
                                    text='NFTs',
                                    command=self.define_nfts)
        nfts_button.grid(column=0, row=0,
                         padx=5, pady=0,
                         columnspan=1, sticky=tk.W)

        view_button = ctk.CTkButton(master=button_frame,
                                    text='View',
                                    command=self.view_nfts)
        view_button.grid(column=1, row=0,
                         padx=5, pady=0,
                         columnspan=1, sticky=tk.W)

        view_button = ctk.CTkButton(master=button_frame,
                                    text='Upload',
                                    command=self.upload_nfts)
        view_button.grid(column=2, row=0,
                         padx=5, pady=0,
                         columnspan=1, sticky=tk.W)

        view_button = ctk.CTkButton(master=button_frame,
                                    text='Vend',
                                    command=self.vend_nfts)
        view_button.grid(column=3, row=0,
                         padx=5, pady=0,
                         columnspan=1, sticky=tk.W)

    def get_name(self):
        return self.project.get_name()

    def define_nfts(self):
        dialog = DefineNftsDialog(self,
                                  'Define NFTs',
                                  self.project.get_nft_data(),
                                  self.data)
        self.wait_window(dialog)
        with open(self.project.get_nft_data(), 'w') as file:
            file.write(json.dumps(self.data, indent=4))

    def view_nfts(self):
        pass

    def upload_nfts(self):
        pass

    def vend_nfts(self):
        pass

class ProjectsFrame(ListFrame):
    def __init__(self, parent, user:ProjectData):
        super().__init__(parent)

        self.user = user

    def create_views(self):
        return [ProjectView(self, Project(self.user, obj))
                for obj in self.user.get_projects()]

    def add_item(self):
        dialog = CreateProjectDialog(self, self.user)
        self.wait_window(dialog)

        if not dialog.is_ok():
            return

        name = dialog.get_result()['name']
        if self.is_view_existing(name):
            tk.messagebox.showerror('Error', 'Duplicate Project Name')
            return

        policy = dialog.get_result()['policy']
        nft_data = dialog.get_result()['nft_data']
        new_project = Project.create_new(self.user, name, policy, nft_data)
        view = ProjectView(self, new_project)
        return view

    def delete_item(self, name):
        self.user.delete_project(name)
