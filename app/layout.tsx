import type { Metadata } from "next";
import "./globals.css";
import { TaskBar } from "@/app/components/TaskBar";

export const metadata: Metadata = {
  title: "Loan Prequalification Dashboard",
  description: "AI-infused BFSI loan prequalification dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <div className="min-h-screen pb-24">{children}</div>
        <TaskBar />
      </body>
    </html>
  );
}
