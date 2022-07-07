// SPDX-License-Identifier: MIT
pragma solidity 0.5.17;

interface IFunctionsList {
    function getFunctionList() external pure returns (bytes4[] memory functionSignatures);
}
