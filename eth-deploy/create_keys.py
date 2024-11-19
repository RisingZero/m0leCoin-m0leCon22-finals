from eth_account import Account
import sys, glob, json, os


def usage():
    print("Usage:\ncreate_keys.py <num_of_teams>")
    print("The keys will be created in the ./keys/ folder, in the ./addresses.json file all accounts addresses will be reported.\
        The general key (pwnthem0le) will be in the 0.key file, each team will have its own key in the form <team#>.key.\
        This script will create keys to reach the number of teams, keeping already created team keys.")


def create_key(team: int):
    print("Creating keys for team " + str(team) + "...")
    account = Account.create(os.urandom(32))
    keyfile = open(f'{team}.key', 'w')
    keyfile.write(account.key.hex())
    keyfile.close()
    return account.address


def main():
    if len(sys.argv) != 2:
        usage()
        exit(1)

    os.chdir('keys')
    n_teams = int(sys.argv[1])
    existing_keys = glob.glob('*.key')
    addresses_json = json.load(open('addresses.json', 'r'))

    if '0.key' not in existing_keys:
        addresses_json[str(0)] = create_key(0)

    if len(existing_keys)  != 0:
        existing_teams = max(list(map(lambda x: int(x.split('.')[0]), existing_keys)))
    else:
        existing_teams = 0

    if existing_teams >= n_teams:
        print("The number of existing teams is higher than the number of teams to be created.")
        exit(1)
    
    offset = existing_teams + 1

    for i in range(offset, n_teams+1):
        addresses_json[str(i)] = create_key(i)

    json.dump(addresses_json, open('addresses.json', 'w'))


if __name__ == '__main__':
    main()
