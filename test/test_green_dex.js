const truffleAssert = require('truffle-assertions');
const GreenDEX = artifacts.require("GreenDEX");
const GreenToken = artifacts.require("GreenToken");


contract("Test GreenDEX smart contract", accounts => {
  const manufacturer = accounts[1];
  const consumer1 = accounts[2];

  describe("Manufacturer tokens' purchase", async () => {

    beforeEach('Deploy the GreenDEX smart contract', async () => {
      greenDexInstance = await GreenDEX.new({from: accounts[2]});
      const greenTokenAddress = await greenDexInstance.greenToken();
      greenTokenInstance = await GreenToken.at(greenTokenAddress);
    });

    it("the manufacturer should not buy tokens without ether", async () => {
      await truffleAssert.reverts(
        greenDexInstance.buy({from: manufacturer, value: 0})
      );
    });

    it("the manufacturer should acquire some tokens", async () => {
      const nTokenToBuy = 10;
      let tx = await greenDexInstance.buy({from: manufacturer, value: nTokenToBuy});
      assert.equal(
        await greenTokenInstance.balanceOf(manufacturer),
        nTokenToBuy,
        "The manufacturer should have " + nTokenToBuy + " tokens");
    });

    it("should emit the Bought event", async () => {
      const nTokenToBuy = 10;
      let tx = await greenDexInstance.buy({from: manufacturer, value: nTokenToBuy});
      truffleAssert.eventEmitted(tx, 'Bought', (ev) => {
        return ev.amount.toNumber() === nTokenToBuy;
      });
    });

    beforeEach('The consumer1 buys some tokens', async () => {
      await greenDexInstance.buy({from: consumer1, value: 30});
    });

    it("the consumer1 should sell an amount of token less then his balance", async () => {
      const nTokenToSell = 40;
      await greenTokenInstance.approve(
        greenDexInstance.address, nTokenToSell,
        {from: consumer1}
      );
      await truffleAssert.reverts(
        greenDexInstance.sell(nTokenToSell, {from: consumer1})
      );
    });

    it("the consumer1 should approve the tokens transfer before sell them", async () => {
      const nTokenToSell = 10;
      await truffleAssert.reverts(
        greenDexInstance.sell(nTokenToSell, {from: consumer1})
      );
    });

    it("the consumer1 should sell some tokens", async () => {
      const nTokenToSell = 10;
      await greenTokenInstance.approve(
        greenDexInstance.address, nTokenToSell,
        {from: consumer1}
      );
      await greenDexInstance.sell(nTokenToSell, {from: consumer1});
      assert.equal(
        await greenTokenInstance.balanceOf(consumer1),
        30 - nTokenToSell,
        "The consumer1 should have " + (30 - nTokenToSell) + " tokens");
    });

    it("should emit the Sold event", async () => {
      const nTokenToSell = 10;
      await greenTokenInstance.approve(
        greenDexInstance.address, nTokenToSell,
        {from: consumer1}
      );
      let tx = await greenDexInstance.sell(nTokenToSell, {from: consumer1});
      truffleAssert.eventEmitted(tx, 'Sold', (ev) => {
        return ev.amount.toNumber() === nTokenToSell;
      });
    });

  });

});
