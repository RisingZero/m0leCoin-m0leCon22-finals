// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IM0leBank {

    function openAccount(uint8 v, bytes32 r, bytes32 s, bytes32 hash) external;
    function isRegistered() external view returns(bool);
    function deposit(uint256 amount) external;
    function withdraw() external;
    function getBalance() external view returns (uint256);

}    