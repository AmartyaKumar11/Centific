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

  return <div className="absolute inset-0 -z-10 bg-gradient-to-br from-blue-900 via-blue-800 to-slate-900" />;
}
