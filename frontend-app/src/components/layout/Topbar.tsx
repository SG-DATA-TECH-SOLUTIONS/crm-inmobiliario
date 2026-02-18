import { HiOutlineBell, HiOutlineArrowRightOnRectangle } from 'react-icons/hi2'
import { useAuthStore } from '@/store/authStore'

export function Topbar() {
  const { user, org, logout } = useAuthStore()

  return (
    <header className="sticky top-0 z-20 bg-white border-b border-gray-200 h-14">
      <div className="flex items-center justify-between h-full px-6">
        {/* Left - Breadcrumb area */}
        <div />

        {/* Right - Actions */}
        <div className="flex items-center gap-4">
          {/* Org badge */}
          {org && (
            <span className="text-xs font-medium text-primary-700 bg-primary-50 px-3 py-1 rounded-full">
              {org.name}
            </span>
          )}

          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-gray-100 text-gray-500">
            <HiOutlineBell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
          </button>

          {/* User */}
          <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
            <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-semibold">
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-medium text-gray-700 leading-tight">
                {user?.email || 'Usuario'}
              </p>
            </div>
            <button
              onClick={logout}
              className="p-2 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600"
              title="Cerrar sesión"
            >
              <HiOutlineArrowRightOnRectangle className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
