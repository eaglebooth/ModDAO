import type { Metadata } from "next";
import "./globals.css";
import { Shell } from "@/components/Shell";
import { WalletProvider } from "@/components/WalletProvider";

export const metadata: Metadata = {
  title: "ModDAO | Moderation quality, settled on-chain",
  description: "Comparative AI review and transparent moderator payout ledgers on GenLayer.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body><WalletProvider><Shell>{children}</Shell></WalletProvider></body>
    </html>
  );
}
