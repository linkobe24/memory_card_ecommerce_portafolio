import type { Metadata } from "next";
import { Barlow } from "next/font/google";
import "./globals.css";
import { AppProviders } from "@/providers/AppProviders";
import { ReactNode } from "react";
import { Header } from "@/components/layout/Header";

const barlow = Barlow({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-barlow",
  display: "swap",
});

export const metadata: Metadata = {
  title: "MemoryCard - Tienda de Videojuegos",
  description: "E-commerce de videojuegos con catálogo completo de RAWG API",
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className={barlow.variable}>
        <AppProviders>
          <Header />
          {children}
        </AppProviders>
      </body>
    </html>
  );
}
