import { AbiItem } from 'web3-utils';

// Abi Interface m0leCoin contract
export const tokenInterface: AbiItem[] = [{"anonymous": false, "inputs": [{"indexed": true, "internalType": "address", "name": "_to", "type": "address"}, {"indexed": false, "internalType": "uint256", "name": "_value", "type": "uint256"}], "name": "Minted", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": true, "internalType": "address", "name": "_from", "type": "address"}, {"indexed": true, "internalType": "address", "name": "_to", "type": "address"}, {"indexed": false, "internalType": "uint256", "name": "_value", "type": "uint256"}], "name": "Sent", "type": "event"}, {"inputs": [{"internalType": "address", "name": "addr", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "getBalance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "granularity", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "pure", "type": "function"}, {"inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "pure", "type": "function"}, {"inputs": [{"internalType": "address", "name": "_from", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "requestTransfer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "pure", "type": "function"}, {"inputs": [{"internalType": "address", "name": "_to", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "transfer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}];