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
  // if the participant is subscribed in the task
  mapping(address => bool) private participants;

  uint8[] participantIds;

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
  }

  /// @notice Subscribes the sender in the announcement
  function subscribe() public {
    participants[msg.sender] = true;
    currentNumberParticipant = currentNumberParticipant + 1;
  }

  /// @notice Checks if the sender is subscribed
  /// @return True if the sendes is subscribed
  ///         False otherwise
  function isSubscribed() public view returns(bool) {
    return participants[msg.sender];
  }

}
