
/**
 * Utility functions for handling image URLs
 */

// Get the server base URL from environment or use default
const SERVER_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
    console.log('Returning base64 image as-is');
    return url;
  }

  // Fix protocol issues (like https:;//)
  if (url.includes('://;')) {
    url = url.replace('://;', '://');
  }
  
  // If it's an absolute URL, return as is
  if (url.startsWith('http')) {
    console.log(`Returning absolute URL: ${url}`);
    return url;
  }
  
  // Handle server paths by prepending server URL
  if (url.startsWith('/static/')) {
    const fullUrl = `${SERVER_BASE_URL}${url}`;
    console.log(`Constructed server URL: ${fullUrl} from path: ${url}`);
    return fullUrl;
  }
  
  // Prepend / if it's a relative path and doesn't already start with /
  if (!url.startsWith('/')) {
    return `/${url}`;
  }
  
  // For other paths starting with /, prepend server URL
  const fullUrl = `${SERVER_BASE_URL}${url}`;
  console.log(`Constructed server URL for path: ${fullUrl}`);
  return fullUrl;
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
  
  // Additional debugging
  console.log(`Image URL that failed: ${imageUrl}`);
  console.log(`Using fallback: ${fallback}`);
  console.log(`Server base URL: ${SERVER_BASE_URL}`);
};
