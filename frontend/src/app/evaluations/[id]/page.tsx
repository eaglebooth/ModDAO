"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { readContract } from "@/lib/genlayer";

export default function EvaluationPage(){
  const {id}=useParams<{id:string}>();
  const contract=process.env.NEXT_PUBLIC_CONTRACT_ADDRESS||"";
  const[data,setData]=useState<Record<string,string>|null>(null);
  const[msg,setMsg]=useState(contract?"Press sync to load this evaluation.":"V3 deployment pending.");
  async function sync(){if(!contract)return;const r=await readContract("get_evaluation",[Number(id)],contract);if(r.success&&typeof r.data==="string"){try{setData(JSON.parse(r.data));setMsg("Synced from Studionet.")}catch{setMsg("Malformed contract response.")}}else setMsg(r.error||"Read failed")}
  const actions=[["Review",`/evaluations/${id}/review`],["Replace evidence",`/evaluations/${id}/evidence`],["Appeal",`/evaluations/${id}/appeal`],["Appeal jury",`/evaluations/${id}/appeal/review`],["Settle payout",`/evaluations/${id}/finalize`]];
  return <><section className="page-head"><div className="wrap"><span className="kicker">Evaluation / {id}</span><h1 className="display">AUDIT PACKET #{id}</h1><p className="lede">{msg}</p><button className="secondary" onClick={sync} disabled={!contract}>SYNC EVALUATION</button></div></section><section className="band"><div className="wrap action-layout"><aside className="instructions"><span className="kicker">Available actions</span><ol>{actions.map(([l,h],i)=><li key={h}><b>{i+1}</b><Link href={h}>{l}</Link></li>)}</ol></aside><div className="packet"><div className="packet-head"><strong className="mono">ON-CHAIN EVALUATION</strong><span>{data?.status||"NOT LOADED"}</span></div><div className="packet-body">{data?Object.entries(data).map(([k,v])=><div className="row" key={k}><strong className="mono">{k}</strong><span style={{gridColumn:"span 3",overflowWrap:"anywhere"}}>{v}</span><span/></div>):<div className="empty"><p>No fabricated evaluation is shown before a successful contract read.</p></div>}</div></div></div></section></>;
}
