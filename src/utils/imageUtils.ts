
/**
 * Utility functions for handling image URLs
 */

/**
 * Ensures a valid image URL is returned, handling various edge cases
 * 
 * @param url The original image URL
 * @param fallback Optional fallback URL (defaults to '/placeholder.svg')
 * @returns A valid image URL
 */
export const getValidImageUrl = (url: string, fallback: string = '/placeholder.svg'): string => {
  // Handle empty or undefined URLs
  if (!url) return fallback;
  
  // Handle base64 images (return as-is)
  if (url.startsWith('data:')) {
    return url;
  }
  
  // Handle server paths correctly (return as-is)
  if (url.startsWith('/static/')) {
    return url;
  }
  
  // Fix protocol issues (like https:;//)
  if (url.includes(';//')) {
    return url.replace(';//', '://');
  }
  
  // If it's an absolute URL, return as is
  if (url.startsWith('http')) {
    return url;
  }
  
  // Prepend / if it's a relative path and doesn't already start with /
  if (!url.startsWith('/')) {
    return `/${url}`;
  }
  
  // Return original URL if none of the conditions are met
  return url;
};

/**
 * Handles image loading errors by setting a placeholder
 * 
 * @param event The error event
 * @param imageUrl The original image URL that failed
 * @param fallback Optional fallback URL (defaults to '/placeholder.svg')
 */
export const handleImageError = (
  event: React.SyntheticEvent<HTMLImageElement, Event>,
  imageUrl: string,
  fallback: string = '/placeholder.svg'
): void => {
  console.error(`Failed to load image: ${imageUrl}`);
  (event.target as HTMLImageElement).src = fallback;
};
