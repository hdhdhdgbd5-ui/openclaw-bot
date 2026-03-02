import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'

// Layouts
import MainLayout from './layouts/MainLayout'
import AuthLayout from './layouts/AuthLayout'

// Pages
import Dashboard from './pages/Dashboard'
import Dashboards from './pages/Dashboards'
import Datasets from './pages/Datasets'
import DataSources from './pages/DataSources'
import Visualizations from './pages/Visualizations'
import MLModels from './pages/MLModels'
import Predictions from './pages/Predictions'
import Alerts from './pages/Alerts'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import Login from './pages/Login'
import Register from './pages/Register'
import Landing from './pages/Landing'

// Components
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={
        isAuthenticated ? <Navigate to="/dashboards" replace /> : <Landing />
      } />
      
      {/* Auth routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route path="/dashboards" element={<Dashboards />} />
          <Route path="/dashboard/:id" element={<Dashboard />} />
          <Route path="/datasets" element={<Datasets />} />
          <Route path="/data-sources" element={<DataSources />} />
          <Route path="/visualizations" element={<Visualizations />} />
          <Route path="/ml-models" element={<MLModels />} />
          <Route path="/predictions" element={<Predictions />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
