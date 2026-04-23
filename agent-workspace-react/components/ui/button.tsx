import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

export function Button({
  children,
  onClick,
  variant = "secondary"
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: ButtonVariant;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn("btn", {
        "btn-primary": variant === "primary",
        "btn-secondary": variant === "secondary",
        "btn-ghost": variant === "ghost",
        "btn-danger": variant === "danger"
      })}
    >
      {children}
    </button>
  );
}
