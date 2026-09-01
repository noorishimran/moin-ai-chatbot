import { ChatWidget } from "./components/ChatWidget";

function App() {
  return (
    <div style={{ minHeight: "100vh", padding: 40, fontFamily: "system-ui" }}>
      <h1>MoinSystems AI — Demo Page</h1>
      <p>This is a placeholder host page. The chat widget appears bottom-right.</p>
      <ChatWidget />
    </div>
  );
}

export default App;