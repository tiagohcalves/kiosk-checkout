import { useState } from 'react';
import { PlusIcon, MinusIcon } from '@heroicons/react/24/outline';
import { useCart } from '../context/CartContext';
import { getImageFallbackUrls } from '../utils/imageUtils';
import './MenuItem.css';

/**
 * MenuItem component for displaying individual menu items
 * @param {Object} item - Menu item object with id, name, price, image_id
 */
const MenuItem = ({ item }) => {
  const { addItem, removeItem, cart } = useCart();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  const cartItem = cart.items.find(cartItem => cartItem.id === item.id);
  const quantity = cartItem ? cartItem.quantity : 0;
  
  // Get all possible image URLs for fallback handling
  const imageUrls = getImageFallbackUrls(item.image_id, item.id);

  const handleAdd = () => {
    addItem(item);
  };

  const handleRemove = () => {
    if (quantity > 0) {
      removeItem(item);
    }
  };

  const handleImageError = () => {
    // Try the next image URL in the fallback list
    if (currentImageIndex < imageUrls.length - 1) {
      setCurrentImageIndex(currentImageIndex + 1);
    }
  };

  const currentImageUrl = imageUrls[currentImageIndex];

  return (
    <div className="menu-item">
      <div className="menu-item-image">
        <img 
          src={currentImageUrl} 
          alt={item.name}
          onError={handleImageError}
          loading="lazy"
        />
      </div>
      
      <div className="menu-item-content">
        <h3 className="menu-item-name">{item.name}</h3>
        <p className="menu-item-price">${item.price.toFixed(2)}</p>
      </div>
      
      <div className="menu-item-actions">
        {quantity > 0 ? (
          <div className="quantity-controls">
            <button 
              className="quantity-btn quantity-btn-minus"
              onClick={handleRemove}
              aria-label="Remove item"
            >
              <MinusIcon className="quantity-icon" />
            </button>
            <span className="quantity-display">{quantity}</span>
            <button 
              className="quantity-btn quantity-btn-plus"
              onClick={handleAdd}
              aria-label="Add item"
            >
              <PlusIcon className="quantity-icon" />
            </button>
          </div>
        ) : (
          <button 
            className="add-to-cart-btn"
            onClick={handleAdd}
          >
            Add to Cart
          </button>
        )}
      </div>
    </div>
  );
};

export default MenuItem;
