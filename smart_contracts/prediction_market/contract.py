from algopy import (
    Account,
    ARC4Contract,
    Asset,
    Global,
    Txn,
    UInt64,
    arc4,
    BoxMap,  # Importiamo BoxMap
    gtxn,
    itxn,
    subroutine,
)
from typing import Tuple

# quantità totale di token del pool
TOTAL_SUPPLY = 10_000_000_000
# goal asset optin --wallet unencrypted-default-wallet --assetid 1009 --account NB3CGUNBFEL5WIPF4QYRDII4MW3XDXDN257KIFLJVWRUA7TWEFUCYDNUMM


class PredictionMarket(ARC4Contract):

    def __init__(self) -> None:
        self.asset_yes = Asset()
        self.asset_no = Asset()
        self.pool_token = (
            Asset()
        )  # Asset che rappresenta il token del pool di liquidità
        self.ratio = UInt64(0)  # Variabile per mantenere il rapporto tra asset
        # BoxMap per memorizzare gli ordini di acquisto
        self.place_order_yes_price = BoxMap(Account, UInt64, key_prefix=b"yes_price_")
        self.place_order_yes_quantity = BoxMap(
            Account, UInt64, key_prefix=b"yes_quantity_"
        )

        self.place_order_no_price = BoxMap(Account, UInt64, key_prefix=b"no_price_")
        self.place_order_no_quantity = BoxMap(
            Account, UInt64, key_prefix=b"no_quantity_"
        )
        self.matched_yes_price = UInt64(0)  # Prezzo di YES al momento del match
        self.matched_no_price = UInt64(0)  # Prezzo di NO al momento del match

        self.winning_asset: Asset
        self.market_closed = False  # Inizialmente il mercato è aperto

    @arc4.abimethod
    def fund_contract(self, payment_txn: gtxn.PaymentTransaction) -> None:
        assert payment_txn.receiver == Global.current_application_address
        assert payment_txn.amount == UInt64(400_000)  # 0.4 Algo

    @arc4.abimethod
    def create_asset(self) -> None:
        # Yes Asset creation
        yes_txn = itxn.AssetConfig(
            total=100_000,
            decimals=0,
            default_frozen=False,
            unit_name="YES",
            asset_name="YES_asset",
            manager=Global.creator_address,
            reserve=Global.creator_address,
            freeze=Global.creator_address,
            clawback=Global.creator_address,
        ).submit()

        self.asset_yes = Asset(yes_txn.created_asset.id)  # Ora è del tipo corretto

        # No Asset creation
        no_txn = itxn.AssetConfig(
            total=100_000,
            decimals=0,
            default_frozen=False,
            unit_name="NO",
            asset_name="NO_asset",
            manager=Global.creator_address,
            reserve=Global.creator_address,
            freeze=Global.creator_address,
            clawback=Global.creator_address,
        ).submit()

        self.asset_no = Asset(no_txn.created_asset.id)  # Anche questo ora è corretto

    @arc4.abimethod()
    def create_market(
        self, seed: gtxn.PaymentTransaction, yes_asset: Asset, no_asset: Asset
    ) -> UInt64:
        """Inizializza il mercato di previsione con gli asset specificati."""
        # Controlla che il contratto non sia già stato avviato
        assert self.pool_token.id == 0, "Il mercato è già stato creato"

        # Controlla che il gruppo di transazioni sia di dimensione 2
        assert Global.group_size == 2, "gruppo di transazioni non è 2"

        # Verifica che la transazione di funding sia inviata all'indirizzo del contratto
        assert (
            seed.receiver == Global.current_application_address
        ), "receiver non è all'indirizzo del contratto"

        # Controlla che il funding del contratto sia almeno 300.000 microAlgos
        assert seed.amount >= 300_000, "amount minimo non soddisfatto"

        # Assicura che gli asset siano ordinati correttamente (per evitare ambiguità)
        assert yes_asset.id < no_asset.id, "asset yes deve essere minore di asset no"

        # Assegna gli asset al contratto
        self.asset_yes = yes_asset
        self.asset_no = no_asset

        # Crea il token del pool di liquidità
        self.pool_token = self._create_pool_token()

        # Effettua l'opt-in per entrambi gli asset
        self._do_opt_in(self.asset_yes)
        self._do_opt_in(self.asset_no)

        # Ritorna l'ID del token del pool
        return self.pool_token.id

    @arc4.abimethod
    def set_order(
        self,
        order_type: UInt64,
        user: Account,
        price: UInt64,
        quantity: UInt64,
        payment_txn: gtxn.PaymentTransaction,
    ) -> None:
        total_payment = price * quantity  # Importo totale da pagare
        assert payment_txn.sender == user, "Il pagamento deve provenire dall'utente"
        assert (
            payment_txn.receiver == Global.current_application_address
        ), "Il pagamento deve essere inviato al contratto"
        assert payment_txn.amount == total_payment, "L'importo pagato non è corretto"
        if order_type == UInt64(1):
            self.place_order_yes_price[user] = price
            self.place_order_yes_quantity[user] = quantity
        elif order_type == UInt64(0):
            self.place_order_no_price[user] = price
            self.place_order_no_quantity[user] = quantity
        else:
            assert False, "Tipo di ordine non valido"

    @arc4.abimethod
    def get_order(self, order_type: UInt64, user: Account) -> Tuple[UInt64, UInt64]:
        """Recupera un ordine di acquisto dalla BoxMap."""
        if order_type == UInt64(1):
            return self.place_order_yes_price[user], self.place_order_yes_quantity[user]
        elif order_type == UInt64(0):
            return self.place_order_no_price[user], self.place_order_no_quantity[user]
        else:
            assert False, "Tipo di ordine non valido"

    @arc4.abimethod
    def fill_order(
        self,
        yes_user: Account,
        no_user: Account,
    ) -> None:
        assert (
            Txn.sender == Global.creator_address
        ), "Solo il contratto principale può eseguire questa operazione"
        assert yes_user in self.place_order_yes_price, "YES user has no order"
        assert no_user in self.place_order_no_price, "NO user has no order"

        yes_price = self.place_order_yes_price[yes_user]
        yes_quantity = self.place_order_yes_quantity[yes_user]
        no_price = self.place_order_no_price[no_user]
        no_quantity = self.place_order_no_quantity[no_user]

        assert (yes_price + no_price) % UInt64(10) == UInt64(
            0
        ), "Prices don't match condition"
        self.matched_yes_price = yes_price
        self.matched_no_price = no_price
        do_asset_transfer(receiver=yes_user, asset=self.asset_yes, amount=yes_quantity)
        do_asset_transfer(receiver=no_user, asset=self.asset_no, amount=no_quantity)
        del self.place_order_yes_price[yes_user]
        del self.place_order_yes_quantity[yes_user]
        del self.place_order_no_price[no_user]
        del self.place_order_no_quantity[no_user]
        self._update_ratio()

    @arc4.abimethod
    def gas(self) -> None:
        # Funzione vuota per "riempire" le references nel gruppo di transazioni
        pass

    @arc4.abimethod
    def buyAsset(
        self,
        user: Account,
        asset_type: UInt64,
        quantity: UInt64,
        payment_txn: gtxn.PaymentTransaction,
    ) -> None:
        assert (
            self.matched_yes_price > 0 and self.matched_no_price > 0
        ), "Nessun match trovato, impossibile acquistare"

        if asset_type == UInt64(1):  # Asset YES
            price = self.matched_yes_price
            asset_to_buy = self.asset_yes
        elif asset_type == UInt64(0):  # Asset NO
            price = self.matched_no_price
            asset_to_buy = self.asset_no
        else:
            assert False, "Tipo di asset non valido"

        total_cost = price * quantity  # Calcoliamo il costo totale
        assert payment_txn.sender == user, "Il pagamento deve provenire dall'utente"
        assert (
            payment_txn.receiver == Global.current_application_address
        ), "Il pagamento deve essere inviato al contratto"
        assert payment_txn.amount == total_cost, "L'importo pagato non è corretto"
        do_asset_transfer(receiver=user, asset=asset_to_buy, amount=quantity)

    @arc4.abimethod()
    def swap(
        self,
        swap_xfer: gtxn.AssetTransferTransaction,
        yes_asset: Asset,
        no_asset: Asset,
    ) -> None:
        assert yes_asset == self.asset_yes, "asset yes nn corretto"
        assert no_asset == self.asset_no, "asset no nn corretto"
        assert swap_xfer.asset_amount > 0, "amount minimo non raggiunto"
        assert swap_xfer.sender == Txn.sender, "sender invalido"
        match swap_xfer.xfer_asset:
            case self.asset_no:  # Se l'utente invia NO, vuole ricevere YES
                in_supply = self._current_no_balance()  # Pool riceve NO
                out_supply = self._current_yes_balance()  # Pool deve dare YES
                out_asset = self.asset_yes  # Usciranno YES
            case self.asset_yes:  # Se l'utente invia YES, vuole ricevere NO
                in_supply = self._current_yes_balance()  # Pool riceve YES
                out_supply = self._current_no_balance()  # Pool deve dare NO
                out_asset = self.asset_no  # Usciranno NO
            case _:
                assert False, "asset id incorretto"
        to_swap = tokens_to_swap(
            in_amount=swap_xfer.asset_amount,
            in_supply=in_supply,
            out_supply=out_supply,
        )
        assert to_swap > 0, "send amount too low"
        do_asset_transfer(receiver=Txn.sender, asset=out_asset, amount=to_swap)
        self._update_ratio()

    @arc4.abimethod
    def clear_orders(self, order_type: UInt64, user1: Account) -> None:
        """Elimina gli ordini di un determinato tipo per tre utenti specifici."""
        if order_type == UInt64(1):  # YES Orders
            del self.place_order_yes_price[user1]
            del self.place_order_yes_quantity[user1]
        elif order_type == UInt64(0):  # NO Orders
            del self.place_order_no_price[user1]
            del self.place_order_no_quantity[user1]
        else:
            assert False, "Tipo di ordine non valido"

    @arc4.abimethod
    def close_market(self, oracle: Account, outcome: UInt64) -> None:
        """Chiude il mercato e stabilisce il risultato."""
        assert Txn.sender == oracle, "Solo l'oracolo può chiudere il mercato"
        assert not self.market_closed, "Il mercato è già stato chiuso"

        # Imposta il vincitore
        if outcome == UInt64(1):
            self.winning_asset = self.asset_yes  # ID dell'asset YES
        else:
            self.winning_asset = self.asset_no  # ID dell'asset NO

        self.market_closed = True  # Segna il mercato come chiuso

    @arc4.abimethod
    def redeem(self, user: Account, asset_txn: gtxn.AssetTransferTransaction) -> None:
        """Permette agli utenti di riscattare Algo in base al risultato."""
        assert self.market_closed, "Il mercato non è ancora chiuso"
        assert self.winning_asset, "Il risultato non è stato stabilito"

        # Controlla che l'utente stia inviando il token vincente al contratto
        assert asset_txn.sender == user, "L'utente deve inviare il token"
        assert (
            asset_txn.asset_receiver == Global.current_application_address
        ), "I token devono essere inviati al contratto"
        assert (
            asset_txn.xfer_asset == self.winning_asset
        ), "Il token inviato non è quello vincente"

        # Determina il valore di conversione (es. 1 token = 1 Algo, puoi modificare questa logica)
        algo_to_send = asset_txn.asset_amount * 1_000  # 1 token = 1000 microAlgo

        # Invia Algo all'utente
        itxn.Payment(receiver=user, amount=algo_to_send).submit()

    @subroutine
    # Assicura che ogni volta che gli asset vengono scambiati,
    # il rapporto tra YES e NO venga aggiornato per mantenere il bilanciamento del mercato.
    def _update_ratio(self) -> None:
        """Aggiorna il valore della variabile ratio."""
        yes_balance = self._current_yes_balance()
        no_balance = self._current_no_balance()
        self.ratio = yes_balance * no_balance

    @subroutine
    def _update_balance(self, amount: UInt64) -> None:
        """Aggiorna il bilancio del contratto con la quantità di Algos ricevuti."""
        # Qui puoi registrare la quantità di Algos ricevuti per esempio in un registro del contratto
        pass

    @subroutine
    # consente agli utenti di possedere una parte del pool di liquidità e di scambiare la loro quota in base ai cambiamenti del mercato
    def _create_pool_token(self) -> Asset:
        """Crea un nuovo asset che rappresenta il pool token."""
        return (
            itxn.AssetConfig(
                asset_name=b"DPT-"
                + self.asset_yes.unit_name
                + b"-"
                + self.asset_no.unit_name,
                unit_name=b"dbt",
                total=TOTAL_SUPPLY,
                decimals=3,
                manager=Global.current_application_address,
                reserve=Global.current_application_address,
            )
            .submit()
            .created_asset
        )

    @subroutine
    def _do_opt_in(self, asset: Asset) -> None:
        """Effettua l'opt-in per l'asset specificato."""
        do_asset_transfer(
            receiver=Global.current_application_address,
            asset=asset,
            amount=UInt64(0),
        )

    @subroutine
    # guarda la quantità di token totali
    def _current_pool_balance(self) -> UInt64:
        return self.pool_token.balance(Global.current_application_address)

    @subroutine
    # guarda la quantità di token yes
    def _current_yes_balance(self) -> UInt64:
        return self.asset_yes.balance(Global.current_application_address)

    @subroutine
    # guarda la quantità di token no
    def _current_no_balance(self) -> UInt64:
        return self.asset_no.balance(Global.current_application_address)


