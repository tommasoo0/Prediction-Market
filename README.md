# 🧠 PREDICTION MARKET

## OVERVIEW

This project implements a fully decentralized prediction market on the Algorand blockchain, designed to enable users to trade predictions on future events in a secure, transparent, and trustless environment.

In this implementation, users can:
- Create prediction markets with defined outcomes
- Trade outcome shares using a simple swap mechanism

## OBJECTIVE

The main objective of this project is to design and implement a decentralized prediction market on Algorand, showcasing how blockchain technology can transform traditional financial mechanisms by removing the need for trusted intermediaries.

Specifically, the platform aims to:

- Provide a fully decentralized environment for creating and trading prediction markets without requiring a central authority
- Demonstrate how smart contracts can autonomously manage market operations, from order matching to payouts
- Rely on mechanisms to resolve markets and claim payouts
- Use Algorand Standard Assets (ASA) to tokenize prediction shares and facilitate their trading
- Minimize user costs by leveraging Algorand’s low transaction fees and fast finality

---

### Clone the repository
```bash
git clone https://github.com/tommasoo0/Prediction-Market.git
cd Prediction-Market
```
---

## 📦 Prerequisites

- Python 3.10+
- Docker & Docker Compose
- [Algokit CLI](https://github.com/algorandfoundation/algokit-cli)
- Poetry (`pip install poetry`)
- [Lora](https://lora.algokit.io/localnet)

---

##  📥 APPLICATION LAUNCH

This project is designed to run on an Algorand LocalNet using LORA.
Main smart contract located at **'smart_contracts/prediction_market/contract.py'**

### Steps to launch the prediction market:
1) Run Docker container
2) Start the localnet with '***algokit localnet start***'
3) Compile and generate the artifacts with '***algokit project run build***'
4) Run Lora with '***algokit explore***'
5) Deploy the smart contract to the LocalNet

---

## 📸 Preview

![PM](https://github.com/user-attachments/assets/ea6f7c9c-01f1-45eb-bd8b-c1f4ea216cf6)

---

## ✨ MAIN COMPONENTS IN contract.py

The contract.py file contains the core logic of the prediction market, written using Python and structured around ABI methods and reusable subroutines to maintain modularity and clarity.

- ### create_market()
  Initializes a new prediction market by creating two Algorand Standard Assets (ASA) representing the YES and NO outcomes.
- ### set_order()
  Allows users to submit a purchase order for YES or NO by depositing ALGO into the contract. The orders price and desired quantity, are saved for future matching. The logic follows the limit order book model.
- ### fill_order()
  When compatible YES and NO orders are present, this function matches them and distributes tokens to the users. The matching occurs if the sum of the prices is a multiple of 10.
- ### swap()
  Allows the exchange between YES and NO, the system is designed to operate on an automated liquidity formula that ensures the balance between the two assets remains constant.
- ### close_market()
  Can only be executed by the oracle address. Closes the market and sets the final event outcome (YES or NO), preventing further orders or purchases.
- ### redeem()
  After the market is closed, users can redeem ALGO in exchange for the winning tokens. The contract checks the final outcome and reimburses users based on the amount of YES or NO tokens they hold.


