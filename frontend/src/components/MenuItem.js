import React from 'react';
import { PlusIcon, MinusIcon } from '@heroicons/react/24/outline';
import { useCart } from '../context/CartContext';
import './MenuItem.css';

/**
 * MenuItem component for displaying individual menu items
 * @param {Object} item - Menu item object with id, name, price, image_id
 */
const MenuItem = ({ item }) => {
  const { addItem, removeItem, cart } = useCart();
  
  const cartItem = cart.items.find(cartItem => cartItem.id === item.id);
  const quantity = cartItem ? cartItem.quantity : 0;

  const handleAdd = () => {
    addItem(item);
  };

  const handleRemove = () => {
    if (quantity > 0) {
      removeItem(item);
    }
  };

  // Generate placeholder image URL using a service like picsum
  const imageUrl = item.image_id 
    ? `https://picsum.photos/seed/${item.image_id}/300/200`
    : `https://picsum.photos/seed/food-${item.id}/300/200`;

  return (
    <div className="menu-item">
      <div className="menu-item-image">
        <img 
          src={imageUrl} 
          alt={item.name}
          onError={(e) => {
            e.target.src = `https://picsum.photos/seed/food-${item.id}/300/200`;
          }}
        />
      </div>
      
      <div className="menu-item-content">
        <h3 className="menu-item-name">{item.name}</h3>
        <p className="menu-item-price">${item.price.toFixed(2)}</p>
        {item.description && (
          <p className="menu-item-description">{item.description}</p>
        )}
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
