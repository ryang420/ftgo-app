import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ConsumerSessionProvider } from "./context/ConsumerSessionContext.jsx";
import App from "./App.jsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <ConsumerSessionProvider>
        <App />
      </ConsumerSessionProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
