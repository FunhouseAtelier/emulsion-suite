import { useState } from "react";

interface CounterProps {
  initialCount: number;
}

export default function Counter({ initialCount }: CounterProps) {
  const [count, setCount] = useState(initialCount);

  return (
    <div style={{
      border: "2px solid #2563eb",
      borderRadius: "8px",
      padding: "1.5rem",
      display: "inline-block",
      background: "#eff6ff",
    }}>
      <p style={{ margin: "0 0 1rem", fontSize: "1.25rem" }}>
        Count: <strong>{count}</strong>
      </p>
      <button
        onClick={() => setCount((c) => c - 1)}
        style={{ marginRight: "0.5rem", padding: "0.5rem 1rem", cursor: "pointer" }}
      >
        −
      </button>
      <button
        onClick={() => setCount((c) => c + 1)}
        style={{ padding: "0.5rem 1rem", cursor: "pointer" }}
      >
        +
      </button>
      <button
        onClick={() => setCount(initialCount)}
        style={{ marginLeft: "0.5rem", padding: "0.5rem 1rem", cursor: "pointer" }}
      >
        Reset
      </button>
    </div>
  );
}
