import Snackbar from "@mui/material/Snackbar";
import { Alert } from "@mui/material";

const AUTO_HIDE_DURATION = 3000;

export default function SessionMessage({ sessionManager }) {
  return (
    <Snackbar
      open={sessionManager.showSessionMessage}
      autoHideDuration={AUTO_HIDE_DURATION}
      onClose={() => sessionManager.setShowSessionMessage(false)}
      severity="info"
    >
      <Alert severity="success" sx={{ width: "100%" }}>
        {sessionManager.sessionMessage}
      </Alert>
    </Snackbar>
  );
}
