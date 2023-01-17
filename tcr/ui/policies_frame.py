
import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import time
import threading
import json

from functools import partial

from tcr.wallet import Wallet
from tcr.project_data import ProjectData
from tcr.configuration import Configuration
from tcr.policy import Policy
from tcr.ui.create_policy_dialog import CreatePolicyDialog
from tcr.ui.royalty_token_dialog import RoyaltyTokenDialog
from tcr.command import TempFile
import blockfrost

class PolicyView(ctk.CTkFrame):
    def __init__(self, parent, node, user:ProjectData, policy:Policy):
        ctk.CTkFrame.__init__(self, parent)

        self.node = node
        self.user = user
        self.policy = policy
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.royalty_token_tx_hash = tk.StringVar()
        self.royalty_address = tk.StringVar()
        self.royalty_percent = tk.StringVar()
        self.nft_count = tk.StringVar()

        self.add_field(master=self, label='Policy ID:',
                                    value=tk.StringVar(value=policy.get_id()),
                                    row=0)
        self.add_field(master=self, label='Signature Key Hash:',
                                    value=tk.StringVar(value=policy.get_signature_key_hash()),
                                    row=1)
        self.add_field(master=self, label='Before Slot:',
                                    value=tk.StringVar(value=int(policy.get_before_slot())),
                                    row=2)
        self.add_field(master=self, label='Signing Wallet:',
                                    value=tk.StringVar(value=policy.get_wallet()),
                                    row=3)
        self.add_field(master=self, label='Royalty Token TX:',
                                    value=self.royalty_token_tx_hash,
                                    row=4)
        self.add_field(master=self, label='Royalty Address:',
                                    value=self.royalty_address,
                                    row=5)
        self.add_field(master=self, label='Royalty Percent:',
                                    value=self.royalty_percent,
                                    row=6)
        self.add_field(master=self, label='NFT Count:',
                                    value=self.nft_count,
                                    row=7)

        self.royalty_button = ctk.CTkButton(master=self, text='Create Royalty Token', command=self.create_royalty_token)
        self.royalty_button.grid(column=0, row=8, padx=5, pady=0, columnspan=2, sticky=tk.W)

        self.synchronize_thread = threading.Thread(target=self.synchronize_policy,
                                                   daemon=True)
        self.synchronize_thread.start()

    def add_field(self, master, label:str, value:tk.StringVar, row:int) -> None:
        self.rowconfigure(row, weight=0)
        label = ctk.CTkLabel(master=master, text=label)
        label.grid(column=0, row=row, padx=5, pady=0, sticky=tk.E)

        label = ctk.CTkLabel(master=self, textvariable=value)
        label.grid(column=1, row=row, padx=0, pady=0, sticky=tk.W)

    def get_name(self):
        return self.policy.get_name()

    def create_royalty_token(self):
        if self.royalty_percent.get() != '---' or self.royalty_address.get() != 'Not Set' or self.royalty_token_tx_hash.get() != 'None' or self.nft_count.get() != '0':
            print('already created')
            return

        dialog = RoyaltyTokenDialog(self)
        self.wait_window(dialog)

        if not dialog.is_ok():
            return

        signing_wallet = Wallet(self.user.get_network(), self.user.get_wallet(self.policy.get_wallet()))
        #self.node.transfer_ada(signing_wallet,
        #                       'addr_test1qrdxjwwuaep8948c3sqvul47nhtg5nxgqc7wlahwmwqplelft0q70npx8e22rv02jedp8ztmjscqv04dw6pvuerfmnmq2cn5zn',
        #                       1500000)

        royalty_address = dialog.get_result()['address']
        rate = dialog.get_result()['rate']
        tx_hash = self.node.mint_royalty_token(self.policy, signing_wallet, royalty_address, rate)
        print(f'Royalty Mint TX Hash = {tx_hash}')
        self.royalty_percent.set(float(dialog.get_result()['percent'])*100)
        self.royalty_address.set(dialog.get_result()['address'])
        self.nft_count.set('1')
        self.royalty_token_tx_hash.set(tx_hash)

    def synchronize_policy(self):
        policy_id = self.policy.get_id()
        initialized = False

        while not initialized:
            history = None
            try:
                history = self.node.get_asset_history(policy_id, '')
                for item in history:
                    if item.action == 'minted' and int(item.amount) == 1:
                        tx_hash = item.tx_hash
                        self.royalty_token_tx_hash.set(tx_hash)
                        metadata = self.node.get_transaction_metadata(tx_hash)
                        for data in metadata:
                            if data.label == '777':
                                address = ''
                                for part in data.json_metadata.addr:
                                    address += part
                                if hasattr(data.json_metadata, 'pct'):
                                    self.royalty_percent.set(float(data.json_metadata.pct)*100)
                                if hasattr(data.json_metadata, 'rate'):
                                    self.royalty_percent.set(float(data.json_metadata.rate)*100)
                                self.royalty_address.set(address)
            except blockfrost.utils.ApiError as ae:
                if ae.status_code == 404:
                    initialized = True
                    self.royalty_token_tx_hash.set('None')
                    self.royalty_address.set('Not Set')
                    self.royalty_percent.set('---')

            self.assets = self.node.get_assets(policy_id)
            self.nft_count.set(len(self.assets))

            initialized = True


        while True:
            time.sleep(120)

