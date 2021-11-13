// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "./GreenToken.sol";


/// @title _greenDexAddress
/// @notice This contract contains the implementation of the
///         responsible for the direct exchange of green tokens
/// @custom:see In the current implementation 1 ether == 1 token
contract GreenDEX {

  using SafeMath for uint256;

  // green token instance
  GreenToken public greenToken;

  /// @notice Event triggered when someone purchase some tokens
  /// @param amount number of tokens purchased
  event Bought(uint256 amount);
  /// @notice Event triggered when someone sell some tokens
  /// @param amount number of tokens sold
  event Sold(uint256 amount);

  /// @notice Initializes the green token DEX
  constructor() {
    greenToken = new GreenToken();
  }

  /// @notice Permits to an address to buy tokens in exchange of ether
  function buy() external payable {
    uint256 amountTobuy = msg.value;
    require(
      amountTobuy > 0,
      "Some ether are needed"
    );

    uint256 dexBalance = greenToken.balanceOf(address(this));
    if (amountTobuy > dexBalance) {
      uint256 diff = amountTobuy.sub(dexBalance);
      greenToken.mint(address(this), diff.mul(2));
    }
    greenToken.transfer(msg.sender, amountTobuy);
    emit Bought(amountTobuy);
  }

  /// @notice Permits to an address to sell tokens in exchange of ether
  /// @param amount Number of token to sell
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
