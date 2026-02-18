export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  errors: Record<string, string[]>
  detail?: string
}

export interface Tag {
  id: string
  name: string
  slug: string
}

export interface Team {
  id: string
  name: string
  description: string
}

export interface Address {
  id: string
  address_line: string
  street: string
  city: string
  state: string
  postcode: string
  country: string
}
