from algopy import ARC4Contract, Account, Global, Txn, UInt64, arc4, gtxn, itxn


class VaultContract(ARC4Contract):

    def __init__(self, main_contract: Account, vault_type: UInt64) -> None:
        self.main_contract = main_contract  # Contratto principale che ha il controllo
        self.vault_type = vault_type  # 1 = YES, 0 = NO

    @arc4.abimethod
    def receive_funds(self, payment_txn: gtxn.PaymentTransaction) -> None:
        """Permette solo depositi, verificando che i fondi arrivino all'indirizzo del vault"""
        assert payment_txn.receiver == Global.current_application_address
        assert payment_txn.amount > UInt64(0)  # Assicura che ci siano fondi

    @arc4.abimethod
    def withdraw_funds(self, receiver: Account, amount: UInt64) -> None:
        """Permette solo al contratto principale di prelevare fondi"""
        assert (
            Txn.sender == self.main_contract
        ), "Solo il contratto principale può prelevare"

        # Esegui il pagamento dal Vault al destinatario
        itxn.Payment(receiver=receiver, amount=amount).submit()
