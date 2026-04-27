import type { CSSProperties, ReactNode } from "react";

type MacWindowCardProps = {
  title: string;
  children: ReactNode;
  /** Extra classes on the outer shell */
  className?: string;
  /** Extra classes on the body container */
  bodyClassName?: string;
  /** Optional right-side header content (badges, counts, actions) */
  headerRight?: ReactNode;
  style?: CSSProperties;
};

export function MacWindowCard({
  title,
  children,
  className = "",
  bodyClassName = "",
  headerRight,
  style,
}: MacWindowCardProps) {
  return (
    <article className={`theme-card ${className}`.trim()} style={style}>
      <div className="theme-card-head">
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
        </div>
        <div className="flex min-w-0 flex-1 items-center justify-end gap-2">
          <h3 className="truncate text-xs font-semibold text-slate-700">{title}</h3>
          {headerRight ? <div className="shrink-0">{headerRight}</div> : null}
        </div>
      </div>
      <div className={`p-3 ${bodyClassName}`.trim()}>{children}</div>
    </article>
  );
}
