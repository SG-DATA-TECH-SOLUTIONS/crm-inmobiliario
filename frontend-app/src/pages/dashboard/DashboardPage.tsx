import {
  HiOutlineBuildingOffice2,
  HiOutlineUsers,
  HiOutlineRectangleStack,
  HiOutlineCurrencyEuro,
} from 'react-icons/hi2'

const stats = [
  { label: 'Inmuebles activos', value: '-', icon: HiOutlineBuildingOffice2, color: 'bg-blue-50 text-blue-600' },
  { label: 'Contactos', value: '-', icon: HiOutlineUsers, color: 'bg-green-50 text-green-600' },
  { label: 'Leads abiertos', value: '-', icon: HiOutlineRectangleStack, color: 'bg-yellow-50 text-yellow-600' },
  { label: 'Facturación mes', value: '-', icon: HiOutlineCurrencyEuro, color: 'bg-purple-50 text-purple-600' },
]

export function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="card p-5">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Placeholder sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Últimas propiedades
          </h2>
          <p className="text-sm text-gray-500">
            Las propiedades añadidas recientemente aparecerán aquí.
          </p>
        </div>
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Leads recientes
          </h2>
          <p className="text-sm text-gray-500">
            Los últimos leads recibidos aparecerán aquí.
          </p>
        </div>
      </div>
    </div>
  )
}
