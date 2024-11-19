// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Im0leCoin {

    event Sent(
		address indexed _from, 
		address indexed _to, 
		uint256 _value
	);

	event Minted(
		address indexed _to,
		uint256 _value
	);

    function name() external pure returns (string memory);
    function symbol() external pure returns (string memory);
    function granularity() external pure returns (uint256);
    function transfer(address _to, uint256 amount) external;
    function requestTransfer(address _from, uint256 amount) external;
    function balanceOf(address addr) external view returns (uint256);
    function getBalance() external view returns (uint256);
    
}