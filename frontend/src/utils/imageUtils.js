/**
 * Utility functions for handling menu item images
 */

/**
 * Generate the local image URL for a menu item
 * Tries multiple file extensions and falls back to placeholder if not found
 * @param {string} imageId - The image ID from the database
 * @param {number} itemId - The item ID for fallback placeholder
 * @returns {string} Image URL
 */
export const getMenuItemImageUrl = (imageId, itemId) => {
  if (!imageId) {
    return `/images/menu-items/placeholder-${itemId}.jpg`;
  }
  
  // Return the primary image path - the component will handle fallbacks
  return `/images/menu-items/${imageId}.jpg`;
};

/**
 * Get array of possible image paths for fallback handling
 * @param {string} imageId - The image ID from the database
 * @param {number} itemId - The item ID for fallback placeholder
 * @returns {string[]} Array of possible image URLs
 */
export const getImageFallbackUrls = (imageId, itemId) => {
  const urls = [];
  
  if (imageId) {
    // Try different extensions for the image_id
    urls.push(`/images/menu-items/${imageId}.jpg`);
    urls.push(`/images/menu-items/${imageId}.jpeg`);
    urls.push(`/images/menu-items/${imageId}.png`);
    urls.push(`/images/menu-items/${imageId}.webp`);
  }
  
  // Fallback to placeholder images
  urls.push(`/images/menu-items/placeholder-${itemId}.jpg`);
  urls.push(`https://picsum.photos/seed/food-${itemId}/300/200`);
  
  return urls;
};

/**
 * Create a placeholder image name for an item
 * @param {number} itemId - The item ID
 * @returns {string} Placeholder image filename
 */
export const getPlaceholderImageName = (itemId) => {
  return `placeholder-${itemId}.jpg`;
};
