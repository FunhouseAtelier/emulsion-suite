import { useState } from "react";

interface Review {
  author: string;
  rating: number;
  text: string;
}

interface ReviewCarouselProps {
  productId: string;
}

// In a real app these would be fetched from FastAPI
const MOCK_REVIEWS: Record<string, Review[]> = {
  "1": [
    { author: "Alice", rating: 5, text: "Best widget I've ever owned." },
    { author: "Bob", rating: 4, text: "Great quality, fast shipping." },
    { author: "Carol", rating: 5, text: "Worth every penny." },
  ],
  "2": [
    { author: "Dave", rating: 4, text: "Solid gadget, meets expectations." },
    { author: "Eve", rating: 3, text: "Good but a bit pricey." },
  ],
  "3": [{ author: "Frank", rating: 5, text: "Surprisingly versatile." }],
};

function Stars({ rating }: { rating: number }) {
  return (
    <span aria-label={`${rating} out of 5 stars`}>
      {"★".repeat(rating)}
      {"☆".repeat(5 - rating)}
    </span>
  );
}

export default function ReviewCarousel({ productId }: ReviewCarouselProps) {
  const reviews = MOCK_REVIEWS[productId] ?? [];
  const [index, setIndex] = useState(0);

  if (reviews.length === 0) {
    return <p style={{ color: "#6b7280" }}>No reviews yet.</p>;
  }

  // index is always within bounds: initialised to 0 and clamped to reviews.length in navigate()
  const review = reviews[index]!;

  return (
    <div
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: "8px",
        padding: "1.5rem",
        maxWidth: "480px",
      }}
    >
      <div
        style={{
          marginBottom: "0.5rem",
          color: "#f59e0b",
          fontSize: "1.25rem",
        }}
      >
        <Stars rating={review.rating} />
      </div>
      <p style={{ margin: "0 0 0.75rem" }}>"{review.text}"</p>
      <p style={{ margin: 0, fontSize: "0.875rem", color: "#6b7280" }}>
        — {review.author}
      </p>

      {reviews.length > 1 && (
        <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
          <button
            onClick={() =>
              setIndex((i) => (i - 1 + reviews.length) % reviews.length)
            }
            aria-label="Previous review"
            style={{ padding: "0.4rem 0.8rem", cursor: "pointer" }}
          >
            ‹
          </button>
          <span
            style={{
              alignSelf: "center",
              fontSize: "0.85rem",
              color: "#6b7280",
            }}
          >
            {index + 1} / {reviews.length}
          </span>
          <button
            onClick={() => setIndex((i) => (i + 1) % reviews.length)}
            aria-label="Next review"
            style={{ padding: "0.4rem 0.8rem", cursor: "pointer" }}
          >
            ›
          </button>
        </div>
      )}
    </div>
  );
}
