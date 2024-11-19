# m0leCoin - m0leCon Finals 2022

_Author: Andrea Angelo Raineri <@Rising>_


**m0leCoin** was one of the challenges released at the _m0leCon Finals 2022 CTF_, hosted by team _pwnthem0le_ at Politecnico di Torino. The challenge contained 2 different flagstores, one for each vulnerability hidden in the service

[Screenshots](#screenshots)

## Challenge Description

### Flagstore 1: Ethereum smart contract re-entrancy

The challenge is centered around the custom ERC-20 token _m0leCoin_. Players are required to use the MetaMask wallet to perform actual transaction using such coin, interacting with the following smart contracts:

- **m0leCoin**: ERC-20 compliant token
- **M0leBank**: Bank contract, allowing users to open an account on the bank (granting them 10 free tokens), make deposits and withdraws
- **M0leShop**: E-Commerce where users can buy and sell items (i.e. "messages"). The shop feature is supported by the backend application, where shop items are actually being stored. Users are considered as legitimate buyers of an item when a buy event from the `M0leShop` contract associated to that users can be found on the blockchain

The checksystem is putting flags on sale for very high amounts of tokens. Users should exploit the application to increment the number of available tokens and be allowed to buy the flag.

#### Solution

The exploitable vulnerability is hidden in the `withdraw()` function of the `M0leBank` contract. The `m0leCoin` ecosystem has been structured in such a way that on each token transfer a callback function is triggered on the receiver, when the receiver is a smart contract itself.

On `withdraw()` the contract is setting the user balance to 0 after the callback is trigger on the receiver, thus exposing the function to the **re-entrancy** vulnerability. An attacker is able to deploy a smart contract implementing the `ITokenReceiver` interfacing, with a re-entrant call to `withdraw()` in the `tokensReceived()` function. The `witthdraw()` function is going to be called in loop untilthe required amount of token is available to buy the flag on the shop.

NOTE: the `M0leBank` contract does not have an internal pool of tokens, allowing the attack to actually "create" new tokens on `withdraw()`

### Flagstore 2: HMAC with hashed key

The second place where flags are stored is in the "material product" section. These items do not require to be bought by the users but can be "sent" to users via a mailbox service hosted on Redis. After creating a material product (i.e. a flag), only the owner of the product is able to request a send to the mailbox by signing the destination endpoint with its own private key.

#### Solution

The vulnerability to be exploited relies on the fact that the key being used to compute the HMAC by the checksystem is an Ethereum private key formatted as

```
'0x' + 64-bit HEX
```

The length of the key thus makes the HMAC implementation use not the original key but its hash. Those hashes are publicly served by the backend application at the `/product-sellers` endpoint

## Deployment notes

### Technology stack

- Solidity (for smart contracts)
- Python /w Flask (for backend)
- Angular (for frontend)
- Redis (as "mailbox" service, hosting channels)

### Environment variables

All env variables are set in the .env file and are taken in both build stages and container runtimes
Ethereum smart contract addresses must not be changed during the CTF, they must be set after the first full deploy

### Team keys

`eth-deploy/keys` folder contains private keys of all teams. Each account is preloaded with a default balance on the blockchain needed to pay gas fees from contract deploys and transactions. As no other accounts can be initialized with default ETH balance, checker and exploits need to transfer some small amount needed for gas before operating to the new account created at each tick.

`0.key` is pwnthem0le private key, owner of all m0lecoin contracts

`addresses.json` contains all public addresses associated to each key

### Smart contracts deploy

`eth-deploy/full_deploy.py` compiles contracts from `m0lecoin-eth-contracts/contracts` folder, saves abis (json) in `eth-deploy/abis` folder

IM0leShop and Im0leCoin abis must be copied in `m0lecoin-backend/abi` folder as `shop.json` and `token.json`

IM0leShop, IM0leBank and Im0leCoin abis must be updated in `m0lecoin-frontend/src/assets/json-interfaces` folder [.ts files]

After the full deploy all contract address are saved in `eth-deploy/deploy_stats.json` as token, shop, bank addresses for each team. These address must be saved in the .env file

__NOTE__: you must set the `NUM_TEAMS` variable in the Python script before launch

### Docker frontend, backend, db deploy

Eventual step for redeploy during the CTF for smart contract updates:<br>
`python3 contract_redeploy.py <'shop'|'bank'|'all'>`<br>
This takes care of correctly updating the .env file and frontend/backend contract abis before running the docker build

`docker-compose [--env-file .env] up -d --build`

### OTP oracle for bank openAccount feature

Bank openAccount requires a valid signature of a random generated string signed with the `0.key` pwnthem0le key. The oracle service is in `m0lecoin-otp-oracle` folder.
To deploy the service, first edit the `.env` file then run `docker-compose up -d`.

The oracle tracks last otp emission timestamp and value for each team in a Redis instance, updates the value after TICK_SECONDS seconds and returns the signature of the current valid otp.

[Only one endpoint `GET /signature` ]

The team number should be derived from the IP address or the requester

### Notes

For testing purposes a testnet Ethereu blockchain is suitable for the deployment of all smart contracts. For management purposes, during the CTF each team was assigned a different blockchain hosted at the organizers infrastructure. A local deployment using common tools for smart contract development is acceptable when testing the challenge (blockchain address and networkId should be accordingly set in project variables)

# Screenshots

![Login](/images/Screenshot%202024-11-19%20alle%2017.26.27.png)
![m0leWallet](/images/Screenshot%202024-11-19%20alle%2017.26.49.png)
![m0leShop Sell](/images/Screenshot%202024-11-19%20alle%2017.27.36.png)
![m0leShop Gadgets](/images/Screenshot%202024-11-19%20alle%2017.28.23.png)