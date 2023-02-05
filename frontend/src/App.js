import { useSessionManager } from "./utils/Auth";
import Main from "./components/Main";
import LoginFormModal from "./components/LoginFormModal";
import Container from "@mui/material/Container";

function App() {
  const sessionManager = useSessionManager();

  return (
    <Container>
      <LoginFormModal sessionManager={sessionManager} />
      <div style={{ margin: "20px" }}></div>
      <Main sessionManager={sessionManager} />
    </Container>
  );
}
export default App;
