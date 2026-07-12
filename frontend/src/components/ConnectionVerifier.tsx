"use client";

import { ExternalLink, RefreshCw } from "lucide-react";
import { useState } from "react";
import { readContract } from "@/lib/genlayer";

type ContractState = { initialized: string; admin: string; treasury: string; mod_count: string; eval_count: string };

export function ConnectionVerifier(){
  const address=process.env.NEXT_PUBLIC_CONTRACT_ADDRESS||"";
  const[state,setState]=useState<ContractState|null>(null);
  const[message,setMessage]=useState(address?"Address configured. Run a read to verify the deployed contract.":"Contract address is not configured.");
  const[busy,setBusy]=useState(false);
  async function verify(){if(!address)return;setBusy(true);setMessage("Reading get_contract_state from Studionet...");const result=await readContract("get_contract_state",[],address);if(result.success&&typeof result.data==="string"){try{setState(JSON.parse(result.data));setMessage("Contract state refreshed successfully from ModDAO V2.");}catch{setMessage("The address responded, but the contract state payload was malformed.");}}else setMessage(result.error||"Contract read failed.");setBusy(false)}
  return <div className="packet"><div className="packet-head"><strong className="mono">LIVE STUDIONET CONNECTION</strong><span>{state?"VERIFIED":"READY"}</span></div><div className="packet-body"><div className={state?"notice ok":"notice"}><strong>{message}</strong><div className="meta mono" style={{marginTop:7}}>{address}</div></div>{state&&<div className="grid2">{Object.entries(state).map(([key,value])=><div className="signal-row" key={key}><span className="avatar">{key.slice(0,1).toUpperCase()}</span><div><strong className="mono">{key}</strong><div className="meta" style={{overflowWrap:"anywhere"}}>{value||"Not initialized"}</div></div><span/></div>)}</div>}<div style={{display:"flex",gap:12,flexWrap:"wrap"}}><button className="primary" onClick={verify} disabled={!address||busy}><RefreshCw size={16}/>{busy?"READING CONTRACT":"SYNC CONTRACT STATE"}</button>{address&&<a className="secondary" href={`https://explorer-studio.genlayer.com/address/${address}`} target="_blank" rel="noreferrer">OPEN EXPLORER <ExternalLink size={15}/></a>}</div></div></div>;
}
