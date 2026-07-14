"use client";

import Link from "next/link";
import { ArrowUpRight, RefreshCw } from "lucide-react";
import { useState } from "react";
import { readContract } from "@/lib/genlayer";

export function OnchainList({ kind }: { kind: "moderators" | "evaluations" }) {
  const contract = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "";
  const [rows, setRows] = useState<Record<string, string>[]>([]);
  const [message, setMessage] = useState(contract ? "Press sync to read ModDAO V3." : "ModDAO V3 is awaiting deployment.");

  async function sync() {
    if (!contract) return;
    setMessage("Reading Studionet...");
    const state = await readContract("get_contract_state", [], contract);
    if (!state.success || typeof state.data !== "string") {
      setMessage(state.error || "Read failed");
      return;
    }
    const parsed = JSON.parse(state.data);
    const total = Number(kind === "moderators" ? parsed.mod_count : parsed.eval_count);
    const functionName = kind === "moderators" ? "get_moderator" : "get_evaluation";
    const results = await Promise.all(Array.from({ length: total }, (_, index) => readContract(functionName, [index], contract)));
    setRows(results.flatMap((result) => {
      try { return result.success && typeof result.data === "string" ? [JSON.parse(result.data)] : []; }
      catch { return []; }
    }));
    setMessage(total ? `Synced ${total} ${kind}.` : `No ${kind} recorded on V3 yet.`);
  }

  return <div className="wrap">
    <div className="contract-inner" style={{borderBottom:"1px solid var(--line)",paddingBottom:16}}><span className="meta">{message}</span><button className="secondary" onClick={sync} disabled={!contract}><RefreshCw size={15}/>SYNC CONTRACT</button></div>
    {rows.length === 0 ? <div className="empty"><h2 className="display" style={{fontSize:34}}>NO FAKE ROWS.</h2><p>Production only shows records returned by the deployed ModDAO V3 contract.</p><Link className="primary" href={kind === "moderators" ? "/moderators/new" : "/evaluations/new"}>Create the first record</Link></div> : <div className="list">{rows.map((row) => kind === "moderators" ? <div className="row" key={row.id}><b>#{row.id}</b><div><strong>{row.name}</strong><div className="meta mono">{row.wallet}</div></div><span>{row.active === "1" ? "ACTIVE" : "INACTIVE"}</span><span>{row.standard_pay} / {row.excellent_pay}</span><span/></div> : <Link className="row" href={`/evaluations/${row.id}`} key={row.id}><b>#{row.id}</b><div><strong>{row.cycle_ref}</strong><div className="meta">Moderator #{row.mod_id}</div></div><span>{row.status}</span><span>{row.score}/100</span><ArrowUpRight size={16}/></Link>)}</div>}
  </div>;
}
