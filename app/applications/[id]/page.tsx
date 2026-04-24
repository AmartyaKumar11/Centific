import { notFound } from "next/navigation";
import { ApplicationHeader } from "@/components/Application/ApplicationHeader";
import { ApplicationSummary } from "@/components/Application/ApplicationSummary";
import { Timeline } from "@/components/Application/Timeline";
import { applications } from "@/lib/mockData";

export default async function ApplicationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const application = applications.find((item) => item.id === id);

  if (!application) {
    notFound();
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-5 px-4 py-6 md:px-6">
      <ApplicationHeader application={application} />
      <ApplicationSummary application={application} />
      <Timeline steps={application.timeline} />
    </main>
  );
}
