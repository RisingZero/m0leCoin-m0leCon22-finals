// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IM0leShop {

    event ProductSale(
		int256 indexed _id, 
		address indexed _to
	);

    function putOnSale(int256 productId, uint256 price) external;
    function buy(int256 productId) external;
    function getPriceById(int256 productId) external view returns(uint256);

}    