from slither import Slither
from .declarations.contract import Contract
import re
from definitions import ROOT_DIR
import os


def get_sol_version(dir):
    version = None
    code = open(dir, 'r', encoding='utf-8').read().split('\n')
    for line, content in enumerate(code):
        if 'pragma solidity' in content:
            version = re.findall(r'[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}', content)[0]
    return version


def get_all_solc_versions_linux():
    from os import listdir
    solc_dir = f'{ROOT_DIR}/linux_solc/'
    solc_versions = [f for f in listdir(solc_dir)]
    return solc_versions


def get_all_solc_versions_nt():
    from os import listdir
    from os.path import isdir, join
    solc_dir = f'{ROOT_DIR}/solc/'
    solc_versions = [f for f in listdir(solc_dir) if isdir(join(solc_dir, f))]
    return solc_versions


def get_slither_obj(_dir, solc_path):
    return Slither(_dir, solc=solc_path)


def compile_source(_dir, solc_version=None, solc_path=None):
    if solc_path:
        return get_slither_obj(_dir, solc_path)
    if solc_version:
        if os.name == 'posix':
            return get_slither_obj(_dir, f'{ROOT_DIR}/linux_solc/{solc_version}')
        elif os.name == 'nt':
            return get_slither_obj(_dir, f'{ROOT_DIR}/solc/{solc_version}/solc.exe')
        else:
            raise Exception('Currently executing on a unsupported OS. ')

    if os.name == 'posix':
        return compile_linux(_dir)
    elif os.name == 'nt':
        return compile_nt(_dir)
    else:
        raise Exception('Currently executing on a unsupported OS. ')


def compile_nt(_dir):
    solc_version = get_sol_version(_dir)
    all_sol_versions = get_all_solc_versions_nt()
    if solc_version:
        if solc_version in all_sol_versions:
            all_sol_versions.remove(solc_version)
            all_sol_versions.insert(0, solc_version)
    for version in all_sol_versions:
        try:
            return get_slither_obj(_dir, f'{ROOT_DIR}/solc/{version}/solc.exe')
        except:
            pass
    raise Exception(f'Existing solidity compilers do not work on "{_dir}", please try to provide your own solc '
                    f'compiler using --solc_path')


def compile_linux(_dir):
    solc_version = get_sol_version(_dir)
    all_sol_versions = get_all_solc_versions_linux()
    if solc_version:
        if solc_version in all_sol_versions:
            all_sol_versions.remove(solc_version)
            all_sol_versions.insert(0, solc_version)
    for version in all_sol_versions:
        try:
            return get_slither_obj(_dir, f'{ROOT_DIR}/linux_solc/{version}/solc')
        except:
            pass
    raise Exception(f'Existing solidity compilers do not work on "{_dir}", please try to provide your own solc '
                    f'compiler using --solc_path')


class Contracts:
    def __init__(self, _dir: str, solc_version: str, solc_path: str):
        self.contracts = {}
        slither = compile_source(_dir, solc_version, solc_path)
        for contract in slither.contracts:
            new_contract = Contract(contract)
            self.contracts[contract.name] = new_contract

    def get_contract_by_name(self, _name: str):
        return self.contracts.get(_name)

