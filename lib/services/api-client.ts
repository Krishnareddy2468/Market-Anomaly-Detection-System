import { ApiError, ApiResponse } from '../types'

export class ApiClient {
  static async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    // Use relative URLs for client-side requests to work properly in all environments
    try {
      const response = await fetch(endpoint, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const errorData = (await response.json()) as ApiError
        const error = new Error(errorData.message || 'API request failed') as any
        error.code = errorData.error_code
        error.status = response.status
        throw error
      }

      const data = await response.json()
      return data as T
    } catch (error) {
      console.error(`[API Error] ${endpoint}:`, error)
      throw error
    }
  }

  static get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'GET',
    })
  }

  static post<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  static put<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  static delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'DELETE',
    })
  }
}
