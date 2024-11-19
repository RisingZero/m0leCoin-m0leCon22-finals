// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Proxy {
    address payable tokenContract;
    address logic;
    address owner;

    constructor(address payable _tokenAddr) {
        owner = tx.origin;
        tokenContract = _tokenAddr;
    }

    function upgradeLogic(address _newLogic) public {
        require(msg.sender == owner);
        logic = _newLogic;
    }

    function changeOwner(address _owner) public {
        require(msg.sender == owner);
        owner = _owner;
    }

    fallback() external payable {
        address _impl = logic;
        assembly {
            let ptr := mload(0x40)

            // (1) copy incoming call data
            calldatacopy(ptr, 0, calldatasize())

            // (2) forward call to logic contract
            let result := delegatecall(gas(), _impl, ptr, calldatasize(), 0, 0)
            let size := returndatasize()

            // (3) retrieve return data
            returndatacopy(ptr, 0, size)

            // (4) forward return data back to caller
            switch result
            case 0 { revert(ptr, size) }
            default { return(ptr, size) }
        }
    }
}