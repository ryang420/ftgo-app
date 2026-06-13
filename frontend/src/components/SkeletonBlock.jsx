export default function SkeletonBlock({ className = "" }) {
  return (
    <div
      className={`animate-pulse rounded-[1.5rem] border border-orange-100 bg-orange-100/70 ${className}`}
    />
  );
}
