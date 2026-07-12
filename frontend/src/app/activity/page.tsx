import { ContractBar } from "@/components/ContractBar";
import { ConnectionVerifier } from "@/components/ConnectionVerifier";
import { PageHead } from "@/components/PageHead";

export default function ActivityPage(){
  return <><PageHead kicker="Verification surface" title="PROVE THE APP CALLS THE CONTRACT." copy="Read the deployed ModDAO V2 state from Studionet and open the same address in GenLayer Studio Explorer."/><ContractBar/><section className="band"><div className="wrap"><ConnectionVerifier/></div></section></>;
}
