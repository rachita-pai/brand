import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pai Brand Demo - AI Twins for Consumer Research",
  description: "Experience instant consumer insights through AI Twins",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* Merriweather Font - Primary */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400&display=swap"
          rel="stylesheet"
        />
        {/* Instrument Serif - Display Headings */}
        <link
          href="https://fonts.googleapis.com/css2?family=Instrument+Serif:wght@400&display=swap"
          rel="stylesheet"
        />
        {/* Instrument Sans - Chat UI */}
        <link
          href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
