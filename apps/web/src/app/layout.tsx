import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IdeaOps",
  description: "Turn raw ideas into structured, actionable project briefs",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-950 text-gray-100 antialiased">
        <header className="border-b border-gray-800 px-6 py-4">
          <nav className="mx-auto flex max-w-4xl items-center justify-between">
            <a href="/" className="text-xl font-bold tracking-tight">
              IdeaOps
            </a>
            <a
              href="/ideas"
              className="text-sm text-gray-400 hover:text-gray-200"
            >
              History
            </a>
          </nav>
        </header>
        <main className="mx-auto max-w-4xl px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
