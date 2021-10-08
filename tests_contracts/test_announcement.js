const truffleAssert = require('truffle-assertions');
const Announcement = artifacts.require("Announcement");

const taskName = "Task test";
const taskDescription = "Description task test";
// TODO: change w.r.t. deadlineDate attribute in Announcement
const deadlineDate = 8;
const modelArtifact = "path/to/model_artifact";
const modelConfig = "path/to/model_config";
const modelWeights = "path/to/model_weights";
const featuresNames = "path/to/features_names";
const flRound = 5;

contract("Test Announcement smart contract", accounts => {
  const manufacturer = accounts[0];
  const consumer1 = accounts[1];
  const consumer2 = accounts[2];

  beforeEach('Deploy the Announcement smart contract', async () => {
    announcementInstance = await Announcement.deployed({from: manufacturer});
  });

  describe("Announcement SC initialization", async () => {

    it("shoud deploy the Announcement SC", async () => {
    assert.equal(
      await announcementInstance.manufacturerAddress(),
      manufacturer,
      "The owner of the Announcement SC should be the manufacturer: " + manufacturer);
    });

    it("should reject the initialization", async () => {
      await truffleAssert.reverts(
        announcementInstance.initialize(
          web3.utils.fromUtf8(taskName),
          web3.utils.fromUtf8(taskDescription),
          deadlineDate,
          web3.utils.fromUtf8(modelArtifact),
          web3.utils.fromUtf8(modelConfig),
          web3.utils.fromUtf8(modelWeights),
          web3.utils.fromUtf8(featuresNames),
          flRound,
          {from: consumer1}
        )
      );
    });

    it("should initialize the Announcement SC with the ML task attributes", async () => {
      await announcementInstance.initialize(
        web3.utils.fromUtf8(taskName),
        web3.utils.fromUtf8(taskDescription),
        deadlineDate,
        web3.utils.fromUtf8(modelArtifact),
        web3.utils.fromUtf8(modelConfig),
        web3.utils.fromUtf8(modelWeights),
        web3.utils.fromUtf8(featuresNames),
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
        web3.utils.toUtf8(await announcementInstance.featuresNames()),
        featuresNames,
        "The federated rounds should be " + manufacturer
      );
      assert.equal(
        await announcementInstance.flRound(),
        flRound,
        "The federated rounds should be " + manufacturer
      );

    });

  });

  describe("Consumer subscription", async () => {

    beforeEach('Consumer 1 subscribes to the task', async () => {
      await announcementInstance.subscribe({from: consumer1});
      nFlRounds = await announcementInstance.flRound();
    });

    it("the Consumer 1 should be subscribed", async () => {
      assert.equal(
        await announcementInstance.isSubscribed({from: consumer1}),
        true,
        "The consumer" + consumer1 + " should be subscribed"
      );
    });

    it("the Consumer 2 should not be subscribed", async () => {
      assert.equal(
        await announcementInstance.isSubscribed({from: consumer2}),
        false,
        "The consumer" + consumer2 + " should be subscribed"
      );
    });

  });

});
