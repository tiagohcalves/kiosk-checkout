import React from 'react';
import { PlusIcon, MinusIcon, TrashIcon } from '@heroicons/react/24/outline';
import { useCart } from '../context/CartContext';
import './CartItem.css';

/**
 * CartItem component for displaying cart items
 * @param {Object} item - Cart item object with id, name, price, quantity
 */
const CartItem = ({ item }) => {
  const { addItem, removeItem } = useCart();

  const handleAdd = () => {
    addItem(item);
  };

  const handleRemove = () => {
    removeItem(item);
  };

  const itemTotal = item.price * item.quantity;

  // Generate placeholder image URL
  const imageUrl = item.image_id 
    ? `https://picsum.photos/seed/${item.image_id}/80/80`
    : `https://picsum.photos/seed/food-${item.id}/80/80`;

  return (
    <div className="cart-item">
      <div className="cart-item-image">
        <img 
          src={imageUrl} 
          alt={item.name}
          onError={(e) => {
            e.target.src = `https://picsum.photos/seed/food-${item.id}/80/80`;
          }}
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
