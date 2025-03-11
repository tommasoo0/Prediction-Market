from algopy import ARC4Contract, Asset, Global, Txn, UInt64, arc4, gtxn, itxn
import algopy


class PredictionMarket(ARC4Contract):
    market_id: UInt64
    question: algopy.String
    description: algopy.String
    yes_asset_id: UInt64  # ID asset per Yes
    no_asset_id: UInt64  # ID asset per No

    # Creazione mercato
    @arc4.abimethod(allow_actions=["NoOp"], create="require")
    def create_market(
        self, market_id: UInt64, question: algopy.String, description: algopy.String
    ) -> None:
        self.market_id = market_id
        self.question = question
        self.description = description
        self.creator = Global.current_application_address

    @arc4.abimethod
    def fund_contract(self, payment_txn: gtxn.PaymentTransaction) -> None:
        assert payment_txn.receiver == Global.current_application_address
        assert payment_txn.amount == UInt64(400_000)  # 0.4 Algo

    @arc4.abimethod
    def create_asset(self) -> None:
        # Yes Asset creation
        yes_creation_tx = itxn.AssetConfig(
            total=100_000,
            decimals=0,
            default_frozen=False,
            unit_name="YES",
            asset_name="buy YES",
            manager=Global.creator_address,
            reserve=Global.creator_address,
            freeze=Global.creator_address,
            clawback=Global.creator_address,
        ).submit()
        self.yes_asset_id = yes_creation_tx.created_asset.id

        # No Asset creation
        no_creation_tx = itxn.AssetConfig(
            total=100_000,
            decimals=0,
            default_frozen=False,
            unit_name="NO",
            asset_name="buy NO",
            manager=Global.creator_address,
            reserve=Global.creator_address,
            freeze=Global.creator_address,
            clawback=Global.creator_address,
        ).submit()
        self.no_asset_id = no_creation_tx.created_asset.id

    @arc4.abimethod
    def get_yes_asset_id(self) -> UInt64:
        return self.yes_asset_id

    @arc4.abimethod
    def get_no_asset_id(self) -> UInt64:
        return self.no_asset_id
