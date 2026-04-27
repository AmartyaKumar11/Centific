import { Link } from "react-router-dom";

export default function LogoutPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl items-center justify-center px-6 py-8">
      <section className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-900">Logged Out</h1>
        <p className="mt-2 text-sm text-slate-600">Session ended successfully.</p>
        <Link
          to="/"
          className="mt-4 inline-flex rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Return to Desktop
        </Link>
      </section>
    </main>
  );
}
