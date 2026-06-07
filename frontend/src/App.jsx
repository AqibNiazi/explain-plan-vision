import React from "react";
import AppRoutes from "./routes/AppRoutes";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function App() {
  return (
    <>
      <AppRoutes />
      <ToastContainer
        position="bottom-right"
        autoClose={4000}
        hideProgressBar={false}
        theme="dark"
        toastStyle={{
          background: "var(--bg-panel)",
          border: "1px solid var(--border-bright)",
          color: "var(--text-primary)",
          fontFamily: "var(--font-mono)",
          fontSize: "12px",
          borderRadius: "0",
        }}
      />
    </>
  );
}
