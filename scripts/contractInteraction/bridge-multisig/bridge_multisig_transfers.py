
'''
This script serves the purpose of interacting with existing smart contracts on the testnet or mainnet.
'''

from brownie import *
#from scripts.contractInteraction.token import * 
import json

def main():

    #load the contracts and acct depending on the network
    loadConfig()

    #call the function you want here

    # RSK-USDTes 0.01
    #sendTokensFromBridgeRSKMultisig(contracts['RSK-USDTes'], 10**16)

    #sendTokensFromBridgeETHMultisig(contracts['ETH-USDT'], 10**16)
    #print(acct)
    #sendAggregatedTokensFromExchequer(contracts['BNBbs'], contracts['Aggregator-BNB-RSK'], '0x5092019A3E0334586273A21a701F1BD859ECAbD6', 764e18)
    #sendAggregatedTokensFromExchequer(contracts['ETHbs'], contracts['Aggregator-ETH-RSK'], acct, 39.5e18)
    #sendTokensToETHFromMultisig(contracts['SOV'], '0xdd0e3546eebf3f1cc4454a16b4dc5b677923bdc1', 50000e18)
    #bal = getBalance(conf.contracts['USDCes'], conf.contracts['multisig'])
    #sendTokensToETHFromMultisig(contracts['USDTes'], '0x9E0816a71B53ca67201a5088df960fE90910DE55', 2000e18)
    #sendTokensToETHFromMultisig(contracts['ETHes'], '0x5092019A3E0334586273A21a701F1BD859ECAbD6', 15e18)
    #sendAggregatedTokensFromWallet(contracts['ETHes'], contracts['Aggregator-ETH-RSK'], '0xf5972e2bcc10404367cbdca2a3319470fbea3ff7', 2e17)

    #send eSOV send eSOV over the bridge to our gate.io address
    #sendTokensToETHFromMultisig(contracts['SOV'], '0x5092019A3E0334586273A21a701F1BD859ECAbD6', 260000e18)
    #DLLR
    #setFeeAndMinPerToken(contracts['DLLR'], 60e18, 70e18)
    #allowToken('0xc1411567d2670e24d9C4DaAa7CdA95686e1250AA') #DLLR - one time whitelisting on bridge
    #sendTokensToETHFromMultisig(contracts['DLLR'], '0xdD0E3546EEBf3f1Cc4454a16b4DC5b677923bDC1', 100e18) #to be on the safe side sending 100 DLLR to our multisig on ethereum
    
    #sendTokensFromWalletFromSepolia(contracts['SEPUSD'], acct, 1000e18)

def loadConfig():
    global contracts, acct
    thisNetwork = network.show_active()
    if thisNetwork == "development":
        acct = accounts[0]
        configFile =  open('./scripts/contractInteraction/testnet_contracts.json')
    elif thisNetwork == "testnet":
        acct = accounts.load("rskdeployer")
        configFile =  open('./scripts/contractInteraction/testnet_contracts.json')
    elif thisNetwork == "rsk-testnet":
        acct = accounts.load("rskdeployer")
        configFile =  open('./scripts/contractInteraction/testnet_contracts.json')
    elif thisNetwork == "rsk-mainnet":
        acct = accounts.load("rskdeployer")
        configFile =  open('./scripts/contractInteraction/mainnet_contracts.json')
    elif thisNetwork == "sepolia":
        acct = accounts.load("rskdeployer")
        configFile =  open('./scripts/contractInteraction/sepolia_contracts.json')
    else:
        raise Exception("Network not supported.")
    contracts = json.load(configFile)

# function setFeeAndMinPerToken(address token, uint256 _feeConst, uint256 _minAmount)
def setFeeAndMinPerToken(token, feeConst, minAmount):
    abiFileBridge =  open('./scripts/contractInteraction/bridge-multisig/Bridge.json')
    abiFileAllowTokens =  open('./scripts/contractInteraction/bridge-multisig/AllowTokens.json')
    abiBridge = json.load(abiFileBridge)
    abiAllowTokens = json.load(abiFileAllowTokens)
    bridgeRSK = Contract.from_abi("BridgeRSK", address=contracts['BridgeRSK'], abi=abiBridge, owner=acct)

    allowTokensAddress = bridgeRSK.allowTokens()
    allowTokens = Contract.from_abi("AllowTokens", address=allowTokensAddress, abi=abiAllowTokens, owner=acct)
    print(f"Configuring AllowTokens contract {allowTokens.address}: setting const fee and min amount")

    multiSigAddress = allowTokens.owner()
    print('Allow tokens owner address (multisig): ' + multiSigAddress)
    multiSig = Contract.from_abi("MultiSig", multiSigAddress, MultiSigWallet.abi, owner=acct)

    setFeeAndMinPerTokenData = allowTokens.setFeeAndMinPerToken.encode_input(token, feeConst, minAmount)
    print(setFeeAndMinPerTokenData)

    print(f'Setting fee and min amount for token {token}')
    tx = multiSig.submitTransaction(allowTokens.address, 0, setFeeAndMinPerTokenData)
    txId = tx.events["Submission"]["transactionId"]
    print(txId)

