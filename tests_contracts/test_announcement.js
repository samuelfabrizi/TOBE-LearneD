const Announcement = artifacts.require("Announcement");

const taskName = "Task test";
const taskDescription = "Description task test";
// TODO: change w.r.t. deadlineDate attribute in Announcement
const deadlineDate = 8;
const modelArtifact = "path/to/model_artifact";
const modelConfig = "path/to/model_config";
const modelWeights = "path/to/model_weights";
const flRound = 5;

contract("Test Announcement smart contract", accounts => {
  const manufacturer = accounts[0];
  beforeEach('Deploy the Announcement smart contract', async () => {
    announcementInstance = await Announcement.deployed({from: manufacturer});
  });

  it("should deploy the Announcement SC", async () => {
    assert.equal(
      await announcementInstance.manufacturerAddress(),
      manufacturer,
      "The owner of the Announcement SC should be the manufacturer: " + manufacturer);
  });

  it("should initialize the Announcement SC with the ML task attributes", async () => {
    await announcementInstance.initialize(
      web3.utils.fromUtf8(taskName),
      web3.utils.fromUtf8(taskDescription),
      deadlineDate,
      web3.utils.fromUtf8(modelArtifact),
      web3.utils.fromUtf8(modelConfig),
      web3.utils.fromUtf8(modelWeights),
      flRound,
      {from: manufacturer}
    );
    assert.equal(
      web3.utils.toUtf8(await announcementInstance.taskName()),
      taskName,
      "The task name should be " + manufacturer
    );
    assert.equal(
      web3.utils.toUtf8(await announcementInstance.taskDescription()),
      taskDescription,
      "The task description should be " + manufacturer
    );
    assert.equal(
      await announcementInstance.deadlineDate(),
      deadlineDate,
      "The task deadline should be " + manufacturer
    );
    assert.equal(
      web3.utils.toUtf8(await announcementInstance.modelArtifact()),
      modelArtifact,
      "The model's artifact should be " + manufacturer
    );
    assert.equal(
      web3.utils.toUtf8(await announcementInstance.modelConfig()),
      modelConfig,
      "The model's config should be " + manufacturer
    );
    assert.equal(
      web3.utils.toUtf8(await announcementInstance.modelWeights()),
      modelWeights,
      "The model's weights should be " + manufacturer
    );
    assert.equal(
      await announcementInstance.flRound(),
      flRound,
      "The federated rounds shold be " + manufacturer
    );

  });

});
