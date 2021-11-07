// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "./GreenToken.sol";


contract GreenDEX {

  using SafeMath for uint256;

  GreenToken public greenToken;

  event Bought(uint256 amount);
  event Sold(uint256 amount);

  constructor() {
    greenToken = new GreenToken();
  }

  function buy() payable public {
    uint256 amountTobuy = msg.value;
    uint256 dexBalance = greenToken.balanceOf(address(this));
    require(
      amountTobuy > 0,
      "Some ether are needed"
    );

    if (amountTobuy <= dexBalance) {
      uint256 diff = dexBalance.sub(amountTobuy);
      greenToken.mint(address(this), diff.mul(2));
    }
    require(
      amountTobuy <= dexBalance,
      "Not enough tokens"
    );

    greenToken.transfer(msg.sender, amountTobuy);
    emit Bought(amountTobuy);
  }

  function approve(uint256 amount) public returns(bool)  {
    return greenToken.approve(address(this), amount);
  }

  function sell(uint256 amount) public {
    require(
      amount > 0,
      "Some tokens are needed"
    );
    uint256 allowance = greenToken.allowance(msg.sender, address(this));
    require(
      allowance >= amount,
      "Check the token allowance"
    );
    greenToken.transferFrom(msg.sender, address(this), amount);
    payable(msg.sender).transfer(amount);
    emit Sold(amount);
  }


}
