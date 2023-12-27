# Aptos DeFi Automation Script for Quest Two Campaign

This Python script is crafted specifically for the "Quest Two - Aptos Ecosystem Fundamentals" campaign, streamlining participants' journey through various Decentralized Finance (DeFi) tasks on the Aptos blockchain. It automates the required actions, including staking, swapping, and borrowing, in alignment with the campaign's objectives set by partners like Amnis, Thala, Merkle, Aries, Pontem, PancakeSwap, and SushiSwap.

## Campaign Task Automation Detailed Description

This script is designed to automate each step of the Quest Two campaign on the Aptos blockchain. Here's how it addresses each task:

### 1. Move Dollars
- **Functionality**: The script swaps zUSDC for MOD tokens and then supplies these MOD tokens to Thala’s Stability Pool.
- **Implementation**:
  - Utilizes the `swap_zUSDC_to_MOD` function to exchange zUSDC for MOD.
  - Calls `stake_MOD` to deposit the obtained MOD into Thala’s Stability Pool.

### 2. Learn to Ape on Merkle Trade
- **Functionality**: Leverages the user's zUSDC to conduct leverage trading on the Merkle Trade platform.
- **Implementation**:
  - The script first ensures that the user has zUSDC using `get_coin_value`.
  - Executes leveraged trades through `open_merkle_order` by using the zUSDC as collateral.
  - Note: No actual position will be open despite corect execution

### 3. Stake APT on Amnis
- **Functionality**: Automates the process of staking APT on Amnis Finance.
- **Implementation**:
  - Checks the balance of APT using `get_account_balance`.
  - Converts APT to stAPT and stakes it using `stake_APT`.

### 4. Simple Market Order on Econia
- **Functionality**: Automates the process of registering a market account, depositing zUSDC, and placing a simple market order on Econia.
- **Implementation**:
  - **Market Account Registration**: Utilizes `register_gator_market_account` to register a market account on Econia, preparing for trading.
  - **Deposit zUSDC**: The `deposit_zUSDC_to_gator` function is used to deposit zUSDC into the newly registered market account.
  - **Place Market Order**: Executes a market order trade using `swap_zUSDC_to_APT_via_gator`, which places a simple market order on Econia, completing the task as required by the campaign.

### 5. Token Swap with Pontem’s Liquidswap DEX
- **Functionality**: Executes token swaps on the Liquidswap DEX.
- **Implementation**:
  - Uses `swap_APT_to_zUSDC_via_liquidswap` function modified for Liquidswap DEX to perform the swap.

### 6. Token Swap on PancakeSwap
- **Functionality**: Performs token swaps on PancakeSwap within the Aptos network.
- **Implementation**:
  - The `swap_zUSDC_to_APT_via_pancakeswap` function is used to swap tokens on PancakeSwap.

### 7. Token Swap on SushiSwap
- **Functionality**: Conducts token swaps on SushiSwap on the Aptos network.
- **Implementation**:
  - Uses the `swap_zUSDC_to_APT_via_sushisvap` function to execute swaps on SushiSwap.
