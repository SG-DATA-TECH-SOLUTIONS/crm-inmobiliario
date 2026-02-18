export interface PropertyImage {
  id: string
  image: string
  thumbnail: string
  title: string
  alt_text: string
  is_primary: boolean
  order: number
}

export interface PropertyVideo {
  id: string
  video_url: string
  video_file: string | null
  title: string
  is_virtual_tour: boolean
  order: number
}

export interface PropertyFeatureCategory {
  id: string
  name: string
  slug: string
  order: number
}

export interface PropertyFeature {
  id: string
  name: string
  slug: string
  category: PropertyFeatureCategory
  icon: string
}

export interface PropertyListItem {
  id: string
  reference: string
  title: string
  slug: string
  property_type: string
  operation: string
  status: string
  sale_price: number | null
  rent_price: number | null
  currency: string
  built_area: number | null
  bedrooms: number
  bathrooms: number
  primary_image: PropertyImage | null
  image_count: number
  address_display: string
  is_featured: boolean
  is_active: boolean
  is_published_web: boolean
  created_at: string
}

export interface PropertyDetail extends PropertyListItem {
  usable_area: number | null
  plot_area: number | null
  terrace_area: number | null
  floors: number
  floor_number: string
  year_built: number | null
  year_renovated: number | null
  orientation: string
  furnished: string
  energy_rating: string
  energy_consumption: number | null
  co2_emissions: number | null
  description: string
  internal_notes: string
  community_fees: number | null
  ibi_tax: number | null
  zone: string
  latitude: number | null
  longitude: number | null
  images: PropertyImage[]
  videos: PropertyVideo[]
  features: PropertyFeature[]
  publish_idealista: boolean
  publish_fotocasa: boolean
  publish_habitaclia: boolean
  available_from: string | null
  sold_date: string | null
}

export interface PropertyFilterParams {
  search?: string
  property_type?: string
  operation?: string
  status?: string
  min_price?: number
  max_price?: number
  min_bedrooms?: number
  min_bathrooms?: number
  min_area?: number
  max_area?: number
  city?: string
  zone?: string
  is_featured?: boolean
  is_active?: boolean
  limit?: number
  offset?: number
}

export type PropertyType =
  | 'flat' | 'house' | 'chalet' | 'duplex' | 'penthouse'
  | 'studio' | 'villa' | 'townhouse' | 'country_house'
  | 'building' | 'land' | 'garage' | 'storage'
  | 'office' | 'commercial' | 'warehouse'

export type OperationType = 'sale' | 'rent' | 'sale_rent' | 'transfer'

export type PropertyStatus = 'available' | 'reserved' | 'sold' | 'rented' | 'withdrawn'

export const PROPERTY_TYPE_LABELS: Record<PropertyType, string> = {
  flat: 'Piso',
  house: 'Casa',
  chalet: 'Chalet',
  duplex: 'Dúplex',
  penthouse: 'Ático',
  studio: 'Estudio',
  villa: 'Villa',
  townhouse: 'Adosado',
  country_house: 'Casa Rural',
  building: 'Edificio',
  land: 'Terreno',
  garage: 'Garaje',
  storage: 'Trastero',
  office: 'Oficina',
  commercial: 'Local Comercial',
  warehouse: 'Nave Industrial',
}

export const OPERATION_LABELS: Record<OperationType, string> = {
  sale: 'Venta',
  rent: 'Alquiler',
  sale_rent: 'Venta y Alquiler',
  transfer: 'Traspaso',
}

export const STATUS_LABELS: Record<PropertyStatus, string> = {
  available: 'Disponible',
  reserved: 'Reservado',
  sold: 'Vendido',
  rented: 'Alquilado',
  withdrawn: 'Retirado',
}
