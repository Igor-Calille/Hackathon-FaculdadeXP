import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import "chartjs-plugin-zoom";
import "chart.js/auto";
import axios from "axios";

const App = () => {
  const [portfolioData, setPortfolioData] = useState([]);
  const [buyHoldDataAAPL, setBuyHoldDataAAPL] = useState([]);
  const [buyHoldDataMSFT, setBuyHoldDataMSFT] = useState([]);
  const [showAAPL, setShowAAPL] = useState(true);
  const [showMSFT, setShowMSFT] = useState(true);

  useEffect(() => {
    const fetchPortfolioData = async () => {
      const response = await axios.post("http://localhost:5002/portfolio/value", {
        tickers: ["AAPL", "MSFT"],
        start_date: "2024-01-01",
        valor_inicial: 10000,
      });
      setPortfolioData(response.data);
    };

    const fetchBuyHoldData = async () => {
      const response = await axios.post("http://localhost:5001/buyhold/value", {
        tickers: ["AAPL", "MSFT", "GSPC"],
        start_date: "2024-01-01",
        valor_inicial: 10000,
      });

      if (response.data.AAPL && response.data.MSFT) {
        setBuyHoldDataAAPL(response.data.AAPL);
        setBuyHoldDataMSFT(response.data.MSFT);
      } else {
        setBuyHoldDataAAPL([]);
        setBuyHoldDataMSFT([]);
      }
    };

    fetchPortfolioData();
    fetchBuyHoldData();
  }, []);

  const toggleAAPL = () => setShowAAPL(!showAAPL);
  const toggleMSFT = () => setShowMSFT(!showMSFT);

  const combinedChartData = {
    labels: portfolioData.map((data) => new Date(data.date).toLocaleDateString()),
    datasets: [
      {
        label: "Valor Portfólio",
        data: portfolioData.map((data) => data.total_portfolio_value),
        borderColor: "rgba(75,192,192,1)",
        fill: true,
      },
      showAAPL && {
        label: "AAPL (Buy and Hold)",
        data: buyHoldDataAAPL.map((data) => data.portfolio_value),
        borderColor: "rgba(255,99,132,1)",
        fill: true,
      },
      showMSFT && {
        label: "MSFT (Buy and Hold)",
        data: buyHoldDataMSFT.map((data) => data.portfolio_value),
        borderColor: "rgba(54,162,235,1)",
        fill: true,
      },
    ].filter(Boolean),
  };

  const options = {
    responsive: true,
    plugins: {
      zoom: {
        zoom: {
          enabled: true,
          mode: "x",
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: "white",  // Cor das labels no eixo X
        },
      },
      y: {
        ticks: {
          color: "white",  // Cor das labels no eixo Y
        },
      },
    },
    plugins: {
      legend: {
        labels: {
          color: "white",  // Cor das labels da legenda
        },
      },
    },
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif", maxWidth: "900px", margin: "auto", color: '#f5e2b8' }}>
      <h1 style={{textAlign: "center"}}>Top Lanches</h1>
      <h2 style={{textAlign: "center"}}>Evolução do Portfólio x Buy And Hold</h2>
      <Line data={combinedChartData} options={options} />
      <div style={{ display: "flex", justifyContent: "space-between", margin: "10px 0" }}>
        <button onClick={toggleAAPL} style={{ padding: "10px", backgroundColor: showAAPL ? "#a2caa5" : "#f44336", color: "white" }}>
          AAPL
        </button>
        <button onClick={toggleMSFT} style={{ padding: "10px", backgroundColor: showMSFT ? "#a2caa5" : "#f44336", color: "white" }}>
          MSFT
        </button>
      </div>
    </div>
  );
};

export default App;
