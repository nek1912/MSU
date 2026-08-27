export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div className={`animate-pulse rounded-[var(--radius-md)] bg-[var(--surface-overlay)] ${className}`} aria-hidden="true" />
  );
}
