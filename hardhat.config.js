const { task } = require("hardhat/config");

require("@nomiclabs/hardhat-ganache");
require("@nomiclabs/hardhat-truffle5");
require("@nomiclabs/hardhat-ethers");
require("hardhat-deploy-ethers");
require("@nomiclabs/hardhat-web3");
require("@nomiclabs/hardhat-waffle");
require("hardhat-contract-sizer"); //yarn run hardhat size-contracts
require("solidity-coverage"); // $ npx hardhat coverage
require("hardhat-log-remover");
require("hardhat-abi-exporter");
require("hardhat-deploy");
require("@nomicfoundation/hardhat-chai-matchers");
const {
    signWithMultisig,
    multisigCheckTx,
    multisigRevokeConfirmation,
    multisigExecuteTx,
    multisigAddRemoveOwner,
    multisigAddOwner,
    multisigRemoveOwner,
} = require("./deployment/helpers/helpers");
require("./hardhat/tasks/sips/createSIP");

require("./hardhat/tasks/tasks");

require("dotenv").config();

const testnetAccounts = process.env.TESTNET_DEPLOYER_PRIVATE_KEY
    ? [process.env.TESTNET_DEPLOYER_PRIVATE_KEY, process.env.TESTNET_SIGNER_PRIVATE_KEY]
    : [];
const mainnetAccounts = process.env.MAINNET_DEPLOYER_PRIVATE_KEY
    ? [process.env.MAINNET_DEPLOYER_PRIVATE_KEY, process.env.MAINNET_SIGNER_PRIVATE_KEY]
    : [];

/*
 * Test hardhat forking with patched hardhat
 *
 * If you get this error:
 * InvalidResponseError: Invalid JSON-RPC response's result.
 * Errors: Invalid value null supplied to : RpcBlockWithTransactions | null/transactions: RpcTransaction Array/2:
 * RpcTransaction/v: QUANTITY, Invalid value null supplied to : RpcBlockWithTransactions | null/transactions:
 * RpcTransaction Array/2: RpcTransaction/r: QUANTITY, Invalid value null supplied to :
 * RpcBlockWithTransactions | null/transactions: RpcTransaction Array/2: RpcTransaction/s: QUANTITY
 *
 * Then the forking doesn't work correctly (ie. hardhat was not properly patched)
 */
task("check-fork-patch", "Check Hardhat Fork Patch by Rainer").setAction(async (taskArgs, hre) => {
    await hre.network.provider.request({
        method: "hardhat_reset",
        params: [
            {
                forking: {
                    jsonRpcUrl: "https://mainnet4.sovryn.app/rpc",
                    blockNumber: 4272658,
                },
            },
        ],
    });
    //const xusd = await IERC20.at("0xb5999795BE0EbB5bAb23144AA5FD6A02D080299F");
    const xusd = await hre.ethers.getContractAt(
        "ERC20",
        "0xb5999795BE0EbB5bAb23144AA5FD6A02D080299F"
    );
    const totalSupply = await xusd.totalSupply();
    if (totalSupply.toString() === "12346114443582774719512874")
        console.log("Hardhat mainnet forking works properly!");
    else console.log("Hardhat mainnet forking does NOT work properly!");
});

task("governor-owner:queue-proposal", "Queue proposal in the Governor Owner contract")
    .addParam("proposal", "Proposal Id", undefined, types.string)
    .setAction(async ({ proposal }, hre) => {
        const { deployer } = await hre.getNamedAccounts();
        const god = await deployments.get("GovernorOwner");
        const governorOwner = await ethers.getContractAt("GovernorAlpha", god.address, deployer);
        await governorOwner.queue(proposal);
    });

task("multisig:sign-tx", "Sign multisig tx")
    .addParam("txId", "Multisig transaction to sign", undefined, types.string)
    .addOptionalParam("signer", "Signer name: 'signer' or 'deployer'", "deployer")
    .setAction(async ({ txId, signer }, hre) => {
        const signerAcc = (await hre.getNamedAccounts())[signer];
        const ms = await ethers.getContract("MultiSigWallet");
        await signWithMultisig(ms.address, txId, signerAcc);
    });

task("multisig:execute-tx", "Execute multisig tx by one of tx signers")
    .addParam("txId", "Multisig transaction to sign", undefined, types.string)
    .addParam("signer", "Multisig transaction to check", undefined, types.string, true)
    .setAction(async ({ txId, signer }, hre) => {
        await multisigExecuteTx(txId, signer ? signer : (await hre.getNamedAccounts()).signer);
    });

task("multisig:check-tx", "Check multisig tx")
    .addParam("txId", "Multisig transaction to check", undefined, types.string)
    .setAction(async (taskArgs, hre) => {
        await multisigCheckTx(taskArgs.txId);
    });

task("multisig:revoke-confirmation", "Revoke multisig tx confirmation")
    .addParam("txId", "Multisig transaction to check", undefined, types.string)
    .addParam("signer", "Signer", undefined, types.string, true)
    .setAction(async ({ txId, signer }, hre) => {
        await multisigRevokeConfirmation(
            txId,
            signer ? signer : (await hre.getNamedAccounts()).deployer
        );
    });

task("multisig:add-remove-owner", "Add or remove multisig owner")
    .addParam("add", "add = true, remove = false", undefined)
    .addParam("address", "Owner address to add or remove", undefined, types.string)
    .addParam("signer", "Multisig transaction to check", undefined, types.string, true)
    .setAction(async ({ add, address, signer }, hre) => {
        if (add == "true") {
            await multisigAddOwner(address);
        } else {
            await multisigRemoveOwner(address);
        }
        /*await multisigAddRemoveOwner(
            add,
            address,
            signer ? signer : (await hre.getNamedAccounts()).signer
        );*/
    });

