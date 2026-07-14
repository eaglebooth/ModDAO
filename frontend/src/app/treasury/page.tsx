import Link from "next/link";
import { WorkflowPage } from "@/components/WorkflowPage";

export default function TreasuryPage() {
  return <>
    <WorkflowPage mode="fund" kicker="Treasury / payable deposit" title="FUND REAL MODERATOR PAYOUTS." copy="The admin deposits native GEN into contract custody. The attached wallet value, not a typed accounting number, becomes available treasury." steps={["Connect the contract deployer wallet.", "Enter the native GEN amount to custody.", "Confirm total funded and available treasury through contract sync."]} />
    <section className="band"><div className="wrap"><Link className="secondary" href="/treasury/withdraw">WITHDRAW UNALLOCATED GEN</Link></div></section>
  </>;
}
