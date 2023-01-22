
import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import time
import threading

from functools import partial

from tcr.project_data import ProjectData
from tcr.configuration import Configuration
from tcr.policy import Policy
from tcr.ui.create_policy_dialog import CreatePolicyDialog
from tcr.ui.royalty_token_dialog import RoyaltyTokenDialog
import blockfrost
from tcr.ui.list_frame import ListFrame

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

        self.add_field(master=self,
                       label='Policy ID:',
                       value=tk.StringVar(value=policy.get_id_str()),
                       row=0)
        self.add_field(master=self,
                       label='Signature Key Hash:',
                       value=tk.StringVar(value=policy.get_signature_key_hash()),
                       row=1)
        self.add_field(master=self,
                       label='Before Slot:',
                       value=tk.StringVar(value=int(policy.get_before_slot())),
                       row=2)
        self.add_field(master=self,
                       label='Signing Wallet:',
                       value=tk.StringVar(value=policy.get_wallet_name()),
                       row=3)
        self.add_field(master=self,
                       label='Royalty Token TX:',
                       value=self.royalty_token_tx_hash,
                       row=4)
        self.add_field(master=self,
                       label='Royalty Address:',
                       value=self.royalty_address,
                       row=5)
        self.add_field(master=self,
                       label='Royalty Percent:',
                       value=self.royalty_percent,
                       row=6)
        self.add_field(master=self,
                       label='NFT Count:',
                       value=self.nft_count,
                       row=7)

        self.rowconfigure(8, weight=1)
        button_frame = ctk.CTkFrame(master=self)
        button_frame.grid(column=0, row=8, padx=5, pady=0, columnspan=2, sticky=tk.SW)

        self.royalty_button = ctk.CTkButton(
            master=button_frame,
            text='Create Royalty Token',
            command=self.create_royalty_token
        )
        self.royalty_button.grid(
            column=0, row=0,
            padx=5, pady=0,
            columnspan=1, sticky=tk.W
        )

        self.burn_button = ctk.CTkButton(
            master=button_frame,
            text='Burn Royalty Token',
            command=self.burn_royalty_token
        )
        self.burn_button.grid(
            column=1, row=0,
            padx=5, pady=0,
            columnspan=1, sticky=tk.W
        )

        self.synchronize_thread = threading.Thread(target=self.synchronize_policy,
                                                   daemon=True)
        self.synchronize_thread.start()

    def add_field(self, master, label:str, value:tk.StringVar, row:int) -> None:
        self.rowconfigure(row, weight=0)
        label = ctk.CTkLabel(master=master, text=label)
        label.grid(column=0, row=row, padx=5, pady=0, sticky=tk.E)

        label = ctk.CTkLabel(master=master, textvariable=value)
        label.grid(column=1, row=row, padx=0, pady=0, sticky=tk.W)

    def get_name(self):
        return self.policy.get_name()

    def burn_royalty_token(self):
        self.node.burn_nft(self.policy, '')

    def create_royalty_token(self):
        if self.royalty_percent.get() != '---' or self.royalty_address.get() != 'Not Set' or self.royalty_token_tx_hash.get() != 'None' or self.nft_count.get() != '0':
            print('already created')
            return

        dialog = RoyaltyTokenDialog(self)
        self.wait_window(dialog)

        if not dialog.is_ok():
            return

        royalty_address = dialog.get_result()['address']
        rate = dialog.get_result()['rate']
        tx_hash = self.node.mint_royalty_token(self.policy, royalty_address, rate)
        self.royalty_percent.set(float(dialog.get_result()['rate'])*100)
        self.royalty_address.set(dialog.get_result()['address'])
        self.nft_count.set('1')
        self.royalty_token_tx_hash.set(tx_hash)

    def synchronize_policy(self):
        policy_id = self.policy.get_id_str()
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

            initialized = True


        while True:
            self.assets = self.node.get_assets(policy_id)
            count = 0
            for asset in self.assets:
                count += int(asset.quantity)
            self.nft_count.set(count)
            time.sleep(60)

class PoliciesFrame(ListFrame):
    def __init__(self, parent, settings:Configuration, user:ProjectData, node):
        super().__init__(parent)
        self.settings = settings
        self.user = user
        self.node = node

    def create_views(self):
        return [PolicyView(self, self.node, self.user, Policy(self.user, obj))
                for obj in self.user.get_policies()]

    def add_item(self):
        if self.current_slot == 0:
            tk.messagebox.showerror('Error', 'Wait for slot to sync')
            return

        dialog = CreatePolicyDialog(self, self.user)
        self.wait_window(dialog)

        if not dialog.is_ok():
            return

        name = dialog.get_result()['name']
        if self.is_view_existing(name) != False:
            tk.messagebox.showerror('Error', 'Duplicate Policy Name')
            return

        wallet = dialog.get_result()['wallet']
        lock_date = dialog.get_result()['lock_date']
        seconds = dialog.get_result()['seconds']
        new_policy = Policy.create_new(self.user,
                                       name, wallet,
                                       before_slot=self.current_slot + seconds)
        self.user.add_policy(new_policy.serialize())
        policy_view = PolicyView(self, self.node, self.user, new_policy)
        return policy_view

    def delete_item(self, name):
        self.user.delete_policy(name)

    def update_current_slot(self, slot:int):
        self.current_slot = slot
