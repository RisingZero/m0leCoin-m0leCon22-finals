// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ITokenReceiver {

    event TokensReceived(string message);

    function tokensReceived() virtual external {
        emit TokensReceived("Tokens received!");
    }
    
}