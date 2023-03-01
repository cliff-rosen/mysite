import Paper from "@mui/material/Paper";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import Slider from "@mui/material/Slider";
import { Link } from "react-router-dom";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";

export default function Diagnostics({
  conversationID,
  chunks,
  chunksUsedcount,
}) {
  return (
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
  );
}
