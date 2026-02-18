import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { HiOutlinePlus, HiOutlineMagnifyingGlass } from 'react-icons/hi2'
import { propertyApi } from '@/api/properties'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import { formatPrice } from '@/utils/formatters'
import type { PropertyListItem } from '@/types/property'
import { PROPERTY_TYPE_LABELS, OPERATION_LABELS, STATUS_LABELS } from '@/types/property'
import type { PropertyType, OperationType, PropertyStatus } from '@/types/property'

const statusVariant: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'default'> = {
  available: 'success',
  reserved: 'warning',
  sold: 'info',
  rented: 'info',
  withdrawn: 'danger',
}

export function PropertyListPage() {
  const [properties, setProperties] = useState<PropertyListItem[]>([])
  const [count, setCount] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [offset, setOffset] = useState(0)
  const limit = 20

  const fetchProperties = async () => {
    setIsLoading(true)
    try {
      const { data } = await propertyApi.list({
        search: search || undefined,
        limit,
        offset,
      })
      setProperties(data.properties)
      setCount(data.count)
    } catch (err) {
      console.error('Failed to fetch properties', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchProperties()
  }, [offset])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setOffset(0)
    fetchProperties()
  }

  const totalPages = Math.ceil(count / limit)
  const currentPage = Math.floor(offset / limit) + 1

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inmuebles</h1>
          <p className="text-sm text-gray-500">{count} propiedades</p>
        </div>
        <Link to="/app/properties/new">
          <Button>
            <HiOutlinePlus className="w-4 h-4" />
            Nueva propiedad
          </Button>
        </Link>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="mb-4">
        <div className="relative max-w-md">
          <HiOutlineMagnifyingGlass className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por referencia, título, ciudad..."
            className="input-field pl-10"
          />
        </div>
      </form>

      {/* Table */}
      {isLoading ? (
        <div className="py-20">
          <Spinner size="lg" />
        </div>
      ) : properties.length === 0 ? (
        <div className="card p-12 text-center">
          <HiOutlineMagnifyingGlass className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">
            No se encontraron propiedades
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            Añade tu primera propiedad para empezar.
          </p>
          <Link to="/app/properties/new">
            <Button>
              <HiOutlinePlus className="w-4 h-4" />
              Nueva propiedad
            </Button>
          </Link>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b text-left">
                  <th className="px-4 py-3 font-medium text-gray-600">Ref.</th>
                  <th className="px-4 py-3 font-medium text-gray-600">Propiedad</th>
                  <th className="px-4 py-3 font-medium text-gray-600">Tipo</th>
                  <th className="px-4 py-3 font-medium text-gray-600">Operación</th>
                  <th className="px-4 py-3 font-medium text-gray-600">Precio</th>
                  <th className="px-4 py-3 font-medium text-gray-600">Hab.</th>
                  <th className="px-4 py-3 font-medium text-gray-600">m²</th>
                  <th className="px-4 py-3 font-medium text-gray-600">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {properties.map((prop) => (
                  <tr
                    key={prop.id}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <Link
                        to={`/app/properties/${prop.id}`}
                        className="font-medium text-primary-600 hover:text-primary-700"
                      >
                        {prop.reference}
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        {prop.primary_image ? (
                          <img
                            src={prop.primary_image.thumbnail || prop.primary_image.image}
                            alt={prop.title}
                            className="w-10 h-10 rounded object-cover"
                          />
                        ) : (
                          <div className="w-10 h-10 bg-gray-100 rounded flex items-center justify-center">
                            <HiOutlineMagnifyingGlass className="w-4 h-4 text-gray-400" />
                          </div>
                        )}
                        <div>
                          <p className="font-medium text-gray-900 truncate max-w-[200px]">
                            {prop.title}
                          </p>
                          <p className="text-xs text-gray-500 truncate max-w-[200px]">
                            {prop.address_display}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {PROPERTY_TYPE_LABELS[prop.property_type as PropertyType] || prop.property_type}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {OPERATION_LABELS[prop.operation as OperationType] || prop.operation}
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {prop.sale_price
                        ? formatPrice(prop.sale_price, prop.currency)
                        : prop.rent_price
                          ? `${formatPrice(prop.rent_price, prop.currency)}/mes`
                          : '-'}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{prop.bedrooms}</td>
                    <td className="px-4 py-3 text-gray-600">
                      {prop.built_area ? `${prop.built_area}` : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={statusVariant[prop.status] || 'default'}>
                        {STATUS_LABELS[prop.status as PropertyStatus] || prop.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50">
              <p className="text-sm text-gray-600">
                Mostrando {offset + 1}-{Math.min(offset + limit, count)} de {count}
              </p>
              <div className="flex gap-1">
                <button
                  onClick={() => setOffset(Math.max(0, offset - limit))}
                  disabled={offset === 0}
                  className="px-3 py-1 text-sm rounded border hover:bg-white disabled:opacity-50"
                >
                  Anterior
                </button>
                <span className="px-3 py-1 text-sm text-gray-600">
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setOffset(offset + limit)}
                  disabled={offset + limit >= count}
                  className="px-3 py-1 text-sm rounded border hover:bg-white disabled:opacity-50"
                >
                  Siguiente
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
