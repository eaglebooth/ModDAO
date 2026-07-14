import Link from "next/link";
import { PageHead } from "@/components/PageHead";
import { OnchainList } from "@/components/OnchainList";

export default function EvaluationsPage() {
  return <><PageHead kicker="Evaluation registry" title="EVERY CYCLE HAS A STATE." copy="Review pending logs, proposed payout tiers, evidence revisions, timed appeals, and native GEN settlements directly from ModDAO V3."/><div className="wrap" style={{marginBottom:30}}><Link className="primary" href="/evaluations/new">Request evaluation</Link></div><OnchainList kind="evaluations"/></>;
}
