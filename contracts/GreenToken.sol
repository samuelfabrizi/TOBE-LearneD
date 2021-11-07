// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/presets/ERC20PresetMinterPauser.sol";

contract GreenToken is ERC20PresetMinterPauser{

  constructor() ERC20PresetMinterPauser("Green Token", "GRN") {
    _mint(msg.sender, 1000000 * (10 ** uint256(decimals())));
  }

}
