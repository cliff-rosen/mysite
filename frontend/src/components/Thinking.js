import Paper from "@mui/material/Paper";

export default function Thinking({ show }) {
  if (!show) return <></>;

  return (
    <Paper elevation={0}>
      <div style={{ display: "flex", justifyContent: "left", height: 50 }}>
        <img src="/spinner.gif" />
      </div>
    </Paper>
  );
}
