import { Buffer } from "buffer";  // Importa Buffer per il browser
import algosdk from "algosdk";

// Definisci le variabili per la connessione al client Algorand
const algodToken = "a".repeat(64); // Token per la LocalNet, da sostituire con il tuo token se usi una rete diversa
const algodServer = "http://localhost"; // Server della tua LocalNet
const algodPort = "4001"; // Porta della tua LocalNet

// Crea il client per connetterti alla blockchain di Algorand
const algodClient = new algosdk.Algodv2(algodToken, algodServer, algodPort);

// ID del contratto (devi sostituirlo con l'ID del tuo contratto distribuito)
const appId = 1032; // Sostituisci con l'ID del tuo contratto distribuito su Algorand

export const createMarket = async (marketId, question, description, privateKey) => {
  try {
    const sender = "M6VIWH2GPEKCKXA5I5L5KUAUBDR7DDX4FSIOXXIDRHBAE477HTY2F64JLA"; // Sostituisci con l'indirizzo corretto del creatore

    // Ottieni i parametri della transazione
    const params = await algodClient.getTransactionParams().do();

    // Crea la transazione con i parametri presi da Algorand
    const txn = {
      from: sender,
      to: algodClient.getTransactionParams().toString(), // Indirizzo del contratto
      amount: 0,  // Nessun pagamento, solo invocazione del contratto
      fee: params.fee, // Usa la fee predefinita
      note: algosdk.encodeObj({ market_id: marketId, question, description }),
      appIndex: appId,
      appArgs: [algosdk.encodeObj(question), algosdk.encodeObj(description)],
    };

    // Firma la transazione
    const signedTxn = algosdk.signTransaction(txn, new Uint8Array(Buffer.from(privateKey, "base64")));

    // Invia la transazione alla blockchain
    const txId = await algodClient.sendRawTransaction(signedTxn.blob).do();

    console.log(`Transazione inviata con ID: ${txId}`);
    return txId;
  } catch (error) {
    console.error("Errore nella creazione del mercato:", error);
    throw error;
  }
};
