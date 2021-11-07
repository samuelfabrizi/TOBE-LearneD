// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title Announcement
/// @notice This contract contains all the information related to
///         the announcement of a ML task proposed
contract Announcement {

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
  // mapping from participant address to boolean that indicates
  // whether the participant is subscribed in the task
  mapping(address => bool) private participants;
  // mapping from participant address to participant id
  mapping(address => uint8) private participant2id;
  // array of participants' identifier
  bool[] public participantsIdentifier;
  // participants' identifiers
  uint8[] public participantIds;

  /// @notice Sets the manufacturer address
  constructor () {
    manufacturerAddress = msg.sender;
  }

  /// @notice Checks if the sender address corresponds
  ///         to the manufacturer address
  modifier onlyManufacturer() {
    require(
      msg.sender == manufacturerAddress,
      "Sender not authorized"
    );
    _;
  }

  /// @notice Checks if the sender is
  ///         subscribed in the task
  modifier newSubscription() {
    require(
      participants[msg.sender] == false,
      "Participant already subscribed"
    );
    _;
  }

  /// @notice Checks if the sender is
  ///         not already subscribed in the task
  modifier isSubscribed() {
    require(
      participants[msg.sender] == true,
      "Participant not subscribed"
    );
    _;
  }

  /// @notice Checks if the tash is
  ///         already started
  modifier notAlreadyStarted() {
    require(
      currentNumberParticipant != maxNumberParticipant,
      "The task is already started"
    );
    _;
  }

  /// @notice Initializes the announcement
  /// @param _taskConfiguration path to the task's configuration file
  /// @param _maxNumberParticipant maximum number of participants admitted in the task
  function initialize (
    string memory _taskConfiguration,
    uint8 _maxNumberParticipant,
    uint256 _tokensAtStake
    ) public onlyManufacturer() {
      require(
        _tokensAtStake > 0,
        "Not empty rewards"
      );
      require(
        _maxNumberParticipant > 1,
        "Insufficient max participants"
      );
      taskConfiguration = _taskConfiguration;
      maxNumberParticipant = _maxNumberParticipant;
      tokensAtStake = _tokensAtStake;
      currentNumberParticipant = 0;
      participantsIdentifier = new bool[](maxNumberParticipant);
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

}
