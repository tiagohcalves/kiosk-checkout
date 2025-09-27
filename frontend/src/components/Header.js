import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingCartIcon } from '@heroicons/react/24/outline';
import { useCart } from '../context/CartContext';
import './Header.css';

/**
 * Header component with navigation and cart indicator
 */
const Header = () => {
  const { getCartItemCount, cart } = useCart();
  const itemCount = getCartItemCount();

  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo">
          <h1>🍽️ Mashgin Kiosk</h1>
        </Link>
        
        <nav className="nav">
          <Link to="/" className="nav-link">
            Menu
          </Link>
          
          <Link to="/cart" className="cart-link">
            <div className="cart-icon-wrapper">
              <ShoppingCartIcon className="cart-icon" />
              {itemCount > 0 && (
                <span className="cart-badge">{itemCount}</span>
              )}
            </div>
            <span className="cart-total">${cart.total.toFixed(2)}</span>
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
