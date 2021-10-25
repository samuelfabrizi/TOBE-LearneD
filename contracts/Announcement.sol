pragma solidity >=0.4.22 <0.9.0;

/// @title Announcement
/// @notice This contract contains all the information related to the announcement
///         of a ML task proposed
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
  // mapping from participant address to boolean that indicates
  // whether the participant is subscribed in the task
  mapping(address => bool) private participants;
  // mapping from participant address to participant id
  mapping(address => uint8) private participant2id;
  // array of participants' identifier
  bool[] public participantsIdentifier;


  uint8[] public participantIds;

  /// @notice Sets the manufacturer address
  constructor () public {
    manufacturerAddress = msg.sender;
  }

  /// @notice Check if the sender address corresponds
  ///         to the manufacturer address
  modifier onlyManufacturer() {
    require(
      msg.sender == manufacturerAddress,
      "Sender not authorized"
    );
    _;
  }

  modifier newSubscription() {
    require(
      participants[msg.sender] == false,
      "Participant already subscribed"
    );
    _;
  }

  modifier isSubscribed() {
    require(
      participants[msg.sender] == true,
      "Participant not subscribed"
    );
    _;
  }

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
    uint8 _maxNumberParticipant
    ) public onlyManufacturer() {
      taskConfiguration = _taskConfiguration;
      maxNumberParticipant = _maxNumberParticipant;
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

  function getParticipantId() public view isSubscribed() returns(uint8) {
    return participant2id[msg.sender];
  }

}
