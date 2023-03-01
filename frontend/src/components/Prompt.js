import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { TextField, Button } from "@mui/material";
import { Link } from "react-router-dom";

export default function Prompt({
  prompt,
  setPrompt,
  promptCustom,
  promptDefault,
}) {
  return (
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
  );
}
