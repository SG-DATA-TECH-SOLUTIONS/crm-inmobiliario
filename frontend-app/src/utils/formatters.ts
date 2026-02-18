export const formatPrice = (
  amount: number | null | undefined,
  currency: string = 'EUR'
): string => {
  if (amount == null) return '-'
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export const formatArea = (area: number | null | undefined): string => {
  if (area == null) return '-'
  return `${new Intl.NumberFormat('es-ES').format(area)} m²`
}

export const formatDate = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '-'
  return new Intl.DateTimeFormat('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(new Date(dateStr))
}

export const formatDateTime = (dateStr: string | null | undefined): string => {
  if (!dateStr) return '-'
  return new Intl.DateTimeFormat('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(dateStr))
}
