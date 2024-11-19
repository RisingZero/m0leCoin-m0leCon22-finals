// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ITokenReceiver.sol";
import "./Im0leCoin.sol";

contract m0leCoin is Im0leCoin {
	mapping (address => uint256) private _balances;
	mapping (address => bool) private _banks;
	mapping (address => bool) private _shops;
	mapping (bytes32 => bool) private _usedOtps;
	address private owner;

	constructor() {
		owner = tx.origin;
		_balances[tx.origin] = 10000;
	}

	function isContract(address _addr) private view returns (bool) {
		uint32 size;
		assembly {
			size := extcodesize(_addr)
		}
		return (size > 0);
	}

	function name() external pure override returns (string memory) {
		return "moleC0in";
	}

	function symbol() external pure override returns (string memory) { 
		return "M0L";
	}

	function granularity() external pure override returns (uint256) { 
		return 1;
	}

	function mintCoins(address _to, uint256 amount, uint8 v, bytes32 r, bytes32 s, bytes32 hash) public {
		if (msg.sender == owner || _banks[msg.sender]) {
			if (!_usedOtps[hash] && owner == ecrecover(hash, v, r, s)) {
				_usedOtps[hash] = true;
				_balances[_to] += amount;
				emit Minted(_to, amount);
				if (isContract(_to)) {
					ITokenReceiver recvObj = ITokenReceiver(_to);
					recvObj.tokensReceived();
				}
			}
		}
	}

	function registerBank(address _bank) public {
		require(msg.sender == owner);
		_banks[_bank] = true;
		_balances[_bank] = 1000000;
	}

	function registerShop(address _shop) public {
		require(msg.sender == owner);
		_shops[_shop] = true;
		_balances[_shop] = 1000000;
	}

	function transfer(address _to, uint256 amount) external override {
		if (!_banks[msg.sender] && !_shops[msg.sender]) {
			require(_balances[msg.sender] >= amount, "insufficient balance");
			_balances[msg.sender] -= amount;
		}
		if (!_banks[_to] && !_shops[_to]) {
			_balances[_to] += amount;
		}
		emit Sent(msg.sender, _to, amount);
		if (isContract(_to)) {
			ITokenReceiver recvObj = ITokenReceiver(_to);
			recvObj.tokensReceived();
		}
	}

	function requestTransfer(address _from, uint256 amount) external override {
		require(_banks[msg.sender] || _shops[msg.sender] || msg.sender == owner);
		if (!_banks[_from] && !_shops[_from]) {
			require(_balances[_from] >= amount, "insufficient balance");
			_balances[_from] -= amount;
		}
		if (!_banks[msg.sender] && !_shops[msg.sender]) {
			_balances[msg.sender] += amount;
		}
		emit Sent(_from, msg.sender, amount);
		if (isContract(msg.sender)) {
			ITokenReceiver recvObj = ITokenReceiver(msg.sender);
			recvObj.tokensReceived();
		}
	}

	function balanceOf(address addr) external view override returns (uint256) {
		return _balances[addr];
	}

	function getBalance() external view override returns (uint256) {
		return _balances[msg.sender];
	}

	fallback () external { }
}
