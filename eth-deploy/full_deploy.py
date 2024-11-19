from web3.middleware import geth_poa_middleware,construct_sign_and_send_raw_middleware
from web3 import Web3, HTTPProvider
from eth_account import Account
from solcx import compile_source, install_solc, set_solc_version
import json, string, random
from pwn import *

NUM_TEAMS = 12
CONTRACTS_FOLDER = "../service//m0lecoin-eth-contracts/contracts"

acc_addresses = json.load(open('./keys/addresses.json', 'r'))

def get_random_string(n):
    alph = string.ascii_letters + string.digits
    return "".join(random.choice(alph) for _ in range(n))


def get_account_data(team: int):
    keyfile = open(f'keys/{team}.key', 'r')
    account = Account.from_key(keyfile.read())
    keyfile.close()
    if not account.address == acc_addresses[str(team)]:
        print("Addresses not matching: {} and {}".format(account.address, acc_addresses[str(team)]))
        exit(1)
    return account.address, account.key.hex()

def abi_compile(contract_name: str):
    srcfile = open(f'{CONTRACTS_FOLDER}/{contract_name}.sol', 'r')
    src = srcfile.read()
    srcfile.close()
    os.chdir(CONTRACTS_FOLDER)
    set_solc_version('0.8.13')
    compiled = compile_source(src, output_values=['abi'])
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # retrieve the contract interface
    contract_id, contract_interface = list(compiled.items())[0]
    # get abi
    abi = contract_interface['abi']
    with open(f'abis/{contract_name}.abi', 'w') as abi_file:
        json.dump(abi, abi_file)
    return abi


