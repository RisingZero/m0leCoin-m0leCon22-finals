// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ITokenReceiver.sol";
import "./Im0leCoin.sol";
import "./IM0leShop.sol";

contract M0leShop is ITokenReceiver, IM0leShop {

    address payable tokenContract;
    uint256[10] __gap;  // Proxy variables reserved space
    mapping (int256 => uint256) productPrices;
    mapping (int256 => address) productOwners;
    mapping (int256 => bool) productRegistered;

    // move to proxy
    constructor(address payable token) {
        tokenContract = token;
    }

    function putOnSale(int256 productId, uint256 price) external override {
        require(!productRegistered[productId], "product already registered");
        productRegistered[productId] = true;
        productOwners[productId] = msg.sender;
        productPrices[productId] = price;
    }

    function buy(int256 productId) external override {
        require(productRegistered[productId]);
        require(productOwners[productId] != msg.sender, "you can't buy your own products");
        Im0leCoin token = Im0leCoin(tokenContract);
        require(token.balanceOf(msg.sender) >= productPrices[productId]);
        token.requestTransfer(msg.sender, productPrices[productId]);
        token.transfer(productOwners[productId], productPrices[productId]);
        emit ProductSale(productId, msg.sender);
    }

    function getPriceById(int256 productId) external view override returns(uint256) {
        require(productRegistered[productId]);
        return productPrices[productId];
    }

    fallback () external { }

}