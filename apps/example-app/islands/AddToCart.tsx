import { useState } from "react";

interface AddToCartProps {
  productId: string;
  productName: string;
  price: number;
  inStock: boolean;
}

export default function AddToCart({ productId, productName, price, inStock }: AddToCartProps) {
  const [quantity, setQuantity] = useState(1);
  const [status, setStatus] = useState<"idle" | "adding" | "added">("idle");

  const handleAdd = async () => {
    setStatus("adding");
    // Simulate an API call to FastAPI: POST /api/cart
    await new Promise((r) => setTimeout(r, 600));
    setStatus("added");
    setTimeout(() => setStatus("idle"), 2000);
  };

  if (!inStock) {
    return (
      <div style={{ padding: "1rem", background: "#fee2e2", borderRadius: "6px", color: "#991b1b" }}>
        Out of stock
      </div>
    );
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
      <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
        Qty:
        <input
          type="number"
          min={1}
          max={99}
          value={quantity}
          onChange={(e) => setQuantity(Math.max(1, Number(e.target.value)))}
          style={{ width: "60px", padding: "0.4rem", fontSize: "1rem" }}
        />
      </label>

      <button
        onClick={handleAdd}
        disabled={status !== "idle"}
        style={{
          padding: "0.6rem 1.4rem",
          background: status === "added" ? "#16a34a" : "#2563eb",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: status !== "idle" ? "not-allowed" : "pointer",
          fontSize: "1rem",
          transition: "background 0.2s",
        }}
      >
        {status === "idle" && `Add ${quantity} to Cart — $${(price * quantity).toFixed(2)}`}
        {status === "adding" && "Adding…"}
        {status === "added" && "Added ✓"}
      </button>

      <span style={{ fontSize: "0.85rem", color: "#6b7280" }}>
        Product #{productId}
      </span>
    </div>
  );
}
