var Announcement = artifacts.require("Announcement");

module.exports = function(deployer) {
  deployer.deploy(Announcement);
};
