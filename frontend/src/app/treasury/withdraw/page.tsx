import { WorkflowPage } from "@/components/WorkflowPage";

export default function WithdrawPage() {
  return <WorkflowPage mode="withdraw" kicker="Treasury / admin withdrawal" title="WITHDRAW ONLY AVAILABLE GEN." copy="The deployer may recover unallocated treasury. The contract checks the available balance before transferring native GEN back to the admin wallet." steps={["Connect the deployer wallet.", "Enter an amount no greater than available treasury.", "Sign the transfer and verify total withdrawals on-chain."]} />;
}
