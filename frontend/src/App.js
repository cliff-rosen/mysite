import { useSessionManager } from "./utils/Auth";
import Main from "./components/Main";
import LoginFormModal from "./components/LoginFormModal";
import Nav from "./components/Nav";
import Container from "@mui/material/Container";

function App() {
  const sessionManager = useSessionManager();

  return (
    <Container>
      <LoginFormModal sessionManager={sessionManager} />
      <Nav sessionManager={sessionManager} />
      <div style={{ margin: "20px" }}></div>
      <Main sessionManager={sessionManager} />
    </Container>
  );
}
export default App;
