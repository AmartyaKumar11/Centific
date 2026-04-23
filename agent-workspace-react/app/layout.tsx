import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent-First Loan Workspace",
  description: "Frontend-only case workspace for AI Loan Officer Agent"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
