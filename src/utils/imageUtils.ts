
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
  // For debugging
  console.log("Processing image URL:", url);
  
  // Handle empty or undefined URLs
  if (!url) {
    console.log("Empty URL detected, using fallback:", fallback);
    return fallback;
  }
  
  // Handle base64 images (return as-is)
  if (url.startsWith('data:')) {
    console.log("Base64 image detected");
    return url;
  }

  // Fix protocol issues (like https:;//)
  if (url.includes('://;')) {
    url = url.replace('://;', '://');
    console.log("Fixed protocol issue in URL:", url);
  }
  
  // If it's an absolute URL, return as is
  if (url.startsWith('http')) {
    console.log("Absolute URL detected, using as-is:", url);
    return url;
  }
  
  // Critical change: Handle server paths by prepending server URL
  if (url.startsWith('/static/')) {
    // Remove the leading slash so it correctly joins with the server URL
    console.log("Constructed server URL:", `${SERVER_BASE_URL}${url}`, "from path:", url);
    return `${SERVER_BASE_URL}${url}`;
  }
  
  // Prepend / if it's a relative path and doesn't already start with /
  if (!url.startsWith('/')) {
    console.log("Adding leading slash to relative path:", `/${url}`);
    return `/${url}`;
  }
  
  // For other paths starting with /, prepend server URL
  console.log("Adding server base to path:", `${SERVER_BASE_URL}${url}`);
  return `${SERVER_BASE_URL}${url}`;
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
