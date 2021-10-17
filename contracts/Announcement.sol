pragma solidity >=0.4.22 <0.9.0;

/// @title Announcement
/// @notice This contract contains all the information related to the announcement
///         of a ML task proposed
contract Announcement {

  /// @title ParticipantSubscription
  /// @notice This struct contains the participants's information
  struct ParticipantSubscription {
    bool isSubscribed;
    bool[] rounds;
  }

  // address of the manufacturer
  address public manufacturerAddress;
  // name of the task
  bytes32 public taskName;
  // we can move the description in a decentralized storage
  // if it requires too much gas
  // description of the task
  bytes32 public taskDescription;
  // TODO: for now the deadlineDate is only the number of days
  // date of the deadline
  uint256 public deadlineDate;
  // directory path to the whole model (both config and weights)
  string public modelArtifact;
  // this field is only to show a human-readable model's config
  // file path to model's config
  string public modelConfig;
  // actually this is not used by the participants, it is contained
  // in modelArtifact
  // file path to model's weights
  string public modelWeights;
  // file path to the name of the ML task features
  string public featuresNames;
  // number of rounds for the federated learning
  uint8 public flRound;
  mapping(address => ParticipantSubscription) private participants;

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
  /// @param _taskName name of the task
  /// @param _taskDescription description of the task
  /// @param _deadlineDate date of the deadline
  /// @param _modelArtifact directory path to the whole model
  ///        (both config and weights)
  /// @param _modelConfig file path to model's config
  /// @param _modelWeights file path to model's weights
  /// @param _featuresNames file path to the name of the ML task features
  /// @param _flRound number of rounds for the federated learning
  function initialize (
    bytes32 _taskName,
    bytes32 _taskDescription,
    uint256 _deadlineDate,
    string memory _modelArtifact,
    string memory _modelConfig,
    string memory _modelWeights,
    string memory _featuresNames,
    uint8 _flRound
    )
    public onlyManufacturer() {
    taskName = _taskName;
    taskDescription = _taskDescription;
    deadlineDate = _deadlineDate;
    modelArtifact = _modelArtifact;
    modelConfig = _modelConfig;
    modelWeights = _modelWeights;
    featuresNames = _featuresNames;
    flRound = _flRound;
  }

  /// @notice Subscribes the sender in the announcement
  function subscribe() public {
    participants[msg.sender] = ParticipantSubscription(
      true,
      new bool[](flRound)
    );
  }

  /// @notice Checks if the sender is subscribed
  /// @return True if the sendes is subscribed
  ///         False otherwise
  function isSubscribed() public view returns(bool) {
    return participants[msg.sender].isSubscribed;
  }

}
