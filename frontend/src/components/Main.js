import { useState, useEffect, useRef } from "react";
import { fetchGet, fetchPost } from "../utils/APIUtils";
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

export default function Main({ sessionManager }) {
  const [domains, setDomains] = useState([]);
  const [domain, setDomain] = useState("");
  const [query, setQuery] = useState("");
  const [chunks, setChunks] = useState({});
  const [chunksUsedcount, setChunksUsedCount] = useState(0);
  const [result, setResult] = useState("-");

  console.log("Main userID", sessionManager.user.userID);

  useEffect(() => {
    console.log("Main useEffect -> userID", sessionManager.user.userID);
    sessionManager.requireUser();
  }, [sessionManager.user.userID]);

  useEffect(() => {
    const getOptions = async () => {
      const d = await fetchGet("domain");
      setDomains(d);
    };

    getOptions();
  }, []);

  const formSubmit = async (e) => {
    e.preventDefault();
    const queryObj = { domain_id: domain, query };
    try {
      setResult(null);
      setChunks({});
      setChunksUsedCount(0);
      const data = await fetchPost("answer", queryObj);
      setResult(data.answer);
      setChunks(data.chunks);
      setChunksUsedCount(data.chunks_used_count);
    } catch (e) {
      setResult("ERROR");
    }
  };

  return (
    <Box
      component="form"
      maxWidth={800}
      onSubmit={formSubmit}
      sx={{ mt: 1, margin: "auto" }}
    >
      <FormControl fullWidth>
        <InputLabel>Domain</InputLabel>
        <Select
          value={domain}
          label="Domain"
          onChange={(e) => {
            setDomain(e.target.value);
          }}
        >
          {domains.map((d) => (
            <MenuItem key={d.domain_id} value={d.domain_id}>
              {d.domain_desc}
            </MenuItem>
          ))}
        </Select>
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
      {result ? (
        <div>
          <div>
            <br />
          </div>
          <div>{result}</div>{" "}
          <div>
            <br />
          </div>
          <div>Chunks used: {chunksUsedcount}</div>
        </div>
      ) : (
        <div style={{ display: "flex", justifyContent: "center" }}>
          <img src="/waves.gif" style={{ height: 75, width: 250 }} />
        </div>
      )}
      <div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            border: "solid",
          }}
        >
          <div style={{ flexGrow: 0, padding: 5 }}>SCR</div>
          <div style={{ flexGrow: 0, padding: 5 }}>ID</div>
          <div style={{ flexGrow: 1, padding: 5 }}> CHUNK TEXT</div>
        </div>
      </div>

      {Object.values(chunks)
        .sort((a, b) => b.score - a.score)
        .map((chunk, i) => (
          <div key={chunk.metadata.doc_chunk_id}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                border: "solid",
              }}
            >
              <div style={{ flexGrow: 0, padding: 5 }}>
                {chunk.score.toFixed(3)}
              </div>
              <div style={{ flexGrow: 0, padding: 5 }}>
                {chunk.metadata.doc_chunk_id}
              </div>
              <div style={{ flexGrow: 1, padding: 5 }}> {chunk.text}</div>
            </div>
            <div style={{ textAlign: "center" }}>
              {i + 1 === chunksUsedcount ? <div>UNUSED CHUNKS</div> : ""}
            </div>
          </div>
        ))}
    </Box>
  );
}
