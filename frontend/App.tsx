import { Navigate, Route, Routes } from "react-router-dom";
import { TaskBar } from "@/app/components/TaskBar";
import HomePage from "@/app/page";
import OverviewPage from "@/app/overview/page";
import ApplicationsPage from "@/app/applications/page";
import ApplicationDetailPage from "@/app/applications/[id]/page";
import HilReviewPage from "@/app/hil-review/page";
import ReportsPage from "@/app/reports/page";
import SettingsPage from "@/app/settings/page";
import LogoutPage from "@/app/logout/page";

export function App() {
  return (
    <div className="min-h-screen pb-24">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/overview" element={<OverviewPage />} />
        <Route path="/applications" element={<ApplicationsPage />} />
        <Route path="/applications/:id" element={<ApplicationDetailPage />} />
        <Route path="/apps" element={<ApplicationsPage />} />
        <Route path="/hil-review" element={<HilReviewPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/logout" element={<LogoutPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <TaskBar />
    </div>
  );
}
