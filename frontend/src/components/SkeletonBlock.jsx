export default function SkeletonBlock({ className = "" }) {
  return (
    <div
      className={`animate-pulse rounded-[1.5rem] border border-white/10 bg-white/[0.045] ${className}`}
    />
  );
}
