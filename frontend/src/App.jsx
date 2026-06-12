import { Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "./components/auth/ProtectedRoute";
import { AppShell } from "./components/layout/AppShell";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { AdminDashboard } from "./pages/dashboards/AdminDashboard";
import { DoctorDashboard } from "./pages/dashboards/DoctorDashboard";
import { PatientDashboard } from "./pages/dashboards/PatientDashboard";
import { PatientsPage } from "./pages/patients/PatientsPage";
import { PatientProfilePage } from "./pages/patients/PatientProfilePage";
import { DoctorsPage } from "./pages/doctors/DoctorsPage";
import { AppointmentsPage } from "./pages/appointments/AppointmentsPage";
import { DashboardRedirect } from "./pages/dashboard/DashboardRedirect";
import { EhrDashboard } from "./pages/ehr/EhrDashboard";
import { MedicalRecordsPage } from "./pages/ehr/MedicalRecordsPage";
import { PrescriptionsPage } from "./pages/ehr/PrescriptionsPage";
import { LabReportsPage } from "./pages/ehr/LabReportsPage";
import { TreatmentsPage } from "./pages/ehr/TreatmentsPage";
import { VaccinationsPage } from "./pages/ehr/VaccinationsPage";
import { AllergiesPage } from "./pages/ehr/AllergiesPage";
import { TimelinePage } from "./pages/ehr/TimelinePage";
import { AiDashboard } from "./pages/ai/AiDashboard";
import { DiseasePredictionPage } from "./pages/ai/DiseasePredictionPage";
import { OutcomePredictionPage } from "./pages/ai/OutcomePredictionPage";
import { TreatmentRecommendationPage } from "./pages/ai/TreatmentRecommendationPage";
import { ReportAnalysisPage } from "./pages/ai/ReportAnalysisPage";
import { OperationsDashboard } from "./pages/operations/OperationsDashboard";
import { BedsPage } from "./pages/operations/BedsPage";
import { WardsPage } from "./pages/operations/WardsPage";
import { ResourcesPage } from "./pages/operations/ResourcesPage";
import { ForecastPage } from "./pages/operations/ForecastPage";
import { StaffPage } from "./pages/operations/StaffPage";
import { EmergencyPage } from "./pages/operations/EmergencyPage";
import { NotificationsPage } from "./pages/operations/NotificationsPage";
import { SchedulingPage } from "./pages/operations/SchedulingPage";
import { AssistantDashboard } from "./pages/assistant/AssistantDashboard";
import { ChatAssistantPage } from "./pages/assistant/ChatAssistantPage";
import { PatientAssistantPage } from "./pages/assistant/PatientAssistantPage";
import { DoctorCopilotPage } from "./pages/assistant/DoctorCopilotPage";
import { KnowledgeBasePage } from "./pages/assistant/KnowledgeBasePage";
import { ExecutiveInsightsPage } from "./pages/assistant/ExecutiveInsightsPage";
import { ReportsCenterPage } from "./pages/assistant/ReportsCenterPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardRedirect />} />
        <Route path="admin" element={<AdminDashboard />} />
        <Route path="doctor" element={<DoctorDashboard />} />
        <Route path="patient" element={<PatientDashboard />} />
      </Route>

      <Route
        path="/patients"
        element={
          <ProtectedRoute roles={["Admin", "Hospital Staff", "Doctor"]}>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<PatientsPage />} />
        <Route path=":patientId" element={<PatientProfilePage />} />
      </Route>

      <Route
        path="/doctors"
        element={
          <ProtectedRoute roles={["Admin", "Hospital Staff"]}>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<DoctorsPage />} />
      </Route>

      <Route
        path="/appointments"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<AppointmentsPage />} />
      </Route>

      <Route
        path="/ehr"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<EhrDashboard />} />
        <Route path="medical-records" element={<MedicalRecordsPage />} />
        <Route path="prescriptions" element={<PrescriptionsPage />} />
        <Route path="lab-reports" element={<LabReportsPage />} />
        <Route path="treatments" element={<TreatmentsPage />} />
        <Route path="vaccinations" element={<VaccinationsPage />} />
        <Route path="allergies" element={<AllergiesPage />} />
        <Route path="timeline" element={<TimelinePage />} />
      </Route>

      <Route
        path="/ai"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<AiDashboard />} />
        <Route path="disease-prediction" element={<DiseasePredictionPage />} />
        <Route path="outcome-prediction" element={<OutcomePredictionPage />} />
        <Route path="treatment-recommendation" element={<TreatmentRecommendationPage />} />
        <Route path="report-analysis" element={<ReportAnalysisPage />} />
      </Route>

      <Route
        path="/operations"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<OperationsDashboard />} />
        <Route path="beds" element={<BedsPage />} />
        <Route path="wards" element={<WardsPage />} />
        <Route path="resources" element={<ResourcesPage />} />
        <Route path="forecast" element={<ForecastPage />} />
        <Route path="staff" element={<StaffPage />} />
        <Route path="scheduling" element={<SchedulingPage />} />
        <Route path="emergency" element={<EmergencyPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      <Route
        path="/assistant"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<AssistantDashboard />} />
        <Route path="chat" element={<ChatAssistantPage />} />
        <Route path="patient" element={<PatientAssistantPage />} />
        <Route path="doctor" element={<DoctorCopilotPage />} />
        <Route path="knowledge" element={<KnowledgeBasePage />} />
        <Route path="insights" element={<ExecutiveInsightsPage />} />
        <Route path="reports" element={<ReportsCenterPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
