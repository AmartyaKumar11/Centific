"use client";

type DesktopBackgroundProps = {
  backgroundImageUrl?: string;
};

export function DesktopBackground({ backgroundImageUrl }: DesktopBackgroundProps) {
  if (backgroundImageUrl) {
    return (
      <div
        className="absolute inset-0 -z-10 bg-cover bg-center"
        style={{ backgroundImage: `url(${backgroundImageUrl})` }}
      />
    );
  }

  return (
    <div className="absolute inset-0 -z-10 overflow-hidden">
      <div className="desktop-bg-shift absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50" />
      <div
        className="absolute -left-24 top-20 h-64 w-64 rounded-full bg-blue-300/10 blur-3xl desktop-float-1"
        aria-hidden
      />
      <div
        className="absolute right-10 top-24 h-72 w-72 rounded-full bg-violet-300/10 blur-3xl desktop-float-2"
        aria-hidden
      />
      <div
        className="absolute bottom-10 left-1/3 h-56 w-56 rounded-full bg-cyan-300/10 blur-3xl desktop-float-3"
        aria-hidden
      />
    </div>
  );
}
