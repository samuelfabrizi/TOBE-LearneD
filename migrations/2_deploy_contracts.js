var Announcement = artifacts.require("Announcement");
const fs = require("fs");
const output_file_name = "announcement_info.json";

module.exports = async(deployer) => {
  await deployer.deploy(Announcement);
  let contract = await Announcement.deployed();
  const contractObj = {"address": contract.address};
  const contractJson = JSON.stringify(contractObj, null, 4);
  fs.writeFileSync(output_file_name, contractJson, 'utf8');
  console.log("Write contract information in " + output_file_name);
};
