// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ITokenReceiver.sol";
import "./IM0leBank.sol";

contract M0leBank is ITokenReceiver, IM0leBank {

    address payable tokenContract;
    uint256[10] __gap;  // Proxy variables reserved space
    mapping (address => uint256) _accounts;
    mapping (address => bool) _registrations;

    // Move to the proxy
    constructor(address payable molecoin) {
        tokenContract = molecoin;
    }

    function openAccount(uint8 v, bytes32 r, bytes32 s, bytes32 hash) external override {
        require(!_registrations[msg.sender], "user already registered");
        tokenContract.call{gas: 100000}(abi.encodeWithSignature("mintCoins(address,uint256,uint8,bytes32,bytes32,bytes32)", msg.sender, 10, v, r, s, hash));
        _registrations[msg.sender] = true;
    }

    function isRegistered() external view override returns(bool) {
        return _registrations[msg.sender];
    }

    function deposit(uint256 amount) external override {
        require(_registrations[msg.sender], "user not registered");
        tokenContract.call{gas: 50000}(abi.encodeWithSignature("requestTransfer(address,uint256)", msg.sender, amount));
        _accounts[msg.sender] += amount;
    }

    function withdraw() external override {
        require(_registrations[msg.sender], "user not registered");
        require(_accounts[msg.sender] > 0, "bank account is empty");
        tokenContract.call{gas: 50000}(abi.encodeWithSignature("transfer(address,uint256)", msg.sender, _accounts[msg.sender]));
        _accounts[msg.sender] = 0;
    }

    function getBalance() external view override returns (uint256) {
        return _accounts[msg.sender];
    }

}