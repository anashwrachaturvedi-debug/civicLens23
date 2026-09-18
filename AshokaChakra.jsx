export default function AshokaChakra({ size = 24, className = "" }) {
  const spokes = Array.from({ length: 24 });
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      className={className}
      role="img"
      aria-label="Ashoka Chakra"
    >
      <circle cx="50" cy="50" r="46" fill="none" stroke="#000080" strokeWidth="3" />
      {spokes.map((_, i) => {
        const angle = (i * 360) / 24;
        return (
          <line
            key={i}
            x1="50"
            y1="50"
            x2="50"
            y2="6"
            stroke="#000080"
            strokeWidth="2"
            transform={`rotate(${angle} 50 50)`}
          />
        );
      })}
      <circle cx="50" cy="50" r="5" fill="#000080" />
    </svg>
  );
}