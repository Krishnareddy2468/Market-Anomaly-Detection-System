export * from './alert'
export * from './metrics'

export interface ApiError {
  error_code: string
  message: string
}

export interface ApiResponse<T> {
  data?: T
  error?: ApiError
  status: 'SUCCESS' | 'ERROR'
}
