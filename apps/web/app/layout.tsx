import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cuadre de Caja Agua Activa",
  description: "Cuadre diario de caja para Agua Activa",
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
