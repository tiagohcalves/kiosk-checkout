import { useState } from 'react';
import { PlusIcon, MinusIcon, TrashIcon } from '@heroicons/react/24/outline';
import { useCart } from '../context/CartContext';
import { getImageFallbackUrls } from '../utils/imageUtils';
import './CartItem.css';

/**
 * CartItem component for displaying cart items
 * @param {Object} item - Cart item object with id, name, price, quantity
 */
const CartItem = ({ item }) => {
  const { addItem, removeItem } = useCart();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const handleAdd = () => {
    addItem(item);
  };

  const handleRemove = () => {
    removeItem(item);
  };

  const itemTotal = item.price * item.quantity;

  // Get all possible image URLs for fallback handling
  const imageUrls = getImageFallbackUrls(item.image_id, item.id);

  const handleImageError = () => {
  // Try the next image URL in the fallback list
  if (currentImageIndex < imageUrls.length - 1) {
      setCurrentImageIndex(currentImageIndex + 1);
    }
  };

  const currentImageUrl = imageUrls[currentImageIndex];

  return (
    <div className="cart-item">
      <div className="cart-item-image">
        <img 
          src={currentImageUrl} 
          alt={item.name}
          onError={handleImageError}
        />
      </div>
      
      <div className="cart-item-content">
        <h4 className="cart-item-name">{item.name}</h4>
        <p className="cart-item-unit-price">${item.price.toFixed(2)} each</p>
        <p className="cart-item-total">${itemTotal.toFixed(2)}</p>
      </div>
      
      <div className="cart-item-controls">
        <div className="quantity-controls">
          <button 
            className="quantity-btn quantity-btn-minus"
            onClick={handleRemove}
            aria-label="Remove one item"
          >
            {item.quantity === 1 ? (
              <TrashIcon className="quantity-icon" />
            ) : (
              <MinusIcon className="quantity-icon" />
            )}
          </button>
          <span className="quantity-display">{item.quantity}</span>
          <button 
            className="quantity-btn quantity-btn-plus"
            onClick={handleAdd}
            aria-label="Add one item"
          >
            <PlusIcon className="quantity-icon" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default CartItem;
