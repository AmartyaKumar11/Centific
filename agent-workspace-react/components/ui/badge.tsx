import { cn } from "@/lib/utils";

type BadgeTone = "default" | "success" | "warning" | "danger" | "soft";

export function Badge({
  children,
  tone = "default"
}: {
  children: React.ReactNode;
  tone?: BadgeTone;
}) {
  return (
    <span
      className={cn("badge", {
        "badge-default": tone === "default",
        "badge-success": tone === "success",
        "badge-warning": tone === "warning",
        "badge-danger": tone === "danger",
        "badge-soft": tone === "soft"
      })}
    >
      {children}
    </span>
  );
}
