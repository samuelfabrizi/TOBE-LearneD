// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "./GreenDEX.sol";
import "./GreenToken.sol";


/// @title Announcement
/// @notice This contract contains all the information related to
///         the announcement of a ML task proposed
contract Announcement {

  using SafeMath for uint256;

  // address of the manufacturer
  address public manufacturerAddress;
  // in a real implementation this attribute corresponds to
  // the CID
  // path to the task's configuration file
  string public taskConfiguration;
  // maximum number of participants admitted in the task
  uint8 public maxNumberParticipant;
  // number of participants subscribed in the task
  uint8 public currentNumberParticipant;
  // number of tokens stake
  uint256 public tokensAtStake;
  // percentage of tokens to assign to the validator
  uint8 public percentageRewardValidator;
  // mapping from participant address to boolean that indicates
  // whether the participant is subscribed in the task
  mapping(address => bool) private participants;
  // mapping from participant address to participant id
  mapping(address => uint8) private participant2id;
  // array of participants' identifier
  bool[] public participantsIdentifier;
  // participants' identifiers
  uint8[] public participantIds;
  // boolean variable that indicates if the task is finished (true)
  bool public isFinished = false;
  // address of the validator (trusted)
  address public validatorAddress;
  // GreenDEX smart contract instance
  GreenToken private greenToken;

  /// @notice Sets the manufacturer address
  /// @param _greenDex_address address of the GreenDEX instance
  constructor (address _greenDex_address) {
    manufacturerAddress = msg.sender;
    greenToken = GreenToken(GreenDEX(_greenDex_address).greenToken());
  }

  /// @notice Checks if the sender address corresponds to the manufacturer address
  modifier onlyManufacturer() {
    require(
      msg.sender == manufacturerAddress,
      "Sender not authorized"
    );
    _;
  }

  /// @notice Checks if the sender is subscribed in the task
  modifier newSubscription() {
    require(
      participants[msg.sender] == false,
      "Participant already subscribed"
    );
    _;
  }

  /// @notice Checks if the sender is not already subscribed in the task
  modifier isSubscribed() {
    require(
      participants[msg.sender] == true,
      "Participant not subscribed"
    );
    _;
  }

  /// @notice Checks if the task is already started
  modifier notAlreadyStarted() {
    require(
      currentNumberParticipant != maxNumberParticipant,
      "The task is already started"
    );
    _;
  }

  /// @notice Checks if the task is in progress
  modifier taskInProgress(){
    require(
      isFinished != true,
      "The task is already finished"
    );
    _;
  }

  /// @notice Initializes the announcement
  /// @param _taskConfiguration path to the task's configuration file
  /// @param _maxNumberParticipant maximum number of participants admitted in the task
  /// @param _tokensAtStake number of tokens at stake
  /// @param _percentageRewardValidator percentage of tokens to assign to the validator  in (0, 100)
  /// @param _validatorAddress address of the validator (trusted)
  function initialize (
    string memory _taskConfiguration,
    uint8 _maxNumberParticipant,
    uint256 _tokensAtStake,
    uint8 _percentageRewardValidator,
    address _validatorAddress
    ) public onlyManufacturer() {
      require(
        _maxNumberParticipant > 1,
        "Insufficient max participants"
      );
      require(
        _tokensAtStake > 0,
        "Not empty rewards"
      );
      require(
        _percentageRewardValidator > 0,
        "Not empty validator reward"
      );
      require(
        _percentageRewardValidator < 100,
        "Not percentage validator reward"
      );
      taskConfiguration = _taskConfiguration;
      maxNumberParticipant = _maxNumberParticipant;
      tokensAtStake = _tokensAtStake;
      percentageRewardValidator = _percentageRewardValidator;
      currentNumberParticipant = 0;
      participantsIdentifier = new bool[](maxNumberParticipant);
      validatorAddress =_validatorAddress;
  }

  /// @notice Subscribes the sender in the announcement
  function subscribe() public notAlreadyStarted() newSubscription() {
    participants[msg.sender] = true;
    participant2id[msg.sender] = currentNumberParticipant;
    participantsIdentifier[currentNumberParticipant] = true;
    currentNumberParticipant = currentNumberParticipant + 1;
  }

  /// @notice Retrieves the participant' id of the caller
  /// @return participant id
  function getParticipantId() public view isSubscribed() returns(uint8) {
    return participant2id[msg.sender];
  }

  // TODO: add a requirement -> sender == validator
  /// @notice Defines the end of task
  function endTask() public {
    isFinished = true;
  }

  function assignRewards() public taskInProgress() {
    uint validatorReward = tokensAtStake.mul(
      percentageRewardValidator).div(100);
      // TODO: add validator address
      //greenToken.transfer();
  }


}
