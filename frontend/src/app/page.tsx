import Link from "next/link";
import { ArrowRight, CheckCircle2 } from "lucide-react";
import { ContractBar } from "@/components/ContractBar";
import { Reveal } from "@/components/Reveal";

export default function HomePage() {
  return <>
    <section className="hero"><div className="wrap hero-grid">
      <Reveal><span className="kicker">GenLayer moderation payroll</span><h1 className="display">PAY FOR JUDGMENT, NOT MESSAGE COUNT.</h1><p className="lede">ModDAO reads public support logs, reaches semantic AI consensus, protects a timed appeal, and settles native GEN to moderators from on-chain custody.</p><div style={{display:"flex",gap:12,flexWrap:"wrap",marginTop:28}}><Link className="primary" href="/evaluations/new">Start an audit <ArrowRight size={16}/></Link><Link className="secondary" href="/how-it-works">Understand scoring</Link></div></Reveal>
      <Reveal className="signal-board" delay={.1}><div className="mono" style={{fontSize:11,color:"#9ea7b8",marginBottom:8}}>LIVE REVIEW SIGNAL / SAMPLE RUBRIC</div>{[["A","Helpful response",28],["B","Accurate resolution",46],["C","Policy compliance",19]].map(([label,title,score]) => <div className="signal-row" key={String(label)}><span className="avatar">{label}</span><div><strong>{title}</strong><div style={{height:4,background:"#313745",marginTop:8}}><div style={{height:4,width:`${Number(score)*2}%`,maxWidth:"100%",background:"var(--yellow)"}}/></div></div><span className="score">{score}</span></div>)}<div style={{paddingTop:18,display:"flex",justifyContent:"space-between"}}><strong>TOTAL BAND</strong><strong style={{color:"var(--yellow)"}}>EXCELLENT / 93</strong></div></Reveal>
    </div></section>
    <ContractBar />
    <section className="band dark"><div className="wrap"><Reveal><span className="kicker" style={{color:"var(--yellow)"}}>Audit pipeline</span><h2 className="display section-title" style={{marginTop:18}}>SEPARATE REVIEW FROM PAYMENT.</h2></Reveal><div className="steps">{[["01","Fund","Admin deposits native GEN into contract custody."],["02","Request","Moderator or admin submits a unique cycle log."],["03","Review","Validators compare outcome, score band, and policy failures."],["04","Settle","A timed appeal completes before GEN transfers once."]].map(([number,title,copy],index) => <Reveal className="step" key={number} delay={index*.06}><b className="mono">{number}</b><h3 style={{fontSize:22,margin:"18px 0 10px"}}>{title}</h3><p>{copy}</p></Reveal>)}</div></div></section>
    <section className="band"><div className="wrap"><Reveal><span className="kicker">Why the V3 contract matters</span><h2 className="display section-title" style={{marginTop:18}}>THE TREASURY IS NOT A PRETEND NUMBER.</h2></Reveal><div className="grid2" style={{marginTop:46}}>{["Pay tiers are native GEN amounts fixed at registration.","Finalization transfers the selected tier to the moderator wallet.","NO_PAYOUT creates an auditable zero-value settlement.","NEEDS_EVIDENCE opens a bounded correction path instead of guessing."].map((copy) => <Reveal key={copy} className="notice ok"><CheckCircle2 size={17} style={{verticalAlign:"middle",marginRight:8}}/>{copy}</Reveal>)}</div></div></section>
  </>;
}
