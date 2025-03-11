import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [yesAsset, setYesAsset] = useState(null);
  const [noAsset, setNoAsset] = useState(null);

  useEffect(() => {
    const fetchAssets = async () => {
      try {
        const response = await axios.get("http://localhost:5000/get-assets", {
          params: { appId: 1040 }, // Utilizza l'ID corretto del tuo smart contract
        });
        setYesAsset(response.data.yesAssetId);
        setNoAsset(response.data.noAssetId);
      } catch (error) {
        console.error("Errore nel recupero degli asset:", error);
      }
    };
  
    fetchAssets();
  }, []);

  return (
    <div>
      <h1>Prediction Market</h1>
      <p>YES Asset ID: {yesAsset || "Loading..."}</p>
      <p>NO Asset ID: {noAsset || "Loading..."}</p>
    </div>
  );
}

export default App;
