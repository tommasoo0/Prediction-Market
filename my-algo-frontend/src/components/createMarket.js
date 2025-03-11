import React, { useState } from "react";
import { createMarket } from "../Contract/contract";

const CreateMarket = () => {
  const [marketId, setMarketId] = useState("");
  const [question, setQuestion] = useState("");
  const [description, setDescription] = useState("");
  const [privateKey, setPrivateKey] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const txId = await createMarket(marketId, question, description, privateKey);
      alert(`Mercato creato con successo! ID transazione: ${txId}`);
    } catch (error) {
      alert(`Errore nella creazione del mercato: ${error.message}`);
    }
  };

  return (
    <div>
      <h2>Creazione del Mercato</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>ID Mercato:</label>
          <input
            type="text"
            value={marketId}
            onChange={(e) => setMarketId(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Domanda:</label>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Descrizione:</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Chiave Privata (Base64):</label>
          <input
            type="text"
            value={privateKey}
            onChange={(e) => setPrivateKey(e.target.value)}
            required
          />
        </div>
        <button type="submit">Crea Mercato</button>
      </form>
    </div>
  );
};

export default CreateMarket;
