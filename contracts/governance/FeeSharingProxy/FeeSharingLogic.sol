pragma solidity ^0.5.17;

import "../Staking/SafeMath96.sol";
import "../../openzeppelin/SafeMath.sol";
import "../../openzeppelin/SafeERC20.sol";
import "../../openzeppelin/Ownable.sol";
import "../IFeeSharingProxy.sol";
import "../../openzeppelin/Address.sol";
import "./FeeSharingProxyStorage.sol";
import "../../interfaces/IConverterAMM.sol";

/**
 * @title The FeeSharingLogic contract.
 * @notice Staking is not only granting voting rights, but also access to fee
 * sharing according to the own voting power in relation to the total. Whenever
 * somebody decides to collect the fees from the protocol, they get transferred
 * to a proxy contract which invests the funds in the lending pool and keeps
 * the pool tokens.
 *
 * The fee sharing proxy will be set as feesController of the protocol contract.
 * This allows the fee sharing proxy to withdraw the fees. The fee sharing
 * proxy holds the pool tokens and keeps track of which user owns how many
 * tokens. In order to know how many tokens a user owns, the fee sharing proxy
 * needs to know the user’s weighted stake in relation to the total weighted
 * stake (aka total voting power).
 *
 * Because both values are subject to change, they may be different on each fee
 * withdrawal. To be able to calculate a user’s share of tokens when he wants
 * to withdraw, we need checkpoints.
 *
 * This contract is intended to be set as the protocol fee collector.
 * Anybody can invoke the withdrawFees function which uses
 * protocol.withdrawFees to obtain available fees from operations on a
 * certain token. These fees are deposited in the corresponding loanPool.
 * Also, the staking contract sends slashed tokens to this contract. When a
 * user calls the withdraw function, the contract transfers the fee sharing
 * rewards in proportion to the user’s weighted stake since the last withdrawal.
 *
 * The protocol is collecting fees in all sorts of currencies and then automatically
 * supplies them to the respective lending pools. Therefore, all fees are
 * generating interest for the SOV holders. If one of them withdraws fees, it will
 * get pool tokens. It is planned to add the option to convert anything to rBTC
 * before withdrawing, but not yet implemented.
 * */
