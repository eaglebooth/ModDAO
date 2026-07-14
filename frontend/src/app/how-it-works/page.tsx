import { PageHead } from "@/components/PageHead";
import { Reveal } from "@/components/Reveal";

const rows = [
  ["Helpfulness / 30", "Respect, patience, and useful guidance."],
  ["Accuracy / 50", "Correct resolution without harmful invention."],
  ["Compliance / 20", "Consistent rules without abuse."],
  ["90-100", "EXCELLENT native GEN payout tier."],
  ["75-89", "STANDARD native GEN payout tier."],
  ["Below 75", "Finalized with no payout."],
  ["Weak evidence", "NEEDS_EVIDENCE; replace the log and review again."],
];

export default function HowItWorksPage() {
  return <>
    <PageHead kicker="Full product guide" title="READ THE RUBRIC BEFORE THE LOGS." copy="ModDAO V3 exposes its evidence rules, semantic consensus, timed appeal, and real settlement lifecycle so every participant can predict the on-chain outcome." />
    <section className="band"><div className="wrap action-layout">
      <Reveal><h2 className="display" style={{fontSize:38}}>SCORING MAP</h2><p className="lede">Validators may phrase comments differently, but comparative consensus requires agreement on the payout tier, score band, and serious policy failures.</p></Reveal>
      <div className="list">{rows.map(([label, copy]) => <Reveal className="scoring-row" key={label}><strong className="mono">{label}</strong><span>{copy}</span></Reveal>)}</div>
    </div></section>
    <section className="band blue"><div className="wrap"><h2 className="display section-title">FUND / REVIEW / APPEAL / SETTLE</h2><p style={{maxWidth:700,lineHeight:1.8,marginTop:24}}>The deployer funds native GEN custody. A review proposes a payout and opens a 24-hour appeal window. The moderator may appeal once. After the window, or after appeal review, finalization transfers GEN to the registered moderator wallet exactly once.</p></div></section>
  </>;
}