@subroutine
def tokens_to_swap(
    *,
    in_amount: UInt64,  # se sta cercando di comprare "YES" con "NO", questo sarà l'ammontare di "NO" che l'utente vuole scambiare
    in_supply: UInt64,  # La quantità attuale dell'asset che l'utente sta inviando,(in questo caso, "NO")
    out_supply: UInt64,  # La quantità attuale dell'asset che l'utente vuole ricevere
) -> UInt64:
    """Calcola la quantità dell'asset da ricevere con sulla formula X * Y = K."""
    k = (
        in_supply * out_supply
    )  # quantità attuale di "NO" (in_supply) per la quantità attuale di "YES" (out_supply) nel pool.. se un
    # utente aggiunge più "NO" al pool, la quantità di "YES" che riceve deve essere ridotta in modo tale che k rimanga costante
    new_in_supply = in_supply + in_amount  # Nuovo bilancio dopo il deposito
    new_out_supply = k // new_in_supply  # Risolve la quantità da ricevere
    to_swap = (
        out_supply - new_out_supply
    )  # Calcola la quantità di "YES" che l'utente riceverà
    return to_swap  # usata in do_asset_transfer


@subroutine
def do_asset_transfer(*, receiver: Account, asset: Asset, amount: UInt64) -> None:
    """Esegue un trasferimento di asset."""
    itxn.AssetTransfer(
        xfer_asset=asset,
        asset_amount=amount,
        asset_receiver=receiver,
    ).submit()
