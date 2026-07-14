"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, BookOpen, Menu, ShieldCheck, Users, Wallet } from "lucide-react";
import { useWallet } from "./WalletProvider";

const links = [
  ["Overview", "/", Activity],
  ["Moderators", "/moderators", Users],
  ["Evaluations", "/evaluations", ShieldCheck],
  ["How it works", "/how-it-works", BookOpen],
] as const;

export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const { address, busy, connect } = useWallet();
  const contract = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "";

  return <div className="shell">
    <aside className="rail">
      <Link href="/" className="brand"><span className="brand-mark">M</span>MODDAO</Link>
      <nav>
        {links.map(([label, href, Icon]) => <Link key={href} href={href} className={`nav-link ${path === href ? "active" : ""}`}><Icon size={16} style={{marginRight:9,verticalAlign:"middle"}}/>{label}</Link>)}
        <Link className={`nav-link ${path.startsWith("/treasury") ? "active" : ""}`} href="/treasury">Treasury</Link>
        <Link className={`nav-link ${path === "/activity" ? "active" : ""}`} href="/activity">Explorer proof</Link>
      </nav>
      <div className="rail-bottom">
        <div className="mono" style={{fontSize:11,color:"#8f98aa"}}>{contract ? `${contract.slice(0,8)}...${contract.slice(-6)}` : "V3 AWAITING DEPLOY"}</div>
        <button className="wallet-btn" onClick={connect}><Wallet size={16}/>{address ? `${address.slice(0,5)}...${address.slice(-4)}` : busy ? "CONNECTING" : "CONNECT WALLET"}</button>
      </div>
    </aside>
    <header className="topbar">
      <Link href="/" className="brand mobile-menu"><span className="brand-mark">M</span></Link>
      <span className="mono top-status" style={{fontSize:12}}><span className="dot"/>{contract ? "STUDIONET / V3 CONNECTED" : "STUDIONET / V3 PENDING"}</span>
      <div style={{display:"flex",gap:12}}><Link href="/setup" className="secondary">Verify</Link><Link href="/evaluations/new" className="primary">New evaluation</Link><Menu className="mobile-menu"/></div>
    </header>
    <main className="content">{children}</main>
    <footer className="footer"><div className="wrap"><strong>MODDAO / PAYOUT PROTOCOL</strong><p className="meta" style={{marginTop:8}}>Comparative review. Timed appeal. Native GEN settlement.</p></div></footer>
  </div>;
}
