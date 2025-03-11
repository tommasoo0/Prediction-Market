require("dotenv").config();  // Carica le variabili d'ambiente dal file .env
const express = require("express");
const algosdk = require("algosdk");
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());

// Ottieni i valori dalle variabili d'ambiente
const algodToken = process.env.ALGOD_TOKEN;
const algodServer = process.env.ALGOD_SERVER;
const algodPort = process.env.ALGOD_PORT;

// Verifica che tutte le variabili siano state correttamente impostate
if (!algodToken || !algodServer || !algodPort) {
  console.error("Le variabili d'ambiente non sono configurate correttamente!");
  process.exit(1);  // Esci con un errore se le variabili non sono configurate
}

// Configura il client Algorand
const algodClient = new algosdk.Algodv2(algodToken, algodServer, algodPort);

const accountAddress = 'M6VIWH2GPEKCKXA5I5L5KUAUBDR7DDX4FSIOXXIDRHBAE477HTY2F64JLA';

// Endpoint per ottenere gli asset ID creati dallo smart contract
app.get('/state', async (req, res) => {
  try {
    const globalState = await algodClient.accountInformation(accountAddress).do();
    
    // Stampa la risposta per vedere la struttura
    console.log("Account Information:", globalState);

    // Se lo stato globale esiste, stampa le chiavi
    if (globalState['apps-local-state'] && globalState['apps-local-state'][0] && globalState['apps-local-state'][0].global_state) {
      globalState['apps-local-state'][0].global_state.forEach((entry) => {
        const key = new TextDecoder().decode(entry.key);
        console.log('Key:', key, 'Value:', entry.value.uint);
      });
      res.json(globalState['apps-local-state'][0].global_state);
    } else {
      throw new Error("Stato globale non trovato");
    }

  } catch (err) {
    console.error("Errore nel recupero dello stato:", err);
    res.status(500).json({ error: 'Errore nel recupero dello stato', message: err.message });
  }
});



// Avvia il server
const PORT = process.env.PORT || 5000; // Usa la variabile d'ambiente per la porta o 5000 come default
app.get("/", (req, res) => {
  res.send("Backend attivo! 🚀");
});
app.listen(PORT, () => {
  console.log(`Server in esecuzione su http://localhost:${PORT}/`);
});
