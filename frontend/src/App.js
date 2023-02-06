import { useSessionManager } from "./utils/Auth";
import Main from "./components/Main";
import SessionMessage from "./components/SessionMessage";
import LoginFormModal from "./components/LoginFormModal";
import Nav from "./components/Nav";
import Container from "@mui/material/Container";

function App() {
  const sessionManager = useSessionManager();

  return (
    <Container>
      <SessionMessage sessionManager={sessionManager} />
      <LoginFormModal sessionManager={sessionManager} />
      <Nav sessionManager={sessionManager} />
      <div style={{ margin: "20px" }}></div>
      <Main sessionManager={sessionManager} />
    </Container>
  );
}
export default App;
