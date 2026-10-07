/// <reference types="vite/client" />

import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);

const isProd = (import.meta as unknown as { env: { PROD: boolean } }).env.PROD;

if ("serviceWorker" in navigator && isProd) {
  navigator.serviceWorker.register("/sw.js");
}
