export function Card({
  title,
  subtitle,
  right,
  children
}: {
  title: string;
  subtitle?: string;
  right?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="card">
      <header className="card-head">
        <div>
          <h3 className="card-title">{title}</h3>
          {subtitle ? <p className="card-sub">{subtitle}</p> : null}
        </div>
        {right}
      </header>
      <div className="card-body">{children}</div>
    </section>
  );
}
