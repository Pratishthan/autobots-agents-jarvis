// NodeChips — clickable node-reference chips. Click calls the `jump_to_node` action,
// which the server bridges to the host canvas via cl.CopilotFunction("jumpToNode").
const COLORS = { system: "#34d8f0", manual: "#f5c451", decision: "#c98bff", terminal: "#5fe3a1" };

export default function NodeChips() {
  const refs = props.refs || [];
  if (!refs.length) return null;
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, margin: "4px 0" }}>
      {refs.map((r) => (
        <button
          key={r.id}
          onClick={() => callAction({ name: "jump_to_node", payload: { id: r.id } })}
          style={{
            display: "inline-flex", alignItems: "center", gap: 6, cursor: "pointer",
            background: "transparent", border: "1px solid var(--border, #2a3142)",
            borderRadius: 8, padding: "5px 10px", color: "inherit", fontSize: 12, fontWeight: 540,
          }}
        >
          <span style={{
            width: 7, height: 7, borderRadius: r.type === "decision" ? 0 : 4,
            transform: r.type === "decision" ? "rotate(45deg)" : "none",
            background: r.term === "declined" ? "#ff6f6f" : (COLORS[r.type] || "#8b95a7"),
          }} />
          {r.title}
          <span style={{ opacity: 0.6 }}>→</span>
        </button>
      ))}
    </div>
  );
}
