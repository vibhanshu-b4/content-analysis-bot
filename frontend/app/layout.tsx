import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Video RAG Analyzer",
  description: "Compare two social media videos using AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}

