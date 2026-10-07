// Entry point: Vite loads this from index.html and React draws <App /> into #root.
import { createRoot } from "react-dom/client";
import "@fontsource/barlow/400.css";
import "@fontsource/barlow/600.css";
import "@fontsource/barlow-condensed/700.css";
import "./theme.css";
import App from "./App";

createRoot(document.getElementById("root")!).render(<App />);
