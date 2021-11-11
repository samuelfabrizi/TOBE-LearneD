const truffleAssert = require('truffle-assertions');
const GreenDEX = artifacts.require("GreenDEX");
const Announcement = artifacts.require("Announcement");

const taskConfiguration = "path/task/configuration.json";
const maxNumberParticipant = 2;
const tokensAtStake = 100000000;
const percentageRewardValidator = 20;


contract("Test Announcement smart contract", accounts => {
  const manufacturer = accounts[0];
  const consumer1 = accounts[1];
  const consumer2 = accounts[2];
  const consumer3 = accounts[3];
  const validator = accounts[9];

  describe("Announcement SC initialization", async () => {

    beforeEach('Deploy the Announcement smart contract', async () => {
      const greenDexInstance = await GreenDEX.deployed();
      announcementInstance = await Announcement.new(greenDexInstance.address, {from: manufacturer});
    });

    it("should deploy the Announcement SC", async () => {
    assert.equal(
      await announcementInstance.manufacturerAddress(),
      manufacturer,
      "The owner of the Announcement SC should be the manufacturer: " + manufacturer);
    assert.equal(
      await announcementInstance.isFinished(),
      false,
      "The task should not be finished");
    });

    it("should reject the initialization (wrong caller)", async () => {
      await truffleAssert.reverts(
        announcementInstance.initialize(
          taskConfiguration,
          maxNumberParticipant,
          tokensAtStake,
          percentageRewardValidator,
          validator,
          {from: consumer1}
        )
      );
    });

    it("should reject the initialization (empty reward)", async () => {
      await truffleAssert.reverts(
        announcementInstance.initialize(
          taskConfiguration,
          maxNumberParticipant,
          0,
          percentageRewardValidator,
          validator,
          {from: manufacturer}
        )
      );
    });

    it("should reject the initialization (insufficient maximum number of participants)", async () => {
      await truffleAssert.reverts(
        announcementInstance.initialize(
          taskConfiguration,
          1,
          tokensAtStake,
          percentageRewardValidator,
          validator,
          {from: manufacturer}
        )
      );
    });

    it("should reject the initialization (empty validator's reward)", async () => {
      await truffleAssert.reverts(
        announcementInstance.initialize(
          taskConfiguration,
          maxNumberParticipant,
          tokensAtStake,
          0,
          validator,
          {from: manufacturer}
        )
      );
    });

    it("should reject the initialization (not percentage validator's reward)", async () => {
      await truffleAssert.reverts(
        announcementInstance.initialize(
          taskConfiguration,
          maxNumberParticipant,
          tokensAtStake,
          101,
          validator,
          {from: manufacturer}
        )
      );
    });

    it("should initialize the Announcement SC with the ML task attributes", async () => {
      await announcementInstance.initialize(
        taskConfiguration,
        maxNumberParticipant,
        tokensAtStake,
        percentageRewardValidator,
        validator,
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
      assert.equal(
        await announcementInstance.tokensAtStake(),
        tokensAtStake,
        "The number of tokens at stake should be " + tokensAtStake
      );
      assert.equal(
        await announcementInstance.percentageRewardValidator(),
        percentageRewardValidator,
        "The percentage of the validator's reward should be " + percentageRewardValidator
      );
      assert.equal(
        await announcementInstance.validatorAddress(),
        validator,
        "The validator address should be " + validator
      );

    });

  });

  describe("Consumer subscription", async () => {

    beforeEach('Deploy and initialize the Announcement smart contract', async () => {
      const greenDexInstance = await GreenDEX.deployed();
      announcementInstance = await Announcement.new(greenDexInstance.address, {from: manufacturer});
      await announcementInstance.initialize(
        taskConfiguration,
        maxNumberParticipant,
        tokensAtStake,
        percentageRewardValidator,
        validator,
        {from: manufacturer}
      );
    });

    it("should subscribe in the Announcement", async () => {
      await announcementInstance.subscribe({from: consumer1});
      assert.equal(
        await announcementInstance.currentNumberParticipant(),
        1,
        "The current number of participants should be " + 1
      );
    });

    it("should not subscribe in the Announcement (already subscribed)", async () => {
      await announcementInstance.subscribe({from: consumer1});
      await truffleAssert.reverts(
        announcementInstance.subscribe(
          {from: consumer1}
        )
      );
    });

    it("the Consumer 1 should be subscribed", async () => {
      await announcementInstance.subscribe({from: consumer1});
      assert.equal(
        await announcementInstance.getParticipantId({from: consumer1}),
        0,
        "The consumer " + consumer1 + " should be subscribed"
      );
    });

    it("both the Consumer 1 and 2 should be subscribed", async () => {
      await announcementInstance.subscribe({from: consumer1});
      await announcementInstance.subscribe({from: consumer2});
      assert.equal(
        await announcementInstance.getParticipantId({from: consumer1}),
        0,
        "The consumer " + consumer1 + " should be subscribed"
      );
      assert.equal(
        await announcementInstance.getParticipantId({from: consumer2}),
        1,
        "The consumer " + consumer2 + " should be subscribed"
      );
    });

    it("the Consumer 2 should not be subscribed", async () => {
      await announcementInstance.subscribe({from: consumer1});
      await truffleAssert.reverts(
        announcementInstance.getParticipantId(
          {from: consumer2}
        )
      );
    });

    it("the Consumer 3 should not be accepted", async () => {
      await announcementInstance.subscribe({from: consumer1});
      await announcementInstance.subscribe({from: consumer2});
      await truffleAssert.reverts(
        announcementInstance.subscribe(
          {from: consumer3}
        )
      );
    });

  });

  describe("End of the task", async () => {

    beforeEach('Deploy and initialize the Announcement smart contract', async () => {
      const greenDexInstance = await GreenDEX.deployed();
      announcementInstance = await Announcement.new(greenDexInstance.address, {from: manufacturer});
      await announcementInstance.initialize(
        taskConfiguration,
        maxNumberParticipant,
        tokensAtStake,
        percentageRewardValidator,
        validator,
        {from: manufacturer}
      );
      await announcementInstance.subscribe({from: consumer1});
      await announcementInstance.subscribe({from: consumer2});
    });

    it("the validator should define the end of the task", async () => {
      await announcementInstance.endTask({from: validator});
      assert.equal(
        await announcementInstance.isFinished(),
        true,
        "The task should be finished"
      );

    });

    it("should reject the end task call (wrong caller)", async () => {
      await truffleAssert.reverts(
        announcementInstance.endTask({from: consumer1})
      );

    });

    /*
    it("the manufacturer should assign the rewards", async () => {
      await announcementInstance.assignRewards({from: manufacturer});
      assert.equal(
        await announcementInstance.isFinished(),
        true,
        "The task should be finished"
      );


    */
    });
});