contract FeeSharingLogic is SafeMath96, IFeeSharingProxy, Ownable, FeeSharingProxyStorage {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    /* Events */

    /// @notice An event emitted when fee get withdrawn.
    event FeeWithdrawn(address indexed sender, address indexed token, uint256 amount);

    /// @notice An event emitted when tokens transferred.
    event TokensTransferred(address indexed sender, address indexed token, uint256 amount);

    /// @notice An event emitted when checkpoint added.
    event CheckpointAdded(address indexed sender, address indexed token, uint256 amount);

    /// @notice An event emitted when user fee get withdrawn.
    event UserFeeWithdrawn(
        address indexed sender,
        address indexed receiver,
        address indexed token,
        uint256 amount
    );

    /**
     * @notice An event emitted when fee from AMM get withdrawn.
     *
     * @param sender sender who initiate the withdrawn amm fees.
     * @param converter the converter address.
     * @param amount total amount of fee (Already converted to WRBTC).
     */
    event FeeAMMWithdrawn(address indexed sender, address indexed converter, uint256 amount);

    /// @notice An event emitted when converter address has been registered to be whitelisted.
    event WhitelistedConverter(address indexed sender, address converter);

    /// @notice An event emitted when converter address has been removed from whitelist.
    event UnwhitelistedConverter(address indexed sender, address converter);

    event RBTCWithdrawn(address indexed sender, address indexed receiver, uint256 amount);

    /* Functions */

    /// @dev fallback function to support rbtc transfer when unwrap the wrbtc.
    function() external payable {
        IWrbtcERC20 wRBTCToken = protocol.wrbtcToken();
        require(
            msg.sender == address(wRBTCToken),
            "FeeSharingProxy::fallback: only allowed wrbtc"
        );
    }

    /**
     * @notice Withdraw fees for the given token:
     * lendingFee + tradingFee + borrowingFee
     * the fees (except SOV) will be converted in wRBTC form, and then will be transferred to wRBTC loan pool.
     * For SOV, it will be directly deposited into the feeSharingProxy from the protocol.
     *
     * @param _tokens array address of the token
     * */
    function withdrawFees(address[] memory _tokens) public {
        for (uint256 i = 0; i < _tokens.length; i++) {
            require(
                Address.isContract(_tokens[i]),
                "FeeSharingProxy::withdrawFees: token is not a contract"
            );
        }

        uint256 wrbtcAmountWithdrawn = protocol.withdrawFees(_tokens, address(this));

        IWrbtcERC20 wRBTCToken = protocol.wrbtcToken();
        require(
            address(wRBTCToken) != address(0),
            "FeeSharingProxy::withdrawFees: wRBTCAddress is not set"
        );

        if (wrbtcAmountWithdrawn > 0) {
            // unwrap the wrbtc to rbtc, and hold the rbtc.
            wRBTCToken.withdraw(wrbtcAmountWithdrawn);

            /// @notice Update unprocessed amount of tokens
            uint96 amount96 =
                safe96(
                    wrbtcAmountWithdrawn,
                    "FeeSharingProxy::withdrawFees: wrbtc token amount exceeds 96 bits"
                );

            _addCheckpoint(address(0), amount96);
        }

        emit FeeWithdrawn(msg.sender, address(0), wrbtcAmountWithdrawn);
    }

    /**
     * @notice Withdraw amm fees for the given converter addresses:
     * protocolFee from the conversion
     * the fees will be converted in wRBTC form, and then will be transferred to wRBTC loan pool
     *
     * @param _converters array addresses of the converters
     * */
    function withdrawFeesAMM(address[] memory _converters) public {
        IWrbtcERC20 wRBTCToken = protocol.wrbtcToken();
        require(
            address(wRBTCToken) != address(0),
            "FeeSharingProxy::withdrawFees: wRBTCAddress is not set"
        );

        // Validate
        _validateWhitelistedConverter(_converters);

        uint96 totalPoolTokenAmount;
        for (uint256 i = 0; i < _converters.length; i++) {
            uint256 wrbtcAmountWithdrawn =
                IConverterAMM(_converters[i]).withdrawFees(address(this));

            if (wrbtcAmountWithdrawn > 0) {
                // unwrap wrbtc to rbtc, and hold the rbtc
                wRBTCToken.withdraw(wrbtcAmountWithdrawn);

                /// @notice Update unprocessed amount of tokens
                uint96 amount96 =
                    safe96(
                        wrbtcAmountWithdrawn,
                        "FeeSharingProxy::withdrawFeesAMM: wrbtc token amount exceeds 96 bits"
                    );

                totalPoolTokenAmount = add96(
                    totalPoolTokenAmount,
                    amount96,
                    "FeeSharingProxy::withdrawFeesAMM: total wrbtc token amount exceeds 96 bits"
                );

                emit FeeAMMWithdrawn(msg.sender, _converters[i], wrbtcAmountWithdrawn);
            }
        }

        if (totalPoolTokenAmount > 0) {
            _addCheckpoint(address(0), totalPoolTokenAmount);
        }
    }

    /**
     * @notice Transfer tokens to this contract.
     * @dev We just update amount of tokens here and write checkpoint in a separate methods
     * in order to prevent adding checkpoints too often.
     * @param _token Address of the token.
     * @param _amount Amount to be transferred.
     * */
    function transferTokens(address _token, uint96 _amount) public {
        require(_token != address(0), "FeeSharingProxy::transferTokens: invalid address");
        require(_amount > 0, "FeeSharingProxy::transferTokens: invalid amount");

        // if _token is wrbtc, need to unwrap it to rbtc
        IWrbtcERC20 wrbtcToken = protocol.wrbtcToken();
        require(
            address(wrbtcToken) != address(0),
            "FeeSharingProxy::withdraw: wRBTCAddress is not set"
        );
        if (_token == address(wrbtcToken)) {
            wrbtcToken.withdraw(_amount);
            _token = address(0);
        } else {
            /// @notice Transfer tokens from msg.sender
            bool success =
                IERC20(_token).transferFrom(address(msg.sender), address(this), _amount);
            require(success, "Staking::transferTokens: token transfer failed");
        }

        _addCheckpoint(_token, _amount);

        emit TokensTransferred(msg.sender, _token, _amount);
    }

    /**
     * @notice Transfer RBTC / native tokens to this contract.
     * @dev We just write checkpoint here (based on the rbtc value that is sent) in a separate methods
     * in order to prevent adding checkpoints too often.
     * */
    function transferRBTC() external payable {
        uint96 _amount = uint96(msg.value);
        require(_amount > 0, "FeeSharingProxy::transferRBTC: invalid value");

        _addCheckpoint(address(0), _amount);

        emit TokensTransferred(msg.sender, address(0), _amount);
    }

    /**
     * @notice Add checkpoint with accumulated amount by function invocation.
     * @param _token Address of the token.
     * */
    function _addCheckpoint(address _token, uint96 _amount) internal {
        if (block.timestamp - lastFeeWithdrawalTime[_token] >= FEE_WITHDRAWAL_INTERVAL) {
            lastFeeWithdrawalTime[_token] = block.timestamp;
            uint96 amount =
                add96(
                    unprocessedAmount[_token],
                    _amount,
                    "FeeSharingProxy::_addCheckpoint: amount exceeds 96 bits"
                );

            /// @notice Reset unprocessed amount of tokens to zero.
            unprocessedAmount[_token] = 0;

            /// @notice Write a regular checkpoint.
            _writeTokenCheckpoint(_token, amount);
        } else {
            unprocessedAmount[_token] = add96(
                unprocessedAmount[_token],
                _amount,
                "FeeSharingProxy::_addCheckpoint: unprocessedAmount exceeds 96 bits"
            );
        }
    }

    /**
     * @notice Withdraw accumulated fee to the message sender.
     *
     * The Sovryn protocol collects fees on every trade/swap and loan.
     * These fees will be distributed to SOV stakers based on their voting
     * power as a percentage of total voting power. Therefore, staking more
     * SOV and/or staking for longer will increase your share of the fees
     * generated, meaning you will earn more from staking.
     *
     * This function will directly burnToBTC and use the msg.sender (user) as the receiver
     *
     * @param _loanPoolToken Address of the pool token.
     * @param _maxCheckpoints Maximum number of checkpoints to be processed.
     * @param _receiver The receiver of tokens or msg.sender
     * */
    function withdraw(
        address _loanPoolToken,
        uint32 _maxCheckpoints,
        address _receiver
    ) public nonReentrant {
        /// @dev Prevents processing / checkpoints because of block gas limit.
        require(
            _maxCheckpoints > 0,
            "FeeSharingProxy::withdraw: _maxCheckpoints should be positive"
        );

        address wRBTCAddress = address(protocol.wrbtcToken());
        require(wRBTCAddress != address(0), "FeeSharingProxy::withdraw: wRBTCAddress is not set");

        address loanPoolTokenWRBTC = protocol.underlyingToLoanPool(wRBTCAddress);
        require(
            loanPoolTokenWRBTC != address(0),
            "FeeSharingProxy::withdraw: loan wRBTC not found"
        );

        address user = msg.sender;
        if (_receiver == address(0)) {
            _receiver = msg.sender;
        }

        uint256 amount;
        uint256 end;
        (amount, end) = _getAccumulatedFees(user, _loanPoolToken, _maxCheckpoints);
        require(amount > 0, "FeeSharingProxy::withdrawFees: no tokens for a withdrawal");

        processedCheckpoints[user][_loanPoolToken] = end;

        if (loanPoolTokenWRBTC == _loanPoolToken) {
            // We will change, so that feeSharingProxy will directly burn then loanToken (IWRBTC) to rbtc and send to the user --- by call burnToBTC function
            uint256 loanAmountPaid =
                ILoanTokenWRBTC(_loanPoolToken).burnToBTC(_receiver, amount, false);
        } else {
            // Previously it directly send the loanToken to the user
            require(
                IERC20(_loanPoolToken).transfer(_receiver, amount),
                "FeeSharingProxy::withdraw: withdrawal failed"
            );
        }

        emit UserFeeWithdrawn(msg.sender, _receiver, _loanPoolToken, amount);
    }

    /**
     * @dev withdraw all of the RBTC balance based on particular checkpoints
     *
     * RBTC balance consists of:
     * - rbtc balance
     * - wrbtc balance which will be unwrapped to rbtc
     * - iwrbtc balance which will be unwrapped to rbtc
     *
     */
    function withdrawRBTC(uint32 _maxCheckpoints, address _receiver) external {
        uint256 wrbtcAmount;
        uint256 rbtcAmount;
        uint256 iWrbtcAmount;
        uint256 endRBTC;
        uint256 endWRBTC;
        uint256 endIWRBTC;
        uint256 iWRBTCloanAmountPaid;
        address user = msg.sender;

        IWrbtcERC20 wrbtcToken = protocol.wrbtcToken();
        require(
            address(wrbtcToken) != address(0),
            "FeeSharingProxy::withdraw: wRBTCAddress is not set"
        );

        address loanPoolTokenWRBTC = protocol.underlyingToLoanPool(address(wrbtcToken));
        require(
            loanPoolTokenWRBTC != address(0),
            "FeeSharingProxy::withdraw: loan wRBTC not found"
        );

        if (_receiver == address(0)) {
            _receiver = msg.sender;
        }

        (rbtcAmount, wrbtcAmount, iWrbtcAmount, endRBTC, endWRBTC, endIWRBTC) = _getRBTCBalances(
            user,
            _maxCheckpoints
        );

        processedCheckpoints[user][address(0)] = endRBTC;
        processedCheckpoints[user][address(wrbtcToken)] = endWRBTC;
        processedCheckpoints[user][loanPoolTokenWRBTC] = endIWRBTC;

        // unwrap the wrbtc
        if (wrbtcAmount > 0) wrbtcToken.withdraw(wrbtcAmount);

        // pull out the iWRBTC to rbtc to this feeSharingProxy contract
        if (iWrbtcAmount > 0)
            iWRBTCloanAmountPaid = ILoanTokenWRBTC(loanPoolTokenWRBTC).burnToBTC(
                address(this),
                iWrbtcAmount,
                false
            );

        uint256 totalAmount = rbtcAmount.add(wrbtcAmount).add(iWRBTCloanAmountPaid);
        require(totalAmount > 0, "FeeSharingProxy::withdrawFees: no rbtc for a withdrawal");

        // withdraw everything
        (bool success, ) = _receiver.call.value(totalAmount)("");
        require(success, "FeeSharingProxy::withdrawRBTC: Withdrawal failed");

        emit RBTCWithdrawn(user, _receiver, totalAmount);
    }

    /**
     * @notice Get the accumulated loan pool fee of the message sender.
     * @param _user The address of the user or contract.
     * @param _loanPoolToken Address of the pool token.
     * @return The accumulated fee for the message sender.
     * */
    function getAccumulatedFees(address _user, address _loanPoolToken)
        public
        view
        returns (uint256)
    {
        uint256 amount;
        (amount, ) = _getAccumulatedFees(_user, _loanPoolToken, 0);
        return amount;
    }

    /**
     * @notice Whenever fees are withdrawn, the staking contract needs to
     * checkpoint the block number, the number of pool tokens and the
     * total voting power at that time (read from the staking contract).
     * While the total voting power would not necessarily need to be
     * checkpointed, it makes sense to save gas cost on withdrawal.
     *
     * When the user wants to withdraw its share of tokens, we need
     * to iterate over all of the checkpoints since the users last
     * withdrawal (note: remember last withdrawal block), query the
     * user’s balance at the checkpoint blocks from the staking contract,
     * compute his share of the checkpointed tokens and add them up.
     * The maximum number of checkpoints to process at once should be limited.
     *
     * @param _user Address of the user's account.
     * @param _loanPoolToken Loan pool token address.
     * @param _maxCheckpoints Checkpoint index incremental.
     * */
    function _getAccumulatedFees(
        address _user,
        address _loanPoolToken,
        uint32 _maxCheckpoints
    ) internal view returns (uint256, uint256) {
        if (staking.isVestingContract(_user)) {
            return (0, 0);
        }

        uint256 start = processedCheckpoints[_user][_loanPoolToken];
        uint256 end;

        /// @dev Additional bool param can't be used because of stack too deep error.
        if (_maxCheckpoints > 0) {
            /// @dev withdraw -> _getAccumulatedFees
            end = _getEndOfRange(start, _loanPoolToken, _maxCheckpoints);
            if (start >= end) {
                return (0, end);
            }
        } else {
            /// @dev getAccumulatedFees -> _getAccumulatedFees
            /// Don't throw error for getter invocation outside of transaction.
            if (start >= numTokenCheckpoints[_loanPoolToken]) {
                return (0, numTokenCheckpoints[_loanPoolToken]);
            }
            end = numTokenCheckpoints[_loanPoolToken];
        }

        uint256 amount = 0;
        uint256 cachedLockDate = 0;
        uint96 cachedWeightedStake = 0;
        for (uint256 i = start; i < end; i++) {
            Checkpoint storage checkpoint = tokenCheckpoints[_loanPoolToken][i];
            uint256 lockDate = staking.timestampToLockDate(checkpoint.timestamp);
            uint96 weightedStake;
            if (lockDate == cachedLockDate) {
                weightedStake = cachedWeightedStake;
            } else {
                /// @dev We need to use "checkpoint.blockNumber - 1" here to calculate weighted stake
                /// For the same block like we did for total voting power in _writeTokenCheckpoint
                weightedStake = staking.getPriorWeightedStake(
                    _user,
                    checkpoint.blockNumber - 1,
                    checkpoint.timestamp
                );
                cachedWeightedStake = weightedStake;
                cachedLockDate = lockDate;
            }
            uint256 share =
                uint256(checkpoint.numTokens).mul(weightedStake).div(
                    uint256(checkpoint.totalWeightedStake)
                );
            amount = amount.add(share);
        }
        return (amount, end);
    }

    /**
     * @notice Withdrawal should only be possible for blocks which were already
     * mined. If the fees are withdrawn in the same block as the user withdrawal
     * they are not considered by the withdrawing logic (to avoid inconsistencies).
     *
     * @param start Start of the range.
     * @param _loanPoolToken Loan pool token address.
     * @param _maxCheckpoints Checkpoint index incremental.
     * */
    function _getEndOfRange(
        uint256 start,
        address _loanPoolToken,
        uint32 _maxCheckpoints
    ) internal view returns (uint256) {
        uint256 nCheckpoints = numTokenCheckpoints[_loanPoolToken];
        uint256 end;
        if (_maxCheckpoints == 0) {
            /// @dev All checkpoints will be processed (only for getter outside of a transaction).
            end = nCheckpoints;
        } else {
            if (_maxCheckpoints > MAX_CHECKPOINTS) {
                _maxCheckpoints = MAX_CHECKPOINTS;
            }
            end = safe32(
                start + _maxCheckpoints,
                "FeeSharingProxy::withdraw: checkpoint index exceeds 32 bits"
            );
            if (end > nCheckpoints) {
                end = nCheckpoints;
            }
        }

        /// @dev Withdrawal should only be possible for blocks which were already mined.
        uint32 lastBlockNumber = tokenCheckpoints[_loanPoolToken][end - 1].blockNumber;
        if (block.number == lastBlockNumber) {
            end--;
        }
        return end;
    }

    /**
     * @notice Write a regular checkpoint w/ the foolowing data:
     * block number, block timestamp, total weighted stake and num of tokens.
     * @param _token The pool token address.
     * @param _numTokens The amount of pool tokens.
     * */
    function _writeTokenCheckpoint(address _token, uint96 _numTokens) internal {
        uint32 blockNumber =
            safe32(
                block.number,
                "FeeSharingProxy::_writeCheckpoint: block number exceeds 32 bits"
            );
        uint32 blockTimestamp =
            safe32(
                block.timestamp,
                "FeeSharingProxy::_writeCheckpoint: block timestamp exceeds 32 bits"
            );
        uint256 nCheckpoints = numTokenCheckpoints[_token];

        uint96 totalWeightedStake = _getVoluntaryWeightedStake(blockNumber - 1, block.timestamp);
        require(totalWeightedStake > 0, "Invalid totalWeightedStake");
        if (
            nCheckpoints > 0 &&
            tokenCheckpoints[_token][nCheckpoints - 1].blockNumber == blockNumber
        ) {
            tokenCheckpoints[_token][nCheckpoints - 1].totalWeightedStake = totalWeightedStake;
            tokenCheckpoints[_token][nCheckpoints - 1].numTokens = _numTokens;
        } else {
            tokenCheckpoints[_token][nCheckpoints] = Checkpoint(
                blockNumber,
                blockTimestamp,
                totalWeightedStake,
                _numTokens
            );
            numTokenCheckpoints[_token] = nCheckpoints + 1;
        }
        emit CheckpointAdded(msg.sender, _token, _numTokens);
    }

    /**
     * Queries the total weighted stake and the weighted stake of vesting contracts and returns the difference
     * @param blockNumber the blocknumber
     * @param timestamp the timestamp
     */
    function _getVoluntaryWeightedStake(uint32 blockNumber, uint256 timestamp)
        internal
        view
        returns (uint96 totalWeightedStake)
    {
        uint96 vestingWeightedStake = staking.getPriorVestingWeightedStake(blockNumber, timestamp);
        totalWeightedStake = staking.getPriorTotalVotingPower(blockNumber, timestamp);
        totalWeightedStake = sub96(
            totalWeightedStake,
            vestingWeightedStake,
            "FeeSharingProxy::_getTotalVoluntaryWeightedStake: vested stake exceeds total stake"
        );
    }

    /**
     * @dev Whitelisting converter address.
     *
     * @param converterAddress converter address to be whitelisted.
     */
    function addWhitelistedConverterAddress(address converterAddress) external onlyOwner {
        require(Address.isContract(converterAddress), "Non contract address given");
        whitelistedConverterList.add(converterAddress);
        emit WhitelistedConverter(msg.sender, converterAddress);
    }

    /**
     * @dev Removing converter address from whitelist.
     *
     * @param converterAddress converter address to be removed from whitelist.
     */
    function removeWhitelistedConverterAddress(address converterAddress) external onlyOwner {
        whitelistedConverterList.remove(converterAddress);
        emit UnwhitelistedConverter(msg.sender, converterAddress);
    }

    /**
     * @notice Getter to query all of the whitelisted converter.
     * @return All of the whitelisted converter list.
     */
    function getWhitelistedConverterList() external view returns (address[] memory converterList) {
        converterList = whitelistedConverterList.enumerate();
    }

    /**
     * @dev validate array of given address whether is whitelisted or not.
     * @dev if one of them is not whitelisted, then revert.
     *
     * @param converterAddresses array of converter addresses.
     */
    function _validateWhitelistedConverter(address[] memory converterAddresses) private view {
        for (uint256 i = 0; i < converterAddresses.length; i++) {
            require(whitelistedConverterList.contains(converterAddresses[i]), "Invalid Converter");
        }
    }

    function withdrawWRBTC(address receiver, uint256 wrbtcAmount) external onlyOwner {
        address wRBTCAddress = address(protocol.wrbtcToken());
        require(
            wRBTCAddress != address(0),
            "FeeSharingProxy::withdrawFees: wRBTCAddress is not set"
        );

        uint256 balance = IERC20(wRBTCAddress).balanceOf(address(this));
        require(wrbtcAmount <= balance, "Insufficient balance");

        IERC20(wRBTCAddress).safeTransfer(receiver, wrbtcAmount);
    }

    /**
     * @dev view function that calculate the total RBTC that includes:
     * - RBTC
     * - WRBTC
     * - iWRBTC * iWRBTC.tokenPrice()
     * @param _user address of the user.
     * @return rbtc balance of the given user's address.
     */
    function getAccumulatedRBTCFeeBalances(address _user) external view returns (uint256) {
        uint256 _rbtcAmount;
        uint256 _wrbtcAmount;
        uint256 _iWrbtcAmount;
        (_rbtcAmount, _wrbtcAmount, _iWrbtcAmount, , , ) = _getRBTCBalances(_user, 0);
        return _rbtcAmount.add(_wrbtcAmount).add(_iWrbtcAmount);
    }

    /**
     * @dev private function that responsible to calculate the user's token that has RBTC as underlying token (rbtc, wrbtc, iWrbtc)
     *
     * @param _user address of the user.
     * @param _maxCheckpoints maximum checkpoints.
     *
     * @return _rbtcAmount rbtc amount
     * @return _wrbtcAmount wrbtc amount
     * @return _iWrbtcAmount iWrbtc (wrbtc lending pool token) amount * token price
     * @return _endRBTC end time of accumulated fee calculation for rbtc
     * @return _endWRBTC end time of accumulated fee calculation for wrbtc
     * @return _endIWRBTC end time of accumulated fee calculation for iwrbtc
     */
    function _getRBTCBalances(address _user, uint32 _maxCheckpoints)
        private
        view
        returns (
            uint256 _rbtcAmount,
            uint256 _wrbtcAmount,
            uint256 _iWrbtcAmount,
            uint256 _endRBTC,
            uint256 _endWRBTC,
            uint256 _endIWRBTC
        )
    {
        IWrbtcERC20 wrbtcToken = protocol.wrbtcToken();
        require(
            address(wrbtcToken) != address(0),
            "FeeSharingProxy::withdrawFees: wRBTCAddress is not set"
        );

        address loanPoolTokenWRBTC = protocol.underlyingToLoanPool(address(wrbtcToken));
        require(
            loanPoolTokenWRBTC != address(0),
            "FeeSharingProxy::withdraw: loan wRBTC not found"
        );

        (_rbtcAmount, _endRBTC) = _getAccumulatedFees(_user, address(0), _maxCheckpoints);
        (_wrbtcAmount, _endWRBTC) = _getAccumulatedFees(
            _user,
            address(wrbtcToken),
            _maxCheckpoints
        );
        (_iWrbtcAmount, _endIWRBTC) = _getAccumulatedFees(
            _user,
            loanPoolTokenWRBTC,
            _maxCheckpoints
        );

        _iWrbtcAmount = _iWrbtcAmount.mul(ILoanTokenWRBTC(loanPoolTokenWRBTC).tokenPrice());
    }
}

/* Interfaces */
interface ILoanToken {
    function mint(address receiver, uint256 depositAmount) external returns (uint256 mintAmount);
}

interface ILoanTokenWRBTC {
    function burnToBTC(
        address receiver,
        uint256 burnAmount,
        bool useLM
    ) external returns (uint256 loanAmountPaid);

    function tokenPrice() external view returns (uint256 price);
}
