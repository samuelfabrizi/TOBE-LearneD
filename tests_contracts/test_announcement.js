const truffleAssert = require('truffle-assertions');
const Announcement = artifacts.require("Announcement");

const taskConfiguration = "path/task/configuration.json";
const maxNumberParticipant = 2;

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
          taskConfiguration,
          maxNumberParticipant,
          {from: consumer1}
        )
      );
    });

    it("should initialize the Announcement SC with the ML task attributes", async () => {
      await announcementInstance.initialize(
        taskConfiguration,
        maxNumberParticipant,
        {from: manufacturer}
      );
      assert.equal(
        await announcementInstance.taskConfiguration(),
        taskConfiguration,
        "The configuration task should be " + taskConfiguration
      );
      assert.equal(
        await announcementInstance.maxNumberParticipant(),
        maxNumberParticipant,
        "The maximum number of participants should be " + maxNumberParticipant
      );

    });

  });

  describe("Consumer subscription", async () => {

    beforeEach('Consumer 1 subscribes to the task', async () => {
      await announcementInstance.subscribe({from: consumer1});
    });

    it("the Consumer 1 should be subscribed", async () => {
      assert.equal(
        await announcementInstance.isSubscribed({from: consumer1}),
        true,
        "The consumer " + consumer1 + " should be subscribed"
      );
    });

    it("the Consumer 2 should not be subscribed", async () => {
      assert.equal(
        await announcementInstance.isSubscribed({from: consumer2}),
        false,
        "The consumer " + consumer2 + " should not be subscribed"
      );
    });

  });

});
