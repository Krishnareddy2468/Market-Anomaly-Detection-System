import { ApiError } from '../types'

export class ApiClient {
  private static readonly API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, '') || ''

  private static buildCandidateUrls(endpoint: string): string[] {
    if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
      return [endpoint]
    }

    const urls: string[] = []

    if (this.API_BASE_URL) {
      if (endpoint.startsWith('/')) {
        urls.push(`${this.API_BASE_URL}${endpoint}`)
      } else {
        urls.push(`${this.API_BASE_URL}/${endpoint}`)
      }
      // Fallback to same-origin Next API routes if backend is unavailable.
      if (endpoint.startsWith('/api/')) {
        urls.push(endpoint)
      }
    } else if (endpoint.startsWith('/api/')) {
      // No backend URL configured; use Next API routes.
      urls.push(endpoint)
    } else {
      urls.push(endpoint.startsWith('/') ? endpoint : `/${endpoint}`)
    }

    // de-duplicate while preserving order
    return [...new Set(urls)]
  }

  static async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const candidateUrls = this.buildCandidateUrls(endpoint)
    let lastError: unknown

    for (const url of candidateUrls) {
      try {
        const response = await fetch(url, {
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
          ...options,
        })

        if (!response.ok) {
          const errorPayload = (await response.json().catch(() => null)) as
            | (ApiError & { detail?: string; error?: string })
            | null
          const message =
            errorPayload?.message ||
            errorPayload?.detail ||
            errorPayload?.error ||
            `API request failed (${response.status})`
          const error = new Error(message) as any
          error.code = errorPayload?.error_code
          error.status = response.status
          error.endpoint = endpoint
          error.url = url
          lastError = error
          continue
        }

        const data = await response.json()
        return data as T
      } catch (error) {
        lastError = error
        try {
          console.error(`[API Error] ${url}:`, error)
        } catch {
          // ignore logging failures
        }
      }
    }

    if (lastError instanceof Error) {
      throw lastError
    }
    throw new Error('Unable to reach API. Check backend and API route configuration.')
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

  static patch<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
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
