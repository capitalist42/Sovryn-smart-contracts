## How To
### Run all the forge tests
Make sure you have foundry installed. Follow Installation guide: https://book.getfoundry.sh/getting-started/installation.   
```
forge test
```

### Run a specific test
```
forge test --match-path */staking/StakingStake.t.sol --match-test testFuzz_Withdraw -vvv
```

*-vvv is verbosity level, it is the most optimal if having failing tests*