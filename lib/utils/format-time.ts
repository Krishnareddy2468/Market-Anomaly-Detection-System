/**
 * Format time utilities for handling various time formatting scenarios
 */

/**
 * Parse a date string safely, handling multiple formats
 */
function parseDate(dateString: string | number | Date): Date {
  if (!dateString) {
    throw new Error('Invalid date: empty value')
  }

  // If already a Date object
  if (dateString instanceof Date) {
    return dateString
  }

  // Handle timestamps (numbers)
  if (typeof dateString === 'number') {
    return new Date(dateString)
  }

  // Handle ISO strings and other standard formats
  const date = new Date(dateString)

  if (isNaN(date.getTime())) {
    // Try removing 'Z' if present and retry
    const cleaned = dateString.toString().replace('Z', '')
    const retryDate = new Date(cleaned)
    if (isNaN(retryDate.getTime())) {
      throw new Error(`Invalid date format: ${dateString}`)
    }
    return retryDate
  }

  return date
}

/**
 * Format time as relative (e.g., "2 mins ago", "1 hour ago")
 */
export function formatTimeRelative(dateString: string | number | Date): string {
  try {
    const date = parseDate(dateString)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (seconds < 0) {
      return 'now'
    }

    // Seconds
    if (seconds < 60) {
      return seconds === 1 ? '1 sec ago' : `${seconds} secs ago`
    }

    // Minutes
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) {
      return minutes === 1 ? '1 min ago' : `${minutes} mins ago`
    }

    // Hours
    const hours = Math.floor(minutes / 60)
    if (hours < 24) {
      return hours === 1 ? '1 hour ago' : `${hours} hours ago`
    }

    // Days
    const days = Math.floor(hours / 24)
    if (days < 7) {
      return days === 1 ? '1 day ago' : `${days} days ago`
    }

    // Weeks
    const weeks = Math.floor(days / 7)
    if (weeks < 4) {
      return weeks === 1 ? '1 week ago' : `${weeks} weeks ago`
    }

    // Months
    const months = Math.floor(days / 30)
    if (months < 12) {
      return months === 1 ? '1 month ago' : `${months} months ago`
    }

    // Years
    const years = Math.floor(days / 365)
    return years === 1 ? '1 year ago' : `${years} years ago`
  } catch (error) {
    console.error('[v0] Error formatting relative time:', error)
    return 'N/A'
  }
}

/**
 * Format time as absolute date and time (e.g., "Jan 15, 2024 2:30:45 PM")
 */
export function formatTimeAbsolute(dateString: string | number | Date): string {
  try {
    const date = parseDate(dateString)
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    }).format(date)
  } catch (error) {
    console.error('[v0] Error formatting absolute time:', error)
    return 'N/A'
  }
}

/**
 * Format time only (e.g., "2:30:45 PM")
 */
export function formatTimeTime(dateString: string | number | Date): string {
  try {
    const date = parseDate(dateString)
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    }).format(date)
  } catch (error) {
    console.error('[v0] Error formatting time:', error)
    return 'N/A'
  }
}

/**
 * Format date only (e.g., "Jan 15, 2024")
 */
export function formatTimeDate(dateString: string | number | Date): string {
  try {
    const date = parseDate(dateString)
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(date)
  } catch (error) {
    console.error('[v0] Error formatting date:', error)
    return 'N/A'
  }
}

/**
 * Format as ISO string (e.g., "2024-01-15T14:30:45Z")
 */
export function formatTimeISO(dateString: string | number | Date): string {
  try {
    const date = parseDate(dateString)
    return date.toISOString()
  } catch (error) {
    console.error('[v0] Error formatting ISO time:', error)
    return 'N/A'
  }
}
