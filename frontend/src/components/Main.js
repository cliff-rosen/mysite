import { useState, useEffect, useRef } from "react";
import { fetchGet, fetchPost } from "../utils/APIUtils";
import History from "./History";
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
import Slider from "@mui/material/Slider";
import { Link } from "react-router-dom";

export default function Main({ sessionManager }) {
  const [domains, setDomains] = useState([]);
  const [domain, setDomain] = useState("");
  const [query, setQuery] = useState("");
  const [prompt, setPrompt] = useState("TBD");
  const [promptDefault, setPromptDefault] = useState("TBD");
  const [promptCustom, setPromptCustom] = useState("");
  const [temp, setTemp] = useState(0.4);
  const [chunks, setChunks] = useState([]);
  const [chunksUsedcount, setChunksUsedCount] = useState(0);
  const [showThinking, setShowThinking] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [conversationID, setConversationID] = useState("NEW");
  const [initialMessage, setInitialMessage] = useState("");

  console.log("Main --> userID", sessionManager.user.userID, domain);

  function resetConversation() {
    setConversationID("NEW");
    if (initialMessage) setChatHistory([initialMessage]);
    else setChatHistory([]);
    setQuery("");
    setShowThinking(false);
    setChunks([]);
    setChunksUsedCount(0);
  }

  async function setActiveDomain(iDomainID) {
    console.log("setActiveDomain -> setting domain to", iDomainID);
    resetConversation();
    setDomain(iDomainID);
    const data = await fetchGet(`domain/${iDomainID}`);
    setPromptCustom(data.initial_prompt_template);
    let newHistory = [];
    if (data.initial_conversation_message) {
      setInitialMessage("AI: " + data.initial_conversation_message);
      newHistory.push("AI: " + data.initial_conversation_message);
    } else {
      setInitialMessage("");
    }

    setChatHistory(newHistory);
    setPrompt(data.initial_prompt_template || promptDefault);
  }

  // Main useEffect
  useEffect(() => {
    console.log("useEffect -> Main");

    const getOptions = async () => {
      const p = await fetchGet("prompt");
      setPromptDefault(p.prompt_text);
      setPrompt(p.prompt_text);
      const d = await fetchGet("domain");
      setDomains(d);
    };

    getOptions();
  }, []);

  // Domain change useEffect
  useEffect(() => {
    console.log("useEffect -> domain");
    if (domain) setActiveDomain(domain);
  }, [domain, promptDefault]);

  // Session useEffect
  useEffect(() => {
    console.log(
      "useEffect -> Session change, userID",
      sessionManager.user.userID
    );

    if (!domain && sessionManager.user.domainID)
      setDomain(sessionManager.user.domainID);

    if (!sessionManager.user.userID) {
      setDomain("");
      setQuery("");
      setPrompt("");
      setShowThinking(false);
      setChunks([]);
      setChunksUsedCount(0);
      setChatHistory([]);
      setConversationID("NEW");
      setInitialMessage("");
    }

    sessionManager.requireUser();
  }, [sessionManager.user.userID]);

  const formSubmit = async (e) => {
    e.preventDefault();
    const queryObj = {
      domain_id: domain,
      query,
      prompt_template: prompt,
      temp,
      user_id: sessionManager.user.userID,
      conversation_id: conversationID,
    };
    try {
      setQuery("");
      setShowThinking(true);
      setChunks([]);
      setChunksUsedCount(0);
      setChatHistory((h) => [...h, "User: " + query]);
      const data = await fetchPost("answer", queryObj);
      setChatHistory((h) => [...h, "AI: " + data.answer]);
      setConversationID(data.conversation_id);
      setShowThinking(false);
      const rows: GridRowsProp[] = Object.values(data.chunks).sort(
        (a, b) => b.score - a.score
      );
      setChunks(rows);
      setChunksUsedCount(data.chunks_used_count);
    } catch (e) {
      setChatHistory((h) => [
        ...h,
        "Sorry, an error occured.  Please try again.",
      ]);
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
        <div style={{ display: "flex", paddingBottom: 10 }}>
          <div style={{ flexGrow: 1, paddingRight: 10 }}>
            <InputLabel>Domain</InputLabel>
            <Select
              value={domains.length > 0 ? domain : ""}
              label="Domain"
              onChange={(e) => {
                setDomain(e.target.value);
              }}
              style={{ width: "100%" }}
            >
              {domains.map((d) => (
                <MenuItem key={d.domain_id} value={d.domain_id}>
                  {d.domain_desc}
                </MenuItem>
              ))}
            </Select>
          </div>
          <div style={{ flexGrow: 0, alignSelf: "center" }}>
            <Link
              style={{ textDecoration: "none", color: "gray" }}
              to="#"
              onClick={() => resetConversation()}
            >
              RESTART SESSION
            </Link>
          </div>
        </div>
        <Accordion>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls="panel1a-content"
            id="panel1a-header"
          >
            <Typography>customize prompt</Typography>
          </AccordionSummary>

          <AccordionDetails>
            <TextField
              margin="normal"
              fullWidth
              id="desc"
              multiline
              rows={20}
              type="text"
              label="Prompt Template"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              variant="outlined"
            />
            <Link
              style={{ textDecoration: "none", color: "gray" }}
              to="#"
              onClick={() => setPrompt(promptCustom || promptDefault)}
            >
              [reset]
            </Link>
          </AccordionDetails>
        </Accordion>
        <Slider
          aria-label="Temperature"
          defaultValue={temp}
          valueLabelDisplay="auto"
          step={0.1}
          marks
          min={0}
          max={1}
          onChange={(e) => setTemp(e.target.value)}
        />

        <History chatHistory={chatHistory} />

        {showThinking ? (
          <Paper elevation={0}>
            <div
              style={{ display: "flex", justifyContent: "left", height: 50 }}
            >
              <img src="/spinner.gif" />
            </div>
          </Paper>
        ) : (
          <></>
        )}

        <div style={{ display: "flex" }}>
          <div style={{ flexGrow: 1, paddingRight: 10 }}>
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
          </div>
          <div style={{}}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              style={{ marginTop: 20 }}
            >
              O
            </Button>
          </div>
        </div>
      </FormControl>
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
            ConversationID: {conversationID}
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
                      <Link to={chunk.uri} target="_blank">
                        {chunk.id}
                      </Link>
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
