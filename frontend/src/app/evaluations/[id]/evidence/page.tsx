import { WorkflowPage } from "@/components/WorkflowPage";

export default async function EvidencePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <WorkflowPage mode="evidence" id={id} kicker="Evidence correction" title="REPLACE AN UNREADABLE MODERATION LOG." copy="A moderator or admin can replace evidence only after the jury returns NEEDS_EVIDENCE. Two revisions are allowed before the case is locked." steps={["Confirm the evaluation status is NEEDS_EVIDENCE.", "Provide a public HTTPS replacement log.", "Submit it, then run the review again."]} />;
}
