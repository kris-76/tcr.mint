# Copyright 2021-2022 The Card Room
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

import json

class Configuration():
    def __init__(self, filename):
        self.filename = filename
        try:
            with open(filename, "r") as file:
                self.settings = json.load(file)
        except FileNotFoundError as fne:
            self.settings = {}
            self.settings['blockfrost_node_project_id'] = ''
            self.settings['data_file'] = ''

    def save(self):
        with open(self.filename, 'w') as file:
            file.write(json.dumps(self.settings, indent=4))

    def get_blockfrost_node_project_id(self) -> str:
        if 'blockfrost_node_project_id' not in self.settings:
            self.settings['blockfrost_node_project_id'] = ''
        return self.settings['blockfrost_node_project_id']

    def set_blockfrost_node_project_id(self, id:str) -> None:
        self.settings['blockfrost_node_project_id'] = id

    def get_data_file(self) -> str:
        if 'data_file' not in self.settings:
            self.settings['data_file'] = ''
        return self.settings['data_file']

    def set_data_file(self, file:str) -> str:
        self.settings['data_file'] = file