class PoliciesFrame(ctk.CTkFrame):
    def show_policy(self, name):
        for view in self.policy_views:
            view.grid_forget()
            if view.get_name() == name:
                view.grid(column=1, row=0, padx=0, pady=0, sticky=tk.NSEW)

    def policy_selected_event(self, lb, arg):
        if len(lb.curselection()) == 0:
            return

        name = lb.get(lb.curselection()[0])
        self.show_policy(name)

    def create_policy_list(self, parent):
        frame = ctk.CTkFrame(master=parent)

        lb = tk.Listbox(master=frame, selectmode=tk.SINGLE)
        for view in self.policy_views:
            self.count += 1
            lb.insert(self.count, view.get_name())

        lb.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NS)
        frame.rowconfigure(index=0, weight=1)

        lb.bind('<<ListboxSelect>>', partial(self.policy_selected_event, lb))

        button_frame = ctk.CTkFrame(master=frame)
        delete_button = ctk.CTkButton(master=button_frame, text='-', width=28, height=28, command=partial(self.delete_policy, lb))
        add_button = ctk.CTkButton(master=button_frame, text='+', width=28, height=28, command=partial(self.add_policy, lb))
        delete_button.grid(column=0, row=0, padx=0, pady=0)
        add_button.grid(column=1, row=0, padx=0, pady=0)
        button_frame.grid(column=0, row=1, padx=0, pady=0, sticky=tk.E)

        return frame

    def __init__(self, parent, settings:Configuration, user:ProjectData, node):
        ctk.CTkFrame.__init__(self, parent)

        self.settings = settings
        self.user = user
        self.node = node
        self.count = 0
        self.current_slot = 0
        self.policy_views = [PolicyView(self, self.node, self.user, Policy(self.user.get_network(), obj)) for obj in self.user.get_policies()]

        self.columnconfigure(index=0, weight=0)
        self.rowconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=1)

        left_frame = self.create_policy_list(self)
        left_frame.grid(column=0, row=0, padx=0, pady=0, sticky=tk.NS)

        if len(self.policy_views) == 0:
            right_frame = ctk.CTkFrame(self)
        else:
            right_frame = self.policy_views[0]
        right_frame.grid(column=1, row=0, padx=0, pady=0, sticky=tk.NSEW)

    def update_current_slot(self, slot:int):
        self.current_slot = slot

    def delete_policy(self, lb:tk.Listbox):
        if len(lb.curselection()) == 0:
            return

        name = lb.get(lb.curselection()[0])
        print(f'name = {name}')
        lb.delete(lb.curselection()[0])
        for view in self.policy_views:
            view.grid_remove()
            if view.get_name() == name:
                self.policy_views.remove(view)
        self.user.delete_policy(name)

        lb.select_set(0)
        if len(self.policy_views) > 0:
            self.show_policy(self.policy_views[0].get_name())

    def add_policy(self, lb:tk.Listbox):
        if self.current_slot == 0:
            tk.messagebox.showerror('Error', 'Wait for slot to sync')
            return

        dialog = CreatePolicyDialog(self, self.user)
        self.wait_window(dialog)

        if not dialog.is_ok():
            return

        name = dialog.get_result()['name']
        wallet = dialog.get_result()['wallet']
        lock_date = dialog.get_result()['lock_date']
        seconds = dialog.get_result()['seconds']

        if len(name) > 0:
            for view in self.policy_views:
                if view.get_name() == name:
                    tk.messagebox.showerror('Error', 'Duplicate Policy Name')
                    return

            new_policy = Policy.create_new(self.user.get_network(),
                                           name, wallet,
                                           before_slot=self.current_slot + seconds)
            self.policy_views.append(PolicyView(self, self.node, self.user, new_policy))
            self.count += 1
            lb.insert(self.count, new_policy.get_name())
            self.user.add_policy(new_policy.serialize())
            lb.select_set(self.count-1)

            self.show_policy(name)
