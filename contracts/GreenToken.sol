// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/presets/ERC20PresetMinterPauser.sol";

/// @title GreenToken
/// @notice This contract represents an ERC20 token
contract GreenToken is ERC20PresetMinterPauser{

  /// @notice initializes the green token mintin a fixed initial supply
  constructor() ERC20PresetMinterPauser("Green Token", "GRN") {
    _mint(msg.sender, 1000000000000000000);
  }

}
