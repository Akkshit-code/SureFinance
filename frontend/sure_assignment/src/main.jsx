import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css"; // or "./index.css" if your file is directly in src/

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
