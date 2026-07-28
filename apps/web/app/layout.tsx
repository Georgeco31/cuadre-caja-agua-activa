import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agua Activa ERP",
  description: "Gestión operativa de Agua Activa",
  icons: {
    icon: "/brand/logo-icon.png",
    apple: "/brand/logo-icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
