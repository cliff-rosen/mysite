import { useState, useEffect, useRef } from "react";
import { fetchPost } from "./utils/APIUtils";
import Container from "@mui/material/Container";
import Box from "@mui/material/Box";
import Alert from "@mui/material/Alert";
import { TextField, Button } from "@mui/material";
import FormGroup from "@mui/material/FormGroup";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormLabel from "@mui/material/FormLabel";
import Checkbox from "@mui/material/Checkbox";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import InputLabel from "@mui/material/InputLabel";

export default function Hello() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState("...");

  useEffect(() => {}, []);

  const formSubmit = async (e) => {
    e.preventDefault();
    const queryObj = { query };
    try {
      const data = await fetchPost("polls/", queryObj);
      setResult(data.answer);
    } catch (e) {
      setResult("ERROR");
    }
  };

  return (
    <Container>
      <div style={{ margin: "20px" }}></div>
      <Box component="form" onSubmit={formSubmit} sx={{ mt: 1 }}>
        <FormControl fullWidth>
          <TextField
            margin="normal"
            fullWidth
            id="querytitle"
            type="text"
            label="Question"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            variant="outlined"
            required
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            style={{ marginTop: 20 }}
          >
            submit
          </Button>
        </FormControl>
      </Box>
      <div></div>
      <div>Result: {result}</div>
    </Container>
  );
}
