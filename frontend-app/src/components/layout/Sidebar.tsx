import { NavLink } from 'react-router-dom'
import {
  HiOutlineHome,
  HiOutlineBuildingOffice2,
  HiOutlineUsers,
  HiOutlineUserGroup,
  HiOutlineRectangleStack,
  HiOutlineCalendarDays,
  HiOutlineClipboardDocumentList,
  HiOutlineCog6Tooth,
  HiOutlineGlobeAlt,
  HiOutlineEnvelope,
} from 'react-icons/hi2'

const navItems = [
  { to: '/app/dashboard', label: 'Dashboard', icon: HiOutlineHome },
  { to: '/app/properties', label: 'Inmuebles', icon: HiOutlineBuildingOffice2 },
  { to: '/app/contacts', label: 'Contactos', icon: HiOutlineUsers },
  { to: '/app/leads', label: 'Leads', icon: HiOutlineRectangleStack },
  { to: '/app/opportunities', label: 'Oportunidades', icon: HiOutlineClipboardDocumentList },
  { to: '/app/calendar', label: 'Calendario', icon: HiOutlineCalendarDays },
  { to: '/app/teams', label: 'Equipos', icon: HiOutlineUserGroup },
  { to: '/app/portals', label: 'Portales', icon: HiOutlineGlobeAlt },
  { to: '/app/communications', label: 'Comunicaciones', icon: HiOutlineEnvelope },
  { to: '/app/settings', label: 'Ajustes', icon: HiOutlineCog6Tooth },
]

export function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 w-64 bg-sidebar flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-white/10">
        <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-sm">WC</span>
        </div>
        <span className="text-white font-semibold text-lg">Wide City</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-sidebar-active text-white'
                  : 'text-white/70 hover:bg-sidebar-hover hover:text-white'
              }`
            }
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-white/10">
        <p className="text-xs text-white/40">Wide City Realty CRM</p>
        <p className="text-xs text-white/30">v1.0.0</p>
      </div>
    </aside>
  )
}
