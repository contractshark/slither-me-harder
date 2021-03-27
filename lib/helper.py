# SPDX-License-Identifier: GPL-3.0
# Manticore Helper
import os

from functools import partial
from manticore.core.smtlib import Operators
from manticore.ethereum import ABI, ManticoreEVM
from manticore.platforms.evm import Transaction
from os.path import isdir

# Configure paths here!
NODE_MODULES_LIBS = ['openzeppelin-zos', 'zos-lib', 'openzeppelin-solidity']

BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'HammerHead')
HAMMERHEAD_PATH = os.path.join(BASE_PATH, 'contracts')
MARKET_ORACLE_PATH = os.path.join(BASE_PATH, '..', 'market-oracle', 'contracts')

def init_workspace(test_name, cpus=1):
    workspace = test_name
    assert not isdir(workspace), "Workspace folder already exists"
    m = ManticoreEVM(procs=cpus, workspace_url=workspace)
    m.verbosity(3)
    return m


def finalize(m):
    m.finalize()
    print("[+] Look for results in %s" % m.workspace)


def create_all_contracts(m):
    owner_account = m.create_account(balance=int(1e25))
    print('[*] Created owner account')

    market_source = create_market_source(m, owner_account, symbol='GDAX', value=600)
    market_oracle = create_market_oracle(m, owner_account)

    hammerhead = create_hammerhead(m, owner_account)
    hammerhead_policy = create_hammerhead_policy(m, owner_account, hammerhead)

    return owner_account, market_source, market_oracle, hammerhead, hammerhead_policy


def create_market_source(m, owner_account, symbol: str, value: int):
    """
    Example args: symbol='GDAX', value=600
    """
    ms = _load_contract(m, MARKET_ORACLE_PATH, 'MarketSource', owner=owner_account, args=[symbol, value])
    print('[*] Created MarketSource')
    return ms


def create_market_oracle(m, owner_account):
    mo = _load_contract(m, MARKET_ORACLE_PATH, 'MarketOracle', owner=owner_account)
    print('[*] Created MarketOracle')
    return mo


def create_hammerhead(m, owner_account):
    hammerhead = _load_contract(m, HAMMERHEAD_PATH, 'HammerHead', owner=owner_account)
    hammerhead.initialize(owner_account, signature='(address)')
    print('[*] Created and initialized HammerHead')
    return hammerhead


def create_hammerhead_policy(m, owner_account, hammerhead_account):
    hammerhead_policy = _load_contract(m, HAMMERHEAD_PATH, 'HammerHeadPolicy', owner=owner_account)
    hammerhead_policy.initialize(owner_account, hammerhead_account, signature='(address,address)')
    print('[*] Created and initialized HammerHeadPolicy')
    return hammerhead_policy


def _load_contract(m, path, contract, **kwargs):
    with open(os.path.join(path, f'{contract}.sol')) as f:
        return m.solidity_create_contract(
            f,
            contract_name=contract,
            solc_remaps=[f'{m}={os.path.join(BASE_PATH, "node_modules", m)}' for m in NODE_MODULES_LIBS],
            **kwargs,
        )


def get_return_data(tx):
    assert isinstance(tx, Transaction)
    r = tx.return_data
    if isinstance(r, str):
        r = list(map(ord, r))
    return Operators.CONCAT(256, *r)


def get_calldata_uint_arg(input_symbol, arg_ix=0, bits=256):
    offset = (4 + (arg_ix * 32))
    return ABI._deserialize_uint(input_symbol, bits // 8, offset=offset)
