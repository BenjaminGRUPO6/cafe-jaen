import { MotionConfig } from "framer-motion";
import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AdminPage } from "./features/admin/AdminPage";
import { AdvisorPage } from "./features/advisor/AdvisorPage";
import { LoginPage } from "./features/auth/LoginPage";
import { RegisterPage } from "./features/auth/RegisterPage";
import { RequireAdmin } from "./features/auth/RequireAdmin";
import { RequireAuth } from "./features/auth/RequireAuth";
import { DecisionPage } from "./features/decision/DecisionPage";
import { ForecastPage } from "./features/forecast/ForecastPage";
import { LivePricePage } from "./features/live/LivePricePage";
import { AuthProvider } from "./shared/auth/AuthContext";
import { Layout } from "./shared/components/Layout";
import { StatusMessage } from "./shared/components/StatusMessage";

// La librería de gráficos es pesada: se descarga solo al abrir el gráfico (carga rápida en 3G)
const ChartPage = lazy(() =>
  import("./features/live/ChartPage").then((module) => ({ default: module.ChartPage })),
);

// Las rutas están en español porque el caficultor las ve en la barra del navegador
export function App() {
  return (
    // Si el celular pide «reducir movimiento», las animaciones se desactivan
    <MotionConfig reducedMotion="user">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/ingresar" element={<LoginPage />} />
            <Route path="/registro" element={<RegisterPage />} />
            <Route
              element={
                <RequireAuth>
                  <Layout />
                </RequireAuth>
              }
            >
              <Route path="/" element={<LivePricePage />} />
              <Route
                path="/grafico"
                element={
                  <Suspense fallback={<StatusMessage loading />}>
                    <ChartPage />
                  </Suspense>
                }
              />
              <Route path="/vender" element={<DecisionPage />} />
              <Route path="/pronostico" element={<ForecastPage />} />
              <Route path="/asesor" element={<AdvisorPage />} />
              <Route
                path="/equipo"
                element={
                  <RequireAdmin>
                    <AdminPage />
                  </RequireAdmin>
                }
              />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </MotionConfig>
  );
}
