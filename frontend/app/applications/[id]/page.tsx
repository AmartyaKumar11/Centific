import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ApplicationHeader } from "@/components/Application/ApplicationHeader";
import { ApplicationSummary } from "@/components/Application/ApplicationSummary";
import { Timeline } from "@/components/Application/Timeline";
import { api } from "@/lib/api";
import { Application } from "@/types/application";

export default function ApplicationDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState<Application | null>(null);

  useEffect(() => {
    if (!id) {
      navigate("/", { replace: true });
      return;
    }
    let mounted = true;
    api
      .getApplication(id)
      .then((data) => {
        if (!mounted) return;
        setApplication(data);
      })
      .catch(() => {
        if (!mounted) return;
        navigate("/", { replace: true });
      });
    return () => {
      mounted = false;
    };
  }, [id, navigate]);

  if (!application) {
    return (
      <main className="mx-auto flex w-full max-w-5xl flex-col gap-5 px-4 py-6 md:px-6">
        <p className="text-sm text-slate-500">Loading application...</p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-5 px-4 py-6 md:px-6">
      <ApplicationHeader application={application} />
      <ApplicationSummary application={application} />
      <Timeline steps={application.timeline} />
    </main>
  );
}
