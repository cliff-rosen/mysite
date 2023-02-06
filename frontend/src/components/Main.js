import { useState, useEffect, useRef } from "react";
import { fetchGet, fetchPost } from "../utils/APIUtils";
import Container from "@mui/material/Container";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import { TextField, Button } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import InputLabel from "@mui/material/InputLabel";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";

export default function Main({ sessionManager }) {
  const [domains, setDomains] = useState([]);
  const [domain, setDomain] = useState("");
  const [query, setQuery] = useState("");
  const [chunks, setChunks] = useState([]);
  const [chunksUsedcount, setChunksUsedCount] = useState(0);
  const [result, setResult] = useState("");
  const [showThinking, setShowThinking] = useState(false);

  console.log("Main userID", sessionManager.user.userID);

  if (!domain && sessionManager.user.domainID)
    setDomain(sessionManager.user.domainID);

  console.log(chunks);

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
    const queryObj = {
      domain_id: domain,
      query,
      user_id: sessionManager.user.userID,
    };
    try {
      setShowThinking(true);
      setResult(null);
      setChunks([]);
      setChunksUsedCount(0);
      const data = await fetchPost("answer", queryObj);
      setResult(data.answer);
      setShowThinking(false);
      const rows: GridRowsProp[] = Object.values(data.chunks).sort(
        (a, b) => b.score - a.score
      );
      setChunks(rows);
      setChunksUsedCount(data.chunks_used_count);
    } catch (e) {
      setResult("ERROR");
      setShowThinking(false);
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
      <br /> <br /> <br />
      <Paper
        elevation={0}
        style={{ minHeight: 100, backgroundColor: "#eeeeee", padding: 20 }}
      >
        <div>
          <div></div>
          <div>{result}</div>{" "}
        </div>
        {showThinking ? (
          <div style={{ display: "flex", justifyContent: "center" }}>
            <img src="/waves.gif" style={{ height: 175, width: 350 }} />
          </div>
        ) : (
          <></>
        )}
      </Paper>
      <br />
      <br />
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
        >
          <Typography>diagnostics</Typography>
        </AccordionSummary>

        <AccordionDetails>
          <TableContainer component={Paper}>
            <Table aria-label="chunks">
              <TableHead>
                <TableRow>
                  <TableCell align="left">Score</TableCell>
                  <TableCell align="left">ID</TableCell>
                  <TableCell align="left">Text</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {chunks.map((chunk) => (
                  <TableRow key={chunk.ID}>
                    <TableCell style={{ verticalAlign: "top" }} align="left">
                      {chunk.score.toFixed(3)}
                    </TableCell>
                    <TableCell style={{ verticalAlign: "top" }} align="left">
                      {chunk.id}
                    </TableCell>
                    <TableCell align="left">{chunk.text}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <div>Chunks used: {chunksUsedcount}</div>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
}