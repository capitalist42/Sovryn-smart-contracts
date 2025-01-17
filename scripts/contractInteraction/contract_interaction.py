
'''
This script serves the purpose of interacting with existing smart contracts on the testnet or mainnet.
'''
from scripts.contractInteraction.contract_interaction_imports import *

def main():
    '''
    run from CLI:
    brownie run scripts/contractInteraction/contract_interaction.py --network testnet
    brownie run scripts/contractInteraction/contract_interaction.py --network rsk-mainnet
    
    #####################################################################################
    
    run on forked nets:
    1) run a forked net at a block 
    * if forking at the last block don't use --fork-block-number option
    * use --no-deploy param to skip running hh deployment scripts by default 
    
    mainnet: 
    npx hardhat node --fork https://mainnet-dev.sovryn.app/rpc --no-deploy --fork-block-number 4929553
    
    testnet:   
    npx hardhat node --fork https://testnet.sovryn.app/rpc --no-deploy --fork-block-number 3495000

    2) run the script respectively:
    export DEV_NET_NAME="testnet" && brownie run scripts/contractInteraction/contract_interaction.py --network development
    export DEV_NET_NAME="mainnet" && brownie run scripts/contractInteraction/contract_interaction.py --network development
    '''

    # call the function you want here
    
    ##################################
    #addWhitelistConverterFeeSharingCollectorProxy(conf.contracts['ConverterPOWA'])

    #getExchequerBalances()
    # transferOwnershipFromMultisig(conf.contracts['ConverterPOWA'], conf.contracts['TimelockOwner'])
    # transferOwnershipFromMultisig(conf.contracts['POWAPoolOracle'], conf.contracts['TimelockAdmin'])
    #printV1ConverterData('0x4531DD0f24D204c08b251084E12ce3D3e70Dd03e')
    #printV1ConverterData('0xe81373285eb8cdee2e0108e98c5aa022948da9d2')
    #getLMInfo()
    #getPoolInfo(conf.contracts['LiquidityMiningConfigToken'])
    #getPoolInfo(conf.contracts['(WR)BTC/POWA'])
    # rbtcBalance = 1.2235*10**18
    # powaBalance = 29071399974.7820*10**18 
    # product = powaBalance * rbtcBalance
    # amount = 1000 *1e18
    # getTargetAmountFromAMM(sovBalance, 50000, rbtcBalance, 50000, amount)

    #sendTokensFromMultisig(conf.contracts['POWA'], '0x8510fe153b9e6fabee709d75bf0a864cd27d7593', 683101993102460714498381053952)
    #printV1ConverterData(conf.contracts['ConverterPOWA'])
    #addLiquidityV1FromMultisigUsingWrapper(conf.contracts['RBTCWrapperProxyWithoutLM'], conf.contracts['ConverterPOWA'], [conf.contracts['WRBTC'], conf.contracts['POWA']], [1.2235*10**18,29071399974.7820*10**18], 1)

    #addOwnerToAnyMultisig('0x37a706259F5201c03f6Cb556A960f30F86842D01','0x13Be55487D37FE3C66EE7305e1e9C1ac85de75Ae') # BF
    #removeOwnerFromAnyMultisig('0x37a706259F5201c03f6Cb556A960f30F86842D01','0x9E0816a71B53ca67201a5088df960fE90910DE55') # BF
    #cancelTeamVestingsOfAccount('0x673b37941AB527e0EEe13C1Ff09298ef1911d7D6', 1703845695)
    #cancelTeamVestingsOfAccount('0x56B00ca0a274fB53449fBF2DB0253B809E364975')

    #getReleaseScheduleFromDevelopmentFund()
    #getReleaseScheduleFromAdoptionFund()

    # transferProtocolAdminRoleToGovernance()

    # iDLLR
    # print("Transferring iDLLR admin to: ", conf.contracts['TimelockAdmin'])
    # loanToken = Contract.from_abi("loanToken", address=conf.contracts['iDLLR'], abi=LoanTokenSettingsLowerAdmin.abi, owner=conf.acct)
    # data = loanToken.setAdmin.encode_input(conf.contracts['TimelockAdmin'])
    # sendWithMultisig(conf.contracts['multisig'], loanToken.address, data, conf.acct)

    # # iDLLR
    # loanToken = Contract.from_abi("loanToken", address=conf.contracts['iDLLR'], abi=LoanTokenLogicStandard.abi, owner=conf.acct)
    # print("Transferring iDLLR ownserhip to: ", conf.contracts['TimelockOwner'])
    # data = loanToken.transferOwnership.encode_input(conf.contracts['TimelockOwner'])
    # sendWithMultisig(conf.contracts['multisig'], loanToken.address, data, conf.acct)
    #used often:

    #### GET DLLR ####
    ## 2 options by priority
    #getTotalSupply(conf.contracts["iDLLR"])
    #amount = 105000e18

    # either from watcher or from XUSD #
    ## 1) from watcher
    # withdrawTokensFromWatcher(conf.contracts["DLLR"], amount, conf.contracts["multisig"])
    ## 2) XUSD -> DLLR 
    # withdrawTokensFromWatcher(conf.contracts["XUSD"], amount, conf.contracts["multisig"])
    ## 2.1) redeem to a multisig 
    #redeemFromAggregatorWithMS(conf.contracts['XUSDAggregatorProxy'], conf.contracts['DLLR'], amount)
    ## 2.2) redeem to an arbitrary address
    # redeemFromAggregatorWithMsTo(conf.contracts['XUSDAggregatorProxy'], conf.contracts['DLLR'], amount, '0x2064242b697830535a2d76be352e82cf85e0ec2c')
    #sendTokensFromMultisig(conf.contracts['DLLR'], '0x2064242b697830535a2d76be352e82cf85e0ec2c', amount)

    #lendToPoolWithMS(conf.contracts["iDLLR"], conf.contracts["DLLR"], amount)

    #printV1ConverterData("0xa9c3d9681215ef7623dc28ea6b75bf87fdf285d9")
    #print("from testnet_contracts:")
    #printV1ConverterData("0xD877fd00ECF08eD78BF549fbc74bac3001aBBb07")
    
    #printLendingPoolsData()

    #withdrawRBTCFromWatcher(30e18, conf.contracts['multisig'])
    
    #print("fastBTCBiDi.balance()", loadBiDiFastBTC().balance()/1e18)
    #print("getFastBTCOfframpAvailableBalance()", getFastBTCOfframpAvailableBalance()/1e18)
    #withdrawRBTCFromFastBTCBiDi(25e18, '0xD9ECB390a6a32ae651D5C614974c5570c50A5D89')
    #withdrawRBTCFromFastBTCBiDi(30e18, conf.contracts['multisig'])
    #readPauser(conf.contracts['iXUSD'])
    #getBalance(conf.contracts['DLLR'], '0xAc2D05a148Ab512EDEdc7280C00292ed33D31F1a') ## testnet
    #transferTokensFromWallet(conf.contracts['DLLR'], '0xae2a6e86d5f5d534fb372693b0ccda8d0ba9744d', 40e18)
    #redeemFromAggregator('0xAc2D05a148Ab512EDEdc7280C00292ed33D31F1a', conf.contracts['ZUSD'], 40e18) ## testnet
    #mintAggregatedToken('0xAc2D05a148Ab512EDEdc7280C00292ed33D31F1a', conf.contracts['ZUSD'], 1e18)  ## testnet
    #bal = getBalance(conf.contracts['SOV'], conf.contracts['Watcher'])
    #bal = getBalance(conf.contracts['FastBTCBiDi'], conf.contracts['Watcher'])
    #print(getContractBTCBalance(conf.contracts['multisig'])/1e18)
    #print(getBalanceNoPrintOf(conf.contracts['WRBTC'], conf.contracts["Watcher"])/1e18)
    #withdrawTokensFromWatcher(conf.contracts['XUSD'], 750000e18, conf.contracts['multisig'])
    #withdrawTokensFromWatcher(conf.contracts['USDT'], 150000e18, conf.contracts['multisig'])

    #sendTokensFromMultisig(conf.contracts['XUSD'], conf.contracts['Watcher'], 300000e18)
    #sendTokensFromMultisig(conf.contracts['SOV'], '0x4f3948816785e30c3378eD3b9F2de034e3AE2E97', 250000e18)
    #sendFromMultisig(conf.contracts['GenericTokenSender'], 0.014e18)
    #sendFromMultisig('0xc0AAcbDB9Ce627A348B91CfDB67eC6b2FBC3dCbd', 0.1e18)
    #sendFromMultisig(conf.contracts['FastBTC'], 6e18)
    #sendFromMultisig('0xD9ECB390a6a32ae651D5C614974c5570c50A5D89', 30e18)
    #sendFromMultisig('0x986c65fc1783a445ceccade74234dc8627d429d8', 0.1e18) #FastBTC on-ramp master node

    #withdrawRBTCFromIWRBTC('0x9BD6759F6D9eA15D33076e55d4CBba7cf85877A7', 1.6e18)
    #sendMYNTFromMultisigToFeeSharingCollector(36632.144056847e18)
    #confirmWithBFMS(28)
    #checkTxOnBF(28)

    #pauseBiDiFastBTC()
    #unpauseBiDiFastBTC()
    #isBiDiFastBTCPaused()

    #setupTorqueLoanParams(conf.contracts['iBPro'], conf.contracts['BPro'], conf.contracts['DLLR'], Wei("50 ether"))

    #triggerEmergencyStop(conf.contracts['iDLLR'], False)

    #readDemandCurve(conf.contracts['iXUSD'])
    #deployLoanToken(conf.contracts['DLLR'], 'iDLLR', 'iDLLR', 6000000000000000000,15000000000000000000, 75000000000000000000, 150000000000000000000, [conf.contracts['WRBTC'], conf.contracts['SOV'], conf.contracts['BPro']])
    #lendToPool(conf.contracts['iDLLR'], conf.contracts['DLLR'], 5000e18)
    #buyWRBTC(0.5e18)
    #testBorrow(conf.contracts['sovrynProtocol'], conf.contracts['iDLLR'], conf.contracts['DLLR'], conf.contracts['SOV'], 100e18)
    #buyWRBTC(2.5e18)
    #setPriceFeed(conf.contracts['DLLR'], '0xEd80Ccde8bAeFf2dBFC70d3028a27e501Fa0D7D5')
    #withdrawTokensFromWatcher(conf.contracts['XUSD'], amount, conf.contracts['multisig'])
    #sendMYNTFromMultisigToFeeSharingCollector(36632.144056847e18)
    
    ### BF ###
    #confirmWithAnyMS(8, conf.contracts["BFMultisigOrigins"])
    #checkTxOnAny(8, conf.contracts["BFMultisigOrigins"])
    
    #confirmWithAnyMS(8, conf.contracts["BFMultisigToken"])
    #checkTxOnAny(8, conf.contracts["BFMultisigToken"])
    
    #confirmWithAnyMS(8, conf.contracts["BFMultisigDeposit"])
    #checkTxOnAny(8, conf.contracts["BFMultisigDeposit"])
    
    #for i in range(13,17):
    #confirmWithAnyMS(17, conf.contracts["NewMultisigBF"])
    #checkTxOnAny(17, conf.contracts["NewMultisigBF"])
    #queueProposal(30)

    #confirmWithBFMS(36) # "BFmultisig"
    #checkTxOnBF(36)   # "BFmultisig"

    #confirmWithBFMS(32)

    #sendToWatcher(conf.contracts['DLLR'], 70000e18)
    #transferTokensFromWallet(conf.contracts['DLLR'], '0x1bB2b1BeeDa1fB25EE5DA9caE6c0F12ced831128', 10000e18)
    #testTradeOpeningAndClosing(conf.contracts['sovrynProtocol'], conf.contracts['iDLLR'], conf.contracts['DLLR'], conf.contracts['WRBTC'], 100e18, 2e18, False, 0)
    #tokenIsSupported(conf.contracts['DLLR'])
    #tokenIsSupported(conf.contracts['WRBTC'])
    #setSupportedTokens([conf.contracts['DLLR']], [True])
    #testTradeOpeningAndClosing(conf.contracts['sovrynProtocol'], conf.contracts['iDLLR'], conf.contracts['DLLR'], conf.contracts['WRBTC'], 50e18, 2e18, True, 0)
    #testTradeOpeningAndClosingWithCollateral(conf.contracts['sovrynProtocol'], conf.contracts['iDLLR'], conf.contracts['DLLR'], conf.contracts['WRBTC'], 0.002e18, 2e18, True, 0.002e18)

    #executeOnMultisig(1339)
    #executeOnMultisig(1343)
    #confirmWithMS(1540)
    #checkTx(1540)
    #checkTx(1407)
    #checkTx(1408)
   
    #addAmmPoolTokenToLM('(WR)BTC/DLLR')

    #hasApproval(conf.contracts['DLLR'], conf.contracts['multisig'], conf.contracts['RBTCWrapperProxyWithoutLM'])


    #distributeMissedFees()
    '''
    getFeeSharingState(conf.contracts['SOV'])
    getFeeSharingState(conf.contracts['ZUSD'])
    getFeeSharingState(conf.contracts['iRBTC'])
    getFeeSharingState(RBTC_DUMMY_ADDRESS_FOR_CHECKPOINT())
    '''
    #readOwner(conf.contracts['FeeSharingCollectorProxy'])
    #setMaxTransferSatoshi(300000000)
    #bal = getBalance(conf.contracts['iRBTC'], conf.contracts['multisig'])
    #transferTokens(conf.contracts['iRBTC'], bal)

    #MULTIPLE TXS CONFIRM & CHECK - the range is exact tx ids boundaries numbers
    #confirmMultipleTxsWithMS(1511, 1513)

    #mintAggregatedToken(conf.contracts['XUSDAggregatorProxy'], conf.contracts['USDT'], 1e18)

    #setupMarginLoanParams(conf.contracts['SOV'], conf.contracts['iXUSD'])
    #readOwner(conf.contracts['iXUSD'])
    
    #missed = getMissedBalance()
    #transferSOVtoLM(missed)

    #sendTokensFromMultisig(conf.contracts['SOV'], conf.contracts['StakingRewardsProxy'], 430000e18)
    #revokeConfirmation(1075)

    #withdrawFees()
    #readFeesController()
    #setFeesController(conf.contracts['FeeSharingCollectorProxy1DayStaking'])

    #revokeConfirmationMS(txId)
    #bal = getFastBTCOfframpAvailableBalance()
    #print('FastBTC offramp balance:', bal/10**18)
    #print('Multisig balance:', getContractBTCBalance(conf.contracts['multisig'])/1e18)

    #transferRBTCFromFastBTCOffRampToOnRamp(bal)
    #withdrawRBTCFromWatcher(6e18, conf.contracts['FastBTC'])
    #redeemFromAggregatorWithMS(conf.contracts['XUSDAggregatorProxy'], conf.contracts['DLLR'], 16658.600400155126 * 10**18)
    #mintAggregatedTokenWithMS(conf.contracts['DLLRAggregatorProxy'], conf.contracts['ZUSD'], 249999e18)
    #minReturn = getReturnForFirstLiquidityProvisionOnV1([10e18, 250000e18])
    #addLiquidityV1FromMultisigUsingWrapper(conf.contracts['RBTCWrapperProxyWithoutLM'], conf.contracts['ConverterDLLR'], [conf.contracts['WRBTC'], conf.contracts['DLLR']], [0.1e18,2500e18] , 1)
    #acceptOwnershipWithMultisig(conf.contracts['ConverterDLLR'])
    #acceptOwnershipWithMultisig(conf.contracts['ConverterPOWA'])
    #acceptOwnershipWithMultisig(conf.contracts['POWAPoolOracle'])
    #redeemFromAggregator(conf.contracts['XUSDAggregatorProxy'], conf.contracts['DLLR'], 5e18)
    #mintAggregatedToken(conf.contracts['DLLRAggregatorProxy'], conf.contracts['ZUSD'], 5e18) #can be still used if having free ZUSD
    #buyWRBTC(0.0002e18)
    #addLiquidityV1( conf.contracts['ConverterDLLR'], [conf.contracts['WRBTC'], conf.contracts['DLLR']], [0.0002e18,5e18])

    #addLiquidityV1FromMultisigUsingWrapper(conf.contracts['RBTCWrapperProxyWithoutLM'], conf.contracts['ConverterDLLR'], [conf.contracts['WRBTC'], conf.contracts['DLLR']], [9.9e18,247500e18] , 490e18)


    #sendTokensFromMultisig(conf.contracts['DLLR'], '0x13Be55487D37FE3C66EE7305e1e9C1ac85de75Ae', 100e18)

    #bal = getBalance(conf.contracts['(WR)BTC/ETH'], conf.contracts['multisig'])
    #removeLiquidityV1toMultisigUsingWrapper(conf.contracts['RBTCWrapperProxyWithoutLM'], conf.contracts['ConverterBNBs'], 1e18, [conf.contracts['WRBTC'], conf.contracts['BNBs']], [1,1])

    #readMocOracleAddress()

    #bal = getBalance(conf.contracts['(WR)BTC/USDT2'], conf.contracts['multisig'])
    #removeLiquidityV2toMultisig(conf.contracts['ConverterUSDT'], conf.contracts['(WR)BTC/USDT2'], bal, 1)

    #getReturnForV2PoolToken(conf.contracts['ConverterUSDT'], conf.contracts['(WR)BTC/USDT2'], bal)

    #readAllVestingContractsForAddress('0xA6575f1D5Bd6545fBd34BE05259D9d6ae60641f2')
    #getStakes('0x750C49DD9928061Df2224AA81E08Bc4a3c334874')
    #governanceDirectWithdrawVesting('0x750C49DD9928061Df2224AA81E08Bc4a3c334874', conf.contracts['multisig'], 0) // last params is for startFrom arguments

    #addOwnerToMultisig('0x832E1bd30d037d0327F2A0447eD44FB952A9a043')
    #removeOwnerFromMultisig('0x27d55f5668ef4438635bdce0adca083507e77752')

    
    #getVoluntaryWeightedStake()

    #contract = Contract.from_abi("Token", address=conf.contracts['SOV'], abi=LoanToken.abi, owner=conf.acct)
    #balance = contract.balanceOf(conf.acct)
    #print(balance/1e18)

    #setMinTransferSatoshi(100000)
    #addFeeStructure(3,50000,20)
    #setCurrentFeeStructure(3)

    #readTokenOwnerFromFunds()

    #printLendingPoolsData()

    #transferOwnershipFromMultisig(conf.contracts["FourYearVestingFactory"], '0x8C9143221F2b72Fcef391893c3a02Cf0fE84f50b')
    # withdrawSovFromMyntReserved(2000000000000000000000)
    # setupTorqueLoanParams(conf.contracts['iXUSD'], "0x0000000000000000000000000000000000000000", conf.contracts['SOV'], Wei("20 ether"), )
    # checkTx(1344)

