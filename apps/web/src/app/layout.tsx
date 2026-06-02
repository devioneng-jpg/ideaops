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
      <body className="min-h-screen antialiased">
        {/* Ambient glow behind page */}
        <div className="pointer-events-none fixed inset-0 overflow-hidden">
          <div className="absolute -top-40 left-1/2 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-accent-purple/[0.04] blur-[120px]" />
          <div className="absolute -top-20 left-1/3 h-[400px] w-[600px] -translate-x-1/2 rounded-full bg-accent-blue/[0.06] blur-[100px]" />
        </div>

        <div className="relative">
          <header className="border-b border-white/[0.06] px-6 py-4">
            <nav className="mx-auto flex max-w-5xl items-center justify-between">
              <a href="/" className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-accent">
                  <svg
                    className="h-4 w-4 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2.5}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5.002 5.002 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    />
                  </svg>
                </div>
                <span className="text-lg font-semibold tracking-tight">
                  IdeaOps
                </span>
              </a>
              <a
                href="/ideas"
                className="text-sm text-gray-400 transition-colors hover:text-gray-200"
              >
                History
              </a>
            </nav>
          </header>
          <main className="mx-auto max-w-5xl px-6 py-12">{children}</main>
        </div>
      </body>
    </html>
  );
}
