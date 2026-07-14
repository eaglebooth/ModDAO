import { WorkflowPage } from "@/components/WorkflowPage";

export default async function FinalizePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <WorkflowPage mode="finalize" id={id} kicker="Settlement / finalize_evaluation" title="TRANSFER THE RULING ONCE." copy="After the appeal window closes, finalization checks native GEN custody and transfers the selected tier to the registered moderator wallet. A zero-tier ruling records a no-payout settlement." steps={["Confirm the appeal window has closed or the appeal jury has ruled.", "Compare the proposed payout with available treasury.", "Finalize once and verify the recipient transfer in Explorer."]} />;
}
