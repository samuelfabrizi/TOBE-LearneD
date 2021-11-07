var Announcement = artifacts.require("Announcement");
var GreenDEX = artifacts.require("GreenDEX");
const fs = require("fs");
const output_file_name = "announcement_info.json";

module.exports = async(deployer) => {
  // deploy the GreenDEX SC
  await deployer.deploy(GreenDEX);
  let contract_dex = await GreenDEX.deployed();

  // deploy the Announcement SC
  await deployer.deploy(Announcement);
  let contract = await Announcement.deployed();

  // create the json with contracts' addresses
  const contractObj = [
    {"address": contract.address},
    {"address_dex": contract_dex.address}
  ];
  // write the json file in the file system
  const contractJson = JSON.stringify(contractObj, null, 4);
  fs.writeFileSync(output_file_name, contractJson, 'utf8');
  console.log("Write contract information in " + output_file_name);
};