def allowToken(token):
    abiFileBridge =  open('./scripts/contractInteraction/bridge-multisig/Bridge.json')
    abiFileAllowTokens =  open('./scripts/contractInteraction/bridge-multisig/AllowTokens.json')
    abiBridge = json.load(abiFileBridge)
    abiAllowTokens = json.load(abiFileAllowTokens)
    #tokenContract = Contract.from_abi("Token", address=token, abi=TestToken.abi, owner=acct)
    
    bridgeRSK = Contract.from_abi("BridgeRSK", address=contracts['BridgeRSK'], abi=abiBridge, owner=acct)
    
    multisig = Contract.from_abi("MultiSig", address=contracts['multisig'], abi=MultiSigWallet.abi, owner=acct)

    allowTokensAddress = bridgeRSK.allowTokens()
    allowTokens = Contract.from_abi("AllowTokens", address=allowTokensAddress, abi=abiAllowTokens, owner=acct)
    print(f"Configuring AllowTokens contract {allowTokens.address}")

    multiSigAddress = allowTokens.owner()
    print('multisig address: ' + multiSigAddress)
    multiSig = Contract.from_abi("MultiSig", multiSigAddress, MultiSigWallet.abi, owner=acct)

    addAllowTokenData = allowTokens.addAllowedToken.encode_input(token)
    print(addAllowTokenData)

    print(f'Allowing token {token}')
    tx = multiSig.submitTransaction(allowTokens.address, 0, addAllowTokenData)
    txId = tx.events["Submission"]["transactionId"]
    print(txId)
def sendTokensToETHFromMultisig(token, receiver, amount):
    abiFile =  open('./scripts/contractInteraction/bridge-multisig/Bridge.json')
    abi = json.load(abiFile)
    tokenContract = Contract.from_abi("Token", address=token, abi=TestToken.abi, owner=acct)

    multisig = Contract.from_abi("MultiSig", address=contracts['multisig'], abi=MultiSigWallet.abi, owner=acct)
    BridgeRSK = Contract.from_abi("BridgeRSK", address=contracts['BridgeRSK'], abi=abi, owner=acct)
    
    data = tokenContract.approve.encode_input(BridgeRSK.address, amount)
    print(data)
    tx = multisig.submitTransaction(token,0,data)
    txId = tx.events["Submission"]["transactionId"]
    print(txId)
    
    data = BridgeRSK.receiveTokensAt.encode_input(token, amount, receiver, b'')
    print(data)
    tx = multisig.submitTransaction(BridgeRSK.address,0,data)
    txId = tx.events["Submission"]["transactionId"]
    print(txId)

def sendTokensFromWallet(token, receiver, amount):
    abiFile =  open('./scripts/contractInteraction/bridge-multisig/Bridge.json')
    abi = json.load(abiFile)
    tokenContract = Contract.from_abi("Token", address=token, abi=TestToken.abi, owner=acct)

    BridgeRSK = Contract.from_abi("BridgeRSK", address=contracts['BridgeRSK'], abi=abi, owner=acct)
    tokenContract.approve(BridgeRSK.address, amount)
    BridgeRSK.receiveTokensAt(token, amount, receiver, b'')

def sendTokensFromBridgeETHMultisig(token, amount):
    abiFile =  open('./scripts/contractInteraction/bridge-multisig/Bridge.json')
    abi = json.load(abiFile)
    bridgeETH = Contract.from_abi("BridgeETH", address=contracts['BridgeETH'], abi=abi, owner=acct)
    bridgeETHMultisig = Contract.from_abi("MultiSig", address=contracts['BridgeETHMultisig'], abi=MultiSigWallet.abi, owner=acct)

    aggregator = contracts['Aggregator-ETH-RSK']
    receiver = contracts['multisig']

    data = bridgeETH.receiveTokensAt.encode_input(token, amount, aggregator, receiver)
    print(data)
    tx = bridgeETHMultisig.submitTransaction(bridgeETH.address,0,data)
    txId = tx.events["Submission"]["transactionId"]
    print(txId)

def sendAggregatedTokensFromExchequer(basset, masset, receiver, amount):
    abiFile =  open('./scripts/contractInteraction/bridge-multisig/Masset.json')
    abi = json.load(abiFile)
    masset = Contract.from_abi("Masset", address=masset, abi=abi, owner=acct)

    data = masset.redeemToBridge.encode_input(basset, amount, receiver)
    print(data)
    print(contracts['multisig'])
    multisig = Contract.from_abi("MultiSig", address=contracts['multisig'], abi=MultiSigWallet.abi, owner=acct)
    tx = multisig.submitTransaction(masset.address,0,data)
    txId = tx.events["Submission"]["transactionId"]
    print(txId)

def sendAggregatedTokensFromWallet(basset, masset, receiver, amount):
    abiFile =  open('./scripts/contractInteraction/bridge-multisig/Masset.json')
    abi = json.load(abiFile)
    masset = Contract.from_abi("Masset", address=masset, abi=abi, owner=acct)

    masset.redeemToBridge(basset, amount, receiver)

def sendTokensFromWalletFromSepolia(token, receiver, amount):
    abiFile =  open('./scripts/contractInteraction/bridge-multisig/Bridge.json')
    abi = json.load(abiFile)
    tokenContract = Contract.from_abi("Token", address=token, abi=TestToken.abi, owner=acct)

    Bridge = Contract.from_abi("bridge", address=contracts['bridge'], abi=abi, owner=acct)
    tokenContract.approve(Bridge.address, amount)
    Bridge.receiveTokensAt(token, amount, receiver, b'')