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

"""
File: command.py
Author: SuperKK
"""

from typing import List
import subprocess
import os
import logging
import tempfile

networks = {
    'testnet': ['--testnet-magic', '1097911063'],
    'mainnet': ['--mainnet']
}

node_socket_env = {
    'testnet': 'TESTNET_CARDANO_NODE_SOCKET_PATH',
    'mainnet': 'MAINNET_CARDANO_NODE_SOCKET_PATH',
    'active': 'CARDANO_NODE_SOCKET_PATH'
}

logger = logging.getLogger('command')

class TempFile:
    """
    Create temporary files using the 'with' statement to ensure they get removed
    after use.  Supporting two main use cases:

    1.  Initialize a temporary file with content for use as input to a command
        with TempFile(initial_content) as initial_content_file:
            result = run_command(initial_content_file.name)
            ...

    2.  Retrieve output from a command that writes to file
        with TempFile() as output_file:
            write_somethign_to(output_file.name)
            result = output_file.read()
            ...
    """
    def __init__(self, content:str=None):
        self.name = tempfile.TemporaryFile().name
        if content != None:
            with open(self.name, 'w') as file:
                file.write(content)

    def read(self) -> str:
        with open(self.name, 'r') as file:
            return file.read()

    def __str__(self):
        return self.name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.remove(self.name)
        self.name=None

class Command:
    """
    Utility methods to run cardano commands.

    Sets the environment variables based on which network is being used.
    Valid networks are 'testnet' and 'mainnet' defined in the networks
    dictionary object above.
    """

    @staticmethod
    def write_to_file(filename, data):
        """
        Write a string of data to the given filename.
        """

        with open(filename, 'w') as file:
            file.write(data)

    @staticmethod
    def print_command(command):
        """
        Prints a command list.
        """
        cmdstr = 'Command: '

        for c in command:
            if ' ' not in c:
                cmdstr += '{} '.format(c)
            else:
                cmdstr += '\"{}\" '.format(c)

        logger.debug(cmdstr)

    @staticmethod
    def run_generic(command: List[str]):
        Command.print_command(command)

        try:
            completed = subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.error('{}, return code: {}'.format(command[0], e.returncode))
            logger.error('output: {}'.format(e.output))
            logger.error('stdout: {}'.format(e.stdout))
            logger.error('stderr: {}'.format(e.stderr))
            raise e

        return completed.stdout.strip('\r\n')

    @staticmethod
    def run(command:List[str], network:str, input:str=None):
        """
        Run the specified command.

        @param command A list.  The command followed by command line parameters.  Each
                       should be a string.
        @param network One of the values defined in the networks dictionary object above.
        @param input A string of input to pass to the command process if needed.
        """

        envvars = os.environ

        if network != None:
            envvars[node_socket_env['active']] = os.environ[node_socket_env[network]]
            command.extend(networks[network])

        Command.print_command(command)
        if input != None:
            logger.debug('\tinput: {}'.format(input))
        else:
            logger.debug('\tinput: None')
        try:
            completed = subprocess.run(command, check=True, capture_output=True, text=True, input=input, env=envvars)
        except subprocess.CalledProcessError as e:
            logger.error('{}, return code: {}'.format(command[0], e.returncode))
            logger.error('output: {}'.format(e.output))
            logger.error('stdout: {}'.format(e.stdout))
            logger.error('stderr: {}'.format(e.stderr))
            raise e

        return completed.stdout.strip('\r\n')