def guardiansTransfer():
    ####################################################################
    ### THIS SCRIPT SHOULD RUN STRICTLY AFTER THE SIP-0047 EXECUTION ###
    ####################################################################
    
    # # It is critically important to first transfer pauser role
    setNewContractGuardian() 

def governanceTransferStep1():

    ### THIS SCRIPT SHOULD RUN FIRST TO AVOID EARLY OWNERSHIP TRANSFER WHICH WOULD REQUIRE A SEPARATE SIP ###

    # # ---------- Transfer ownership to gov ----------
    # # core protocol
    transferProtocolAdminRoleToGovernance()

    # # loan token
    transferLoanTokenAdminRoleToGovernance()

    # # Governance
    # # lockedSOV
    transferLockedSOVOwnershipToGovernance()

    # # Staking
    # transferStakingOwnershipToGovernance() -> @todo: SIP to add admin and remove exchequer

    # # VestingRegistry
    addVestingRegistryGovernanceAdmin()

def governanceTransferStep2():
    ####################################################################
    ### THIS SCRIPT SHOULD RUN STRICTLY AFTER THE GUARDIANS TRANSFER ###
    ####################################################################

    # # ---------- Transfer ownership to gov ----------
    # # core protocol
    transferProtocolOwnershipToGovernance()

    # # loan token
    transferBeaconOwnershipToGovernance()
    transferLoanTokenOwnershipToGovernance()

    # # oracles
    transferOracleOwnershipToGovernance()

    # # LM
    transferLiquidityMiningOwnershipToGovernance()

    # # Governance
    # # lockedSOV
    removeExchequerFromLockedSOVAdmin()

    # # Staking
    # transferStakingOwnershipToGovernance() -> requires a SIP

    # # StakingRewards
    transferStakingRewardsOwnershipToGovernance()

    # # VestingRegistry
    # transferVestingRegistryOwnershipToGovernance()

    # getLMInfo()
    transferVestingRegistryOwnershipToGovernance()