def deploy_contract(contract_name: str, team, w3, save_abi=False, constructor_params=None):
    srcfile = open(f'{CONTRACTS_FOLDER}/{contract_name}.sol', 'r')
    src = srcfile.read()
    srcfile.close()
    os.chdir(CONTRACTS_FOLDER)
    set_solc_version('0.8.13')
    compiled = compile_source(src, output_values=['abi', 'bin'])
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # retrieve the contract interface
    contract_id, contract_interface = list(compiled.items())[0]
    # get bytecode / bin
    bytecode = contract_interface["bin"]
    # get abix
    abi = contract_interface['abi']
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    if save_abi:
        with open(f'abis/{contract_name}.abi', 'w') as abi_file:
            json.dump(abi, abi_file)

    address, privatekey = get_account_data(team)

    if constructor_params is None:
        tx = Contract.constructor().buildTransaction(
            {
                "gasPrice": w3.eth.gas_price,
                "from": address,
                "nonce": w3.eth.get_transaction_count(address),
            }
        )
    else:
        tx = Contract.constructor(constructor_params).buildTransaction(
            {
                "gasPrice": w3.eth.gas_price,
                "from": address,
                "nonce": w3.eth.get_transaction_count(address),
            }
        )
    tx_signed = w3.eth.account.sign_transaction(tx, private_key=privatekey)
    tx_hash = w3.eth.send_raw_transaction(tx_signed.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return (tx_receipt['contractAddress'], abi)


def main():
    deploy_stats = {}
    # per team deploy of bank (proxy+impl) and shop (proxy+impl) and token contracts
    abi_compile('Im0leCoin')
    bank_abi = abi_compile('IM0leBank')
    shop_abi = abi_compile('IM0leShop')
    log.info('Saved user interfaces in abis/ folder')
    proxy_abi = abi_compile('Proxy')
    for team in range(NUM_TEAMS):
        WEB3_PROVIDER = F"http://10.10.0.4:{8545+team}"
        w3 = Web3(HTTPProvider(WEB3_PROVIDER))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        if not w3.isConnected():
            print("ERROR: Web3 is not connected")
            exit(1)
        log.info(f"--- Started deploying team #{team} at chain {WEB3_PROVIDER} ---")
        deploy_stats[str(team)] = {}
        team_addr, team_key = get_account_data(team)
        deploy_stats[str(team)]['addr_owner'] = team_addr

        # m0leCoin
        m0leCoin_address, m0leCoin_admin_interface = deploy_contract('m0leCoin', team, w3)        
        log.success('m0leCoin #%i deployed at address %s' % (team, m0leCoin_address))
        m0leCoin_contract = w3.eth.contract(address=m0leCoin_address, abi=m0leCoin_admin_interface)
        # Check if is contract is working
        if m0leCoin_contract.functions.getBalance().call({"from": team_addr}) != 10000:
            log.error('m0leCoin contract is NOT working')
            exit(1)
        log.success('m0leCoin contract is working')
        deploy_stats[str(team)]['token'] = m0leCoin_address

        def txs_details(from_addr):
            return {
            "from": from_addr,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(from_addr)
        }

        def signTxAndSend(tx, private_key):
            tx_signed = w3.eth.account.sign_transaction(tx, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(tx_signed.rawTransaction)
            result = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert result['status'] == 1

        # Bank proxy
        bank_proxy_addr, _ = deploy_contract('Proxy', team, w3, constructor_params=m0leCoin_address)
        log.info(f'Proxy bank #{team} deployed at address {bank_proxy_addr}')
        deploy_stats[str(team)]['bank'] = bank_proxy_addr
        # Proxy bank registration in m0leCoin
        tx = m0leCoin_contract.functions.registerBank(bank_proxy_addr).buildTransaction(txs_details(team_addr))
        signTxAndSend(tx, team_key)
        # Bank implementation
        bank_impl_addr, _ = deploy_contract('M0leBank', team, w3, constructor_params=m0leCoin_address)
        log.info(f'Impl bank #{team} deployed at address {bank_impl_addr}')
        bank_contract = w3.eth.contract(address=bank_proxy_addr, abi=proxy_abi)
        tx = bank_contract.functions.upgradeLogic(bank_impl_addr).buildTransaction(txs_details(team_addr))
        signTxAndSend(tx, team_key)
        log.info(f'Bank logic #{team} updated')
        log.info(f'Bank owner #{team} is {team_addr}')

        # Shop proxy
        shop_proxy_addr, _ = deploy_contract('Proxy', team, w3, constructor_params=m0leCoin_address)
        log.info(f'Proxy shop #{team} deployed at address {shop_proxy_addr}')
        deploy_stats[str(team)]['shop'] = shop_proxy_addr
        # Proxy shop registration in m0leCoin
        tx = m0leCoin_contract.functions.registerShop(shop_proxy_addr).buildTransaction(txs_details(team_addr))
        signTxAndSend(tx, team_key)
        # Shop implementation
        shop_impl_addr, _ = deploy_contract('M0leShop', team, w3, constructor_params=m0leCoin_address)
        log.info(f'Impl shop #{team} deployed at address {shop_impl_addr}')
        shop_contract = w3.eth.contract(address=shop_proxy_addr, abi=proxy_abi)
        tx = shop_contract.functions.upgradeLogic(shop_impl_addr).buildTransaction(txs_details(team_addr))
        signTxAndSend(tx, team_key)
        log.info(f'Shop logic #{team} updated')
        log.info(f'Shop owner #{team} is {team_addr}')

        log.success(f'Deployed team #{team}')

    with open('deploy_stats.json', 'w') as stats_file:
        json.dump(deploy_stats, stats_file, indent=4)
    with open('template.env', 'r') as f:
        template_env = f.read()

    for team_id, team_stats in deploy_stats.items():
        env = template_env
        env = env.replace('{{token_contract}}', team_stats['token'])
        env = env.replace('{{shop_contract}}', team_stats['shop'])
        env = env.replace('{{bank_contract}}', team_stats['bank'])
        env = env.replace('{{secret_key}}', get_random_string(24))
        env = env.replace('{{mysql_password}}', get_random_string(24))
        env = env.replace('{{mysql_root_password}}', get_random_string(24))
        env = env.replace('{{team_number}}', team_id)
        env = env.replace('{{chain_port}}', str(8545+int(team_id)))


        with open(f'envs/{team_id}.env', 'w') as team_env:
            team_env.write(env)

if __name__ == '__main__':
    main()
