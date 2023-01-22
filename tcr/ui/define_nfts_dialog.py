import tkinter as tk
import customtkinter as ctk
from tkcalendar import Calendar
from functools import partial
import json

from tcr.ui.list_frame import ListFrame
from tcr.ui.create_nft_definition_dialog import CreateNftDefinitionDialog

class NftView(ctk.CTkFrame):
    def __init__(self, parent, name:str, definition:dict):
        ctk.CTkFrame.__init__(self, parent)
        self.name = name
        self.definition = definition

        self.add_field(master=self,
                       label='Name:',
                       value=tk.StringVar(value=name),
                       row=0)
        self.add_field(master=self,
                       label='Type:',
                       value=tk.StringVar(value=f"{definition['type']}"),
                       row=1)

    def get_name(self):
        return self.name

    def add_field(self, master, label:str, value:tk.StringVar, row:int) -> None:
        self.rowconfigure(row, weight=0)
        label = ctk.CTkLabel(master=master, text=label)
        label.grid(column=0, row=row, padx=5, pady=0, sticky=tk.E)

        label = ctk.CTkLabel(master=master, textvariable=value)
        label.grid(column=1, row=row, padx=0, pady=0, sticky=tk.W)

class DefineNftsDialog(ctk.CTkToplevel):
    def __init__(self, parent, title:str, nft_data:str, data:dict):
        ctk.CTkToplevel.__init__(self, parent)
        self.title(title)
        self.nft_data = nft_data
        self.data = data
        self.grab_set() # makes it modal

        self.rowconfigure(index=0, weight=0)
        self.rowconfigure(index=1, weight=1)
        self.columnconfigure(index=0, weight=0)
        self.columnconfigure(index=1, weight=1)

        label = ctk.CTkLabel(master=self, text='NFT Data File:')
        label.grid(row=0, column=0, padx=5, pady=0, sticky=tk.W)

        label = ctk.CTkLabel(master=self, text=self.nft_data)
        label.grid(row=0, column=1, padx=0, pady=0, sticky=tk.W)

        self.list = ListFrame(self)
        self.list.add_item = self.add_item
        self.list.delete_item = self.delete_item
        self.list.create_views = self.create_views
        self.list.grid(row=1, column=0, columnspan=2,
                       padx=0, pady=0, sticky=tk.NSEW)

    def add_item(self):
        dialog = CreateNftDefinitionDialog(self)
        self.wait_window(dialog)

        if not dialog.is_ok():
            return

        name = dialog.get_result()['name']
        if self.list.is_view_existing(name):
            tk.messagebox.showerror('Error', 'Duplicate NFT Definition')
            return

        type = dialog.get_result()['type']
        definition = {'name': name, 'type': type}
        self.data['definitions'].append(definition)
        return NftView(self.list, name, definition)

    def delete_item(self, name:str):
        for item in self.data['definitions']:
            if name == item['name']:
                self.data['definitions'].remove(item)

    def create_views(self):
        return [NftView(self.list, obj['name'], obj)
                for obj in self.data['definitions']]
