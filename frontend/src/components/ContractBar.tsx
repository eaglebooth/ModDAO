import Link from "next/link";

export function ContractBar() {
  const address = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "";
  return <div className="contract-bar"><div className="wrap contract-inner"><div><span className="dot"/><strong>{address ? "ModDAO V3 connected" : "ModDAO V3 awaits deployment"}</strong><div className="meta mono" style={{marginTop:5}}>{address || "Deploy contracts/ModDAO.py, then add its Studionet address."}</div></div><Link href="/activity" className="secondary">VERIFY CONNECTION</Link></div></div>;
}
