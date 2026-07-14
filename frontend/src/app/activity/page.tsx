import { ContractBar } from "@/components/ContractBar";
import { ConnectionVerifier } from "@/components/ConnectionVerifier";
import { PageHead } from "@/components/PageHead";

export default function ActivityPage(){
  return <><PageHead kicker="Verification surface" title="PROVE THE APP CALLS THE CONTRACT." copy="Read the deployed ModDAO V3 treasury, moderator, evaluation, and settlement counters from Studionet."/><ContractBar/><section className="band"><div className="wrap"><ConnectionVerifier/></div></section></>;
}
