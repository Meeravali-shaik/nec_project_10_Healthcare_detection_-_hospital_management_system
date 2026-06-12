export function Card({ children, className = "" }) {
  return (
    <div
      className={`glass-card theme-surface rounded-[2rem] p-5 transition duration-200 ease-out hover:-translate-y-0.5 hover:shadow-glow ${className}`}
    >
      {children}
    </div>
  );
}
