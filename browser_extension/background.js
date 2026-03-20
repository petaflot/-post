// Use the browser API (standard for Firefox) or chrome API (standard for Chrome/Edge)
const browserAPI = typeof browser !== "undefined" ? browser : chrome;

const WS_URL = "ws://127.0.0.1:12345/ingest";
let ws;

function createWebSocket() {
  ws = new WebSocket(WS_URL);
  ws.onopen = () => {
    console.log("⨯post WebSocket connection established.");
  };
  ws.onerror = (error) => {
    console.error("⨯post WebSocket error:", error);
  };
  ws.onclose = () => {
    console.log("⨯post WebSocket connection closed.");
  };
}

// Start the WebSocket connection when the extension is installed or loaded
browserAPI.runtime.onInstalled.addListener(createWebSocket);
