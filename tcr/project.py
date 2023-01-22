from collections import namedtuple

from tcr.wallet import Wallet
from tcr.project_data import ProjectData
from tcr.policy import Policy
import logging

ProjectSettings = namedtuple('ProjectSettings', ['name', 'policy_name', 'nft_data'])

class Project:
    def __init__(
        self,
        user:ProjectData,
        obj:dict
    ):
        keys = ['name', 'policy_name', 'nft_data']
        settings = {key: obj[key] for key in keys}
        parameters = ProjectSettings(**settings)
        self.user = user
        self.name = parameters.name
        self.policy_name = parameters.policy_name
        self.nft_data = parameters.nft_data
        self.policy = Policy(user, user.get_policy(parameters.policy_name))
        self.network = ProjectData.NetworkLookup[user.get_network().lower()]

    def get_name(self):
        return self.name

    def get_policy_name(self):
        return self.policy_name

    def get_nft_data(self):
        return self.nft_data

    def get_series_number(self):
        if not 'series_number' in self.user.get_project(self.name):
            self.set_series_number(0)

        return self.user.get_project(self.name)['series_number']

    def set_series_number(self, series_number:int):
        self.user.get_project(self.name)['series_number'] = series_number

    def get_initial_id(self):
        if not 'initial_id' in self.user.get_project(self.name):
            self.set_initial_id(0)

        return self.user.get_project(self.name)['initial_id']

    def set_initial_id(self, id:int):
        self.user.get_project(self.name)['initial_id'] = id

    def get_total_nfts(self):
        if not 'total_nfts' in self.user.get_project(self.name):
            self.set_total_nfts(500)

        return self.user.get_project(self.name)['total_nfts']

    def set_total_nfts(self, total:int):
        self.user.get_project(self.name)['total_nfts'] = total

    def get_output_width(self):
        if not 'output_width' in self.user.get_project(self.name):
            self.set_output_width(2048)

        return self.user.get_project(self.name)['output_width']

    def set_output_width(self, width:int):
        self.user.get_project(self.name)['output_width'] = width

    def get_output_height(self):
        if not 'output_height' in self.user.get_project(self.name):
            self.set_output_height(2048)

        return self.user.get_project(self.name)['output_height']

    def set_output_height(self, height:int):
        self.user.get_project(self.name)['output_height'] = height

    def get_token_name(self):
        if not 'token_name' in self.user.get_project(self.name):
            self.set_token_name('')

        return self.user.get_project(self.name)['token_name']

    def set_token_name(self, token_name:str):
        self.user.get_project(self.name)['token_name'] = token_name

    def get_nft_name(self):
        if not 'nft_name' in self.user.get_project(self.name):
            self.set_nft_name('')

        return self.user.get_project(self.name)['nft_name']

    def set_nft_name(self, nft_name:str):
        self.user.get_project(self.name)['nft_name'] = nft_name

    def serialize(self):
        parameters = Project.to_dict(
            name=self.name,
            policy_name=self.policy_name,
            nft_data=self.nft_data
        )
        return parameters

    @staticmethod
    def to_dict(name:str, policy_name:str, nft_data:str, token_name:str) -> dict:
        parameters = dict(
            ProjectSettings(
                name=name,
                policy_name=policy_name,
                nft_data=nft_data,
                token_name = token_name
            )._asdict()
        )
        return parameters

    @staticmethod
    def create_new(
        user:ProjectData,
        name:str,
        policy_name:str,
        nft_data:str
    ):
        parameters = Project.to_dict(
            name=name,
            policy_name=policy_name,
            nft_data=nft_data
        )
        return Project(user, parameters)
