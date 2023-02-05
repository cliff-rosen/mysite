import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";

export default function LoginFormModal({ sessionManager }) {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errMessage, setErrMessage] = useState("");

  const handleClose = () => {
    if (sessionManager.user.userID == 0) return;
    setUsername("");
    setPassword("");
    setErrMessage("");

    if (sessionManager.lao.homeOnAbort) {
      navigate("/");
    }
    sessionManager.hideLogin();
  };

  const isUsernameValid = (u) => {
    if (u.length < 2 || u.length > 15) {
      return false;
    }

    var usernameRegex = /^[a-zA-Z0-9]+$/;
    return u.match(usernameRegex);
  };

  const formSubmit = (e) => {
    e.preventDefault();

    if (username === "" || password === "") {
      setErrMessage("Please enter both fields.");
      return;
    }

    if (!isUsernameValid(username)) {
      setErrMessage(
        "Username may contain only letters and numbers and must be between 2 and 12 characters."
      );
      return;
    }

    sessionManager
      .login(username, password)
      .then((u) => {
        setUsername("");
        setPassword("");
        setErrMessage("");
        sessionManager.hideLoginThen(u);
        sessionManager.setSessionMessageWrapper("Login successful");
      })
      .catch((err) => {
        console.log("formSubmit: ", err.message);
        if (err.message === "UNAUTHORIZED") {
          setErrMessage("Invalid login.  Please try again.");
        } else {
          setErrMessage(
            "Sorry, an unexpected error occurred.  Please try again."
          );
        }
      });
  };

  return (
    <Dialog
      open={sessionManager.lao.show}
      onClose={handleClose}
      PaperProps={{ sx: { width: 350 } }}
    >
      <DialogTitle>Login</DialogTitle>
      <DialogContent>
        {sessionManager.lao.message && (
          <DialogContentText>
            {sessionManager.lao.message}
            <br /> <br />
          </DialogContentText>
        )}
        {errMessage ? (
          <Alert severity="error">
            {errMessage} <br />
            <br />
          </Alert>
        ) : (
          ""
        )}
        <DialogContentText>LOGIN </DialogContentText>
        <Box component="form" onSubmit={formSubmit} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            id="username"
            fullWidth
            autoFocus
            type="text"
            label="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            variant="outlined"
            required
          />
          <br />
          <TextField
            margin="normal"
            id="password"
            fullWidth
            type="password"
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            variant="outlined"
            required
          />
          <br />
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary">
              login
            </Button>
          </DialogActions>
        </Box>{" "}
      </DialogContent>
    </Dialog>
  );
}
