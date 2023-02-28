import { useEffect, useRef } from "react";
import Divider from "@mui/material/Divider";

export default function History({ chatHistory }) {
  const containerRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    container.scrollTop = container.scrollHeight;
  }, [chatHistory]);

  if (chatHistory.length === 0) {
    return <div ref={containerRef}></div>;
  }

  return (
    <div ref={containerRef} style={{ maxHeight: "50vh", overflowY: "auto" }}>
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
