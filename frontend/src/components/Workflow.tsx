"use client";

import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { writeContract } from "@/lib/genlayer";
import { useWallet } from "./WalletProvider";

export type WorkflowMode =
  | "fund"
  | "withdraw"
  | "register"
  | "deactivate"
  | "request"
  | "evidence"
  | "review"
  | "appeal"
  | "appeal-review"
  | "finalize";

const cfg: Record<WorkflowMode, [string, string]> = {
  fund: ["fund_treasury", "Deposit GEN"],
  withdraw: ["withdraw_unallocated", "Withdraw GEN"],
  register: ["register_moderator", "Register moderator"],
  deactivate: ["deactivate_moderator", "Deactivate moderator"],
  request: ["request_evaluation", "Create evaluation"],
  evidence: ["replace_evidence", "Replace evidence"],
  review: ["evaluate", "Run AI review"],
  appeal: ["submit_appeal", "Open appeal"],
  "appeal-review": ["evaluate_appeal", "Run appeal jury"],
  finalize: ["finalize_evaluation", "Settle payout"],
};

function parseGen(input: string): bigint {
  const value = input.trim();
  if (!/^\d+(\.\d{0,18})?$/.test(value)) throw new Error("Enter a valid GEN amount with up to 18 decimals.");
  const [whole, fraction = ""] = value.split(".");
  return BigInt(whole) * BigInt(10) ** BigInt(18) + BigInt((fraction + "0".repeat(18)).slice(0, 18));
}

export function Workflow({ mode, id }: { mode: WorkflowMode; id?: string }) {
  const contract = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "";
  const { address, connect } = useWallet();
  const [v, setV] = useState({
    amount: "",
    wallet: "",
    name: "",
    standard: "",
    excellent: "",
    mod: "",
    url: "",
    cycle: "",
    eval: id || "",
    appeal: "",
    evidence: "",
  });
  const [msg, setMsg] = useState("");
  const [bad, setBad] = useState(false);

  function update(key: keyof typeof v, value: string) {
    setV((state) => ({ ...state, [key]: value }));
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!address) {
      await connect();
      return;
    }
    if (!contract) {
      setBad(true);
      setMsg("ModDAO V3 needs a new Studio deployment before contract actions can run.");
      return;
    }

    try {
      let args: unknown[] = [];
      let value = BigInt(0);
      if (mode === "fund") value = parseGen(v.amount);
      if (mode === "withdraw") args = [parseGen(v.amount)];
      if (mode === "register") args = [v.wallet, v.name, parseGen(v.standard), parseGen(v.excellent)];
      if (mode === "deactivate") args = [BigInt(v.mod || 0)];
      if (mode === "request") args = [BigInt(v.mod || 0), v.url, v.cycle];
      if (mode === "evidence") args = [BigInt(v.eval || 0), v.evidence];
      if (mode === "review" || mode === "appeal-review" || mode === "finalize") args = [BigInt(v.eval || 0)];
      if (mode === "appeal") args = [BigInt(v.eval || 0), v.appeal];

      setBad(false);
      setMsg("Confirm in wallet, then wait for GenLayer finalization...");
      const result = await writeContract(cfg[mode][0], args, contract, value);
      setBad(!result.success);
      setMsg(
        result.success
          ? `Finalized: ${String(result.data ?? result.status ?? result.hash)}`
          : result.error || "Contract call failed",
      );
    } catch (error) {
      setBad(true);
      setMsg(error instanceof Error ? error.message : "Invalid form input");
    }
  }

  return (
    <form className="packet" onSubmit={submit}>
      <div className="packet-head"><strong className="mono">FUNCTION / {cfg[mode][0]}</strong><span>V3</span></div>
      <div className="packet-body">
        {(mode === "fund" || mode === "withdraw") && (
          <Field label="GEN amount">
            <input className="input" inputMode="decimal" placeholder="0.10" value={v.amount} onChange={(e) => update("amount", e.target.value)} required />
          </Field>
        )}
        {mode === "register" && <>
          <div className="grid2">
            <Field label="Moderator wallet"><input className="input mono" value={v.wallet} onChange={(e) => update("wallet", e.target.value)} required /></Field>
            <Field label="Display name"><input className="input" value={v.name} onChange={(e) => update("name", e.target.value)} required /></Field>
          </div>
          <div className="grid2">
            <Field label="Standard payout (GEN)"><input className="input" inputMode="decimal" value={v.standard} onChange={(e) => update("standard", e.target.value)} required /></Field>
            <Field label="Excellent payout (GEN)"><input className="input" inputMode="decimal" value={v.excellent} onChange={(e) => update("excellent", e.target.value)} required /></Field>
          </div>
        </>}
        {mode === "deactivate" && <Field label="Moderator ID"><input className="input" type="number" min="0" value={v.mod} onChange={(e) => update("mod", e.target.value)} required /></Field>}
        {mode === "request" && <>
          <Field label="Moderator ID"><input className="input" type="number" min="0" value={v.mod} onChange={(e) => update("mod", e.target.value)} required /></Field>
          <Field label="Public moderation log URL"><input className="input" type="url" value={v.url} onChange={(e) => update("url", e.target.value)} required /></Field>
          <Field label="Unique payroll cycle reference"><input className="input mono" value={v.cycle} onChange={(e) => update("cycle", e.target.value)} placeholder="DISCORD-2026-W28-MOD04" required /></Field>
        </>}
        {(mode === "review" || mode === "appeal-review" || mode === "finalize") && <Field label="Evaluation ID"><input className="input" type="number" min="0" value={v.eval} onChange={(e) => update("eval", e.target.value)} required /></Field>}
        {mode === "evidence" && <>
          <Field label="Evaluation ID"><input className="input" type="number" min="0" value={v.eval} onChange={(e) => update("eval", e.target.value)} required /></Field>
          <Field label="Replacement moderation log URL"><input className="input" type="url" value={v.evidence} onChange={(e) => update("evidence", e.target.value)} required /></Field>
        </>}
        {mode === "appeal" && <>
          <Field label="Evaluation ID"><input className="input" type="number" min="0" value={v.eval} onChange={(e) => update("eval", e.target.value)} required /></Field>
          <Field label="New appeal evidence URL"><input className="input" type="url" value={v.appeal} onChange={(e) => update("appeal", e.target.value)} required /></Field>
        </>}
        {msg && <div className={`notice ${bad ? "bad" : "ok"}`}>{msg}</div>}
        <button className={mode === "finalize" || mode === "deactivate" || mode === "withdraw" ? "danger" : "primary"}>
          {address ? cfg[mode][1] : "Connect wallet first"}<ArrowRight size={16} />
        </button>
      </div>
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="field"><label>{label}</label>{children}</div>;
}
