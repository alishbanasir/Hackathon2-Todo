/**
 * Utility functions for the Todo application.
 */

/**
 * Combines class names conditionally.
 * Filters out falsy values and joins remaining strings with spaces.
 *
 * @param classes - Array of class names or conditional expressions
 * @returns Combined class name string
 *
 * @example
 * cn('base-class', isActive && 'active', 'another-class')
 * // Returns: "base-class active another-class" (if isActive is true)
 */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}

/**
 * Formats a date string to a human-readable format.
 *
 * @param dateString - ISO 8601 date string
 * @returns Formatted date string (e.g., "Jan 7, 2026")
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

/**
 * Truncates a string to a maximum length, adding ellipsis if needed.
 *
 * @param text - Text to truncate
 * @param maxLength - Maximum length before truncation
 * @returns Truncated text with ellipsis if needed
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.slice(0, maxLength - 3) + "...";
}
