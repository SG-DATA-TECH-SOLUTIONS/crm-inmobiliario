import client from './client'
import type { PropertyDetail, PropertyFilterParams, PropertyListItem, PropertyImage, PropertyFeature, PropertyFeatureCategory } from '@/types/property'

interface PropertyListResponse {
  count: number
  properties: PropertyListItem[]
}

export const propertyApi = {
  list: (params?: PropertyFilterParams) =>
    client.get<PropertyListResponse>('/properties/', { params }),

  detail: (id: string) =>
    client.get<PropertyDetail>(`/properties/${id}/`),

  create: (data: Record<string, unknown>) =>
    client.post<PropertyDetail>('/properties/', data),

  update: (id: string, data: Record<string, unknown>) =>
    client.put<PropertyDetail>(`/properties/${id}/`, data),

  delete: (id: string) =>
    client.delete(`/properties/${id}/`),

  // Images
  getImages: (id: string) =>
    client.get<PropertyImage[]>(`/properties/${id}/images/`),

  uploadImage: (id: string, formData: FormData) =>
    client.post<PropertyImage>(`/properties/${id}/images/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  updateImage: (propertyId: string, imageId: string, data: Record<string, unknown>) =>
    client.put<PropertyImage>(`/properties/${propertyId}/images/${imageId}/`, data),

  deleteImage: (propertyId: string, imageId: string) =>
    client.delete(`/properties/${propertyId}/images/${imageId}/`),

  // Videos
  getVideos: (id: string) =>
    client.get(`/properties/${id}/videos/`),

  addVideo: (id: string, data: FormData) =>
    client.post(`/properties/${id}/videos/`, data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  // Documents
  getDocuments: (id: string) =>
    client.get(`/properties/${id}/documents/`),

  uploadDocument: (id: string, formData: FormData) =>
    client.post(`/properties/${id}/documents/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  // Comments
  getComments: (id: string) =>
    client.get(`/properties/${id}/comment/`),

  addComment: (id: string, comment: string) =>
    client.post(`/properties/${id}/comment/`, { comment }),

  // Features
  getFeatures: () =>
    client.get<PropertyFeature[]>('/properties/features/'),

  getFeatureCategories: () =>
    client.get<PropertyFeatureCategory[]>('/properties/features/categories/'),
}
