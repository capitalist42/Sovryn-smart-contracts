hre = require("hardhat");

const {
    deployments: { deploy, get, log },
    getNamedAccounts,
    ethers,
} = hre;

const getStakingModulesNames = () => {
    return {
        StakingAdminModule: "StakingAdminModule",
        StakingGovernanceModule: "StakingGovernanceModule",
        StakingStakeModule: "StakingStakeModule",
        StakingStorageModule: "StakingStorageModule",
        StakingVestingModule: "StakingVestingModule",
        StakingWithdrawModule: "StakingWithdrawModule",
        WeightedStakingModule: "WeightedStakingModule",
    };
};

const stakingRegisterModuleWithMultisig = () => {
    return process.env.STAKING_REG_WITH_MULTISIG == "true";
};

/* sendWithMultisig(multisigAddress, contractAddress, data, sender, value = 0):
    multisig = Contract.from_abi("MultiSig", address=multisigAddress, abi=MultiSigWallet.abi, owner=multisigAddress)
    tx = multisig.submitTransaction(contractAddress,value,data, {'from': sender})
    txId = tx.events["Submission"]["transactionId"]
    print("tx id: ", txId) */

const sendWithMultisig = async (multisigAddress, contractAddress, data, sender, value = 0) => {
    console.log("Multisig tx data:", data);
    const multisig = await ethers.getContractAt("MultiSigWallet", multisigAddress);
    const signer = await hre.ethers.getSigner(sender);
    receipt = await (
        await multisig.connect(signer).submitTransaction(contractAddress, value, data)
    ).wait();

    const abi = ["event Submission(uint256 indexed transactionId)"];
    let iface = new ethers.utils.Interface(abi);
    const parsedEvent = await getParsedEventLogFromReceipt(receipt, iface, "Submission");
    console.log("Multisig tx id:", parsedEvent.transactionId.value.toNumber());

    //iface.
    //let data = msInterface.encodeFunctionData("setImplementation", [contractAddress]);

    /*let StakingProxyABI = [
        //   // add "payable" to the Solidity signature
        "function setImplementation(address _implementation)",
    ];

    let iStakingRewardsProxy = new ethers.utils.Interface(StakingProxyABI);
    const data = iStakingRewardsProxy.encodeFunctionData("setImplementation", [
        stakinRewardsLogic.address,
    ]);
    */
};

const multisigCheckTx = async (txId, multisigAddress = ethers.constants.ADDRESS_ZERO) => {
    const multisig = await ethers.getContractAt(
        "MultiSigWallet",
        multisigAddress == ethers.constants.ADDRESS_ZERO
            ? (
                  await get("MultiSigWallet")
              ).address
            : multisigAddress
    );
    console.log(
        "TX ID: ",
        txId,
        "confirmations: ",
        (await multisig.getConfirmationCount(txId)).toNumber(),
        " Executed:",
        (await multisig.transactions(txId))[3],
        " Confirmed by: ",
        await multisig.getConfirmations(txId)
    );
    console.log("TX Data:", (await multisig.transactions(txId))[2]);
};

const parseEthersLog = (parsed) => {
    let parsedEvent = {};
    for (let i = 0; i < parsed.args.length; i++) {
        const input = parsed.eventFragment.inputs[i];
        const arg = parsed.args[i];
        const newObj = { ...input, ...{ value: arg } };
        parsedEvent[input["name"]] = newObj;
    }
    return parsedEvent;
};

const getEthersLog = async (contract, filter) => {
    if (contract === undefined || filter === undefined) return;
    const events = await contract.queryFilter(filter);
    if (events.length === 0) return;
    let parsedEvents = [];
    for (let event of events) {
        const ethersParsed = contract.interface.parseLog(event);
        const customParsed = parseEthersLog(ethersParsed);
        parsedEvents.push(customParsed);
    }
    return parsedEvents;
};

const getParsedEventLogFromReceipt = async (receipt, iface, eventName) => {
    const topic = iface.getEventTopic(eventName);
    // search for the log by the topic
    const log = receipt.logs.find((x) => x.topics.indexOf(topic) >= 0);
    // finally, you can parse the log with the interface
    // to get a more user-friendly event object
    const parsedLog = iface.parseLog(log);
    return parseEthersLog(parsedLog);
};

module.exports = {
    getStakingModulesNames,
    stakingRegisterModuleWithMultisig,
    parseEthersLog,
    getEthersLog,
    getParsedEventLogFromReceipt,
    sendWithMultisig,
    multisigCheckTx,
};
