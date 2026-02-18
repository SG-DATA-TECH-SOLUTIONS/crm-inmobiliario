import { createBrowserRouter, Navigate } from 'react-router-dom'
import { MainLayout } from '@/layouts/MainLayout'
import { AuthLayout } from '@/layouts/AuthLayout'
import { ProtectedRoute } from './ProtectedRoute'
import { LoginPage } from '@/pages/auth/LoginPage'
import { DashboardPage } from '@/pages/dashboard/DashboardPage'
import { PropertyListPage } from '@/pages/properties/PropertyListPage'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <AuthLayout />,
    children: [
      { index: true, element: <LoginPage /> },
    ],
  },
  {
    path: '/app',
    element: <ProtectedRoute />,
    children: [
      {
        element: <MainLayout />,
        children: [
          { index: true, element: <Navigate to="dashboard" replace /> },
          { path: 'dashboard', element: <DashboardPage /> },
          { path: 'properties', element: <PropertyListPage /> },
          { path: 'properties/new', element: <div className="text-gray-500">Crear propiedad - Próximamente</div> },
          { path: 'properties/:id', element: <div className="text-gray-500">Detalle propiedad - Próximamente</div> },
          { path: 'contacts', element: <div className="text-gray-500">Contactos - Próximamente</div> },
          { path: 'leads', element: <div className="text-gray-500">Leads - Próximamente</div> },
          { path: 'opportunities', element: <div className="text-gray-500">Oportunidades - Próximamente</div> },
          { path: 'calendar', element: <div className="text-gray-500">Calendario - Próximamente</div> },
          { path: 'teams', element: <div className="text-gray-500">Equipos - Próximamente</div> },
          { path: 'portals', element: <div className="text-gray-500">Portales - Próximamente</div> },
          { path: 'communications', element: <div className="text-gray-500">Comunicaciones - Próximamente</div> },
          { path: 'settings', element: <div className="text-gray-500">Ajustes - Próximamente</div> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/app" replace />,
  },
])
