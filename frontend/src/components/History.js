import Divider from "@mui/material/Divider";

export default function History({ chatHistory }) {
  if (chatHistory.length === 0) {
    return <div></div>;
  }
  return (
    <div>
      {chatHistory.map((e, i) => (
        <div key={i}>
          <Divider style={{ paddingTop: 10, paddingBottom: 10 }} />
          <div style={{ paddingTop: 10 }}>{e}</div>
        </div>
      ))}
      <Divider style={{ paddingTop: 10, paddingBottom: 10 }} />
    </div>
  );
}
