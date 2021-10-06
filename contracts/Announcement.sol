pragma solidity >=0.4.22 <0.9.0;

contract Announcement {

  address public manufacturerAddress;
  bytes32 public taskName;
  // we can move the description in a decentralized storage
  // if it requires too much gas
  bytes32 public taskDescription;
  // TODO: for now the deadlineDate is only the number of days
  uint256 public deadlineDate;
  bytes32 public modelArtifact;
  // this field is only to show a human-readable model's config
  bytes32 public modelConfig;
  // actually this is not used by the participants, it is contained
  // in modelArtifact
  bytes32 public modelWeights;
  uint8 public flRound;

  constructor () public {
    manufacturerAddress = msg.sender;
  }

  function initialize (
    bytes32 _taskName,
    bytes32 _taskDescription,
    uint256 _deadlineDate,
    bytes32 _modelArtifact,
    bytes32 _modelConfig,
    bytes32 _modelWeights,
    uint8 _flRound
    )
    public onlyManufacturer() {
    taskName = _taskName;
    taskDescription = _taskDescription;
    deadlineDate = _deadlineDate;
    modelArtifact = _modelArtifact;
    modelConfig = _modelConfig;
    modelWeights = _modelWeights;
    flRound = _flRound;
  }

  modifier onlyManufacturer() {
    require(
      msg.sender == manufacturerAddress,
      "Sender not authorized"
    );
    _;
  }

}
