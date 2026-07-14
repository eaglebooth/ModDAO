import { ContractBar } from "@/components/ContractBar";
import { ConnectionVerifier } from "@/components/ConnectionVerifier";
import { PageHead } from "@/components/PageHead";

export default function SetupPage() {
  return <>
    <PageHead kicker="Deployment identity" title="VERIFY THE DEPLOYER-OWNED CONTRACT." copy="ModDAO V3 assigns the administrator in its constructor. There is no first-caller initialization transaction to front-run." />
    <ContractBar />
    <section className="band"><div className="wrap"><ConnectionVerifier /></div></section>
  </>;
}