/*task("accounts", "Prints accounts", async (_, { web3 }) => {
    console.log();
    console.log(await web3.eth.getAccounts());
});*/

// You need to export an object to set up your config
// Go to https://hardhat.org/config/ to learn more

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
/**/

module.exports = {
    solidity: {
        version: "0.5.17",
        settings: {
            optimizer: {
                enabled: true,
                runs: 200,
            },
            outputSelection: {
                "*": {
                    "*": ["storageLayout"],
                },
            },
        },
    },
    abiExporter: {
        clear: true,
        runOnCompile: true,
        flat: true,
        spacing: 4,
    },
    contractSizer: {
        alphaSort: false,
        runOnCompile: false,
        disambiguatePaths: false,
    },
    namedAccounts: {
        deployer: {
            default: 0,
        },
        signer: {
            default: 1,
        },
    },
    networks: {
        hardhat: {
            chainId: 31337,
            allowUnlimitedContractSize: true,
            accounts: { mnemonic: "test test test test test test test test test test test junk" },
            initialBaseFeePerGas: 0,
            port: 8505,
            live: false,
        },
        localhost: {
            timeout: 100000,
        },
        rskForkedTestnet: {
            chainId: 31337,
            accounts: testnetAccounts,
            url: "http://127.0.0.1:8545/",
            blockGasLimit: 6800000,
            live: true,
            tags: ["testnet", "forked"],
            timeout: 100000,
        },
        rskForkedTestnetFlashback: {
            chainId: 31337,
            accounts: testnetAccounts,
            url: "http://127.0.0.1:8545/",
            blockGasLimit: 6800000,
            live: true,
            tags: ["testnet", "forked"],
            timeout: 100000,
        },
        rskForkedMainnetFlashback: {
            chainId: 31337,
            accounts: mainnetAccounts,
            url: "http://127.0.0.1:8545",
            blockGasLimit: 6800000,
            live: true,
            tags: ["mainnet", "forked"],
            timeout: 100000,
        },
        rskForkedMainnet: {
            chainId: 31337,
            accounts: mainnetAccounts,
            url: "http://127.0.0.1:8545",
            blockGasLimit: 6800000,
            live: true,
            tags: ["mainnet", "forked"],
            timeout: 100000,
        },
        /*localhost: {
            url: "http://127.0.0.1:8545/",
            allowUnlimitedContractSize: true,
            initialBaseFeePerGas: 0,
        },*/
        rskTestnet: {
            url: "https://public-node.testnet.rsk.co/",
            accounts: testnetAccounts,
            chainId: 31,
            confirmations: 4,
            gasMultiplier: 1.25,
            tags: ["testnet"],
            //timeout: 20000, // increase if needed; 20000 is the default value
            //allowUnlimitedContractSize, //EIP170 contrtact size restriction temporal testnet workaround
        },
        rskMainnet: {
            url: "https://public-node.rsk.co/",
            chainId: 30,
            accounts: mainnetAccounts,
            tags: ["mainnet"],
            //timeout: 20000, // increase if needed; 20000 is the default value
            timeout: 100000,
        },
        rskSovrynTestnet: {
            url: "https://testnet.sovryn.app/rpc",
            accounts: testnetAccounts,
            chainId: 31,
            confirmations: 4,
            gasMultiplier: 1.25,
            tags: ["testnet"],
            //timeout: 20000, // increase if needed; 20000 is the default value
            //allowUnlimitedContractSize, //EIP170 contrtact size restriction temporal testnet workaround
        },
        rskSovrynMainnet: {
            url: "https://mainnet-dev.sovryn.app/rpc",
            chainId: 30,
            accounts: mainnetAccounts,
            gasPrice: 660000010,
            blockGasLimit: 6800000,
            tags: ["mainnet"],
            timeout: 100000,
            //timeout: 20000, // increase if needed; 20000 is the default value
        },
    },
    paths: {
        sources: "./contracts",
        tests: "./tests",
        deploy: "./deployment/deploy",
        deployments: "./deployment/deployments",
    },
    external: {
        contracts: [
            {
                artifacts: "external/artifacts/*.sol/!(*.dbg.json)",
                // deploy: "node_modules/@cartesi/arbitration/export/deploy",
            },
            //{
            //artifacts: "node_modules/someotherpackage/artifacts",
            //},
        ],
        deployments: {
            rskSovrynTestnet: ["external/deployments/rskSovrynTestnet"],
            rskTestnet: [
                "external/deployments/rskSovrynTestnet",
                "deployment/deployments/rskSovrynTestnet",
            ],
            rskForkedTestnet: [
                "external/deployments/rskSovrynTestnet",
                "external/deployments/rskForkedTestnet",
            ],
            rskForkedTestnetFlashback: ["external/deployments/rskForkedTestnetFlashback"],
            rskForkedMainnetFlashback: ["external/deployments/rskForkedMainnetFlashback"],
            rskSovrynMainnet: ["external/deployments/rskSovrynMainnet"],
            rskMainnet: ["external/deployments/rskSovrynMainnet"],
            rskForkedMainnet: [
                "external/deployments/rskSovrynMainnet",
                "external/deployments/rskForkedMainnet",
            ],
        },
    },
    typechain: {
        outDir: "types",
        target: "ethers-v5",
        alwaysGenerateOverloads: false, // should overloads with full signatures like deposit(uint256) be generated always, even if there are no overloads?
        externalArtifacts: ["external/artifacts/*.sol/!(*.dbg.json)"], // optional array of glob patterns with external artifacts to process (for example external libs from node_modules)
        // externalArtifacts: ["external/artifacts/*.json"], // optional array of glob patterns with external artifacts to process (for example external libs from node_modules)
    },
    mocha: {
        timeout: 800000,
    },
};
