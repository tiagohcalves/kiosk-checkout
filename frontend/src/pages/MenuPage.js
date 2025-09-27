import React, { useState, useEffect } from 'react';
import { getMenu } from '../api/api';
import MenuItem from '../components/MenuItem';
import LoadingSpinner from '../components/LoadingSpinner';
import './MenuPage.css';

/**
 * MenuPage component for displaying menu items by category
 */
const MenuPage = () => {
  const [menuData, setMenuData] = useState({ categories: [], items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);

  useEffect(() => {
    fetchMenu();
  }, []);

  const fetchMenu = async () => {
    try {
      setLoading(true);
      const response = await getMenu();
      setMenuData(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching menu:', err);
      setError('Failed to load menu. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filteredItems = selectedCategory
    ? menuData.items.filter(item => item.category_id === selectedCategory)
    : menuData.items;

  if (loading) {
    return <LoadingSpinner size="large" message="Loading menu..." />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">
          <h2>Oops! Something went wrong</h2>
          <p>{error}</p>
          <button 
            className="retry-btn"
            onClick={fetchMenu}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="menu-page">
      {/* Category Filter */}
      <div className="category-filter">
        <button
          className={`category-btn ${selectedCategory === null ? 'active' : ''}`}
          onClick={() => setSelectedCategory(null)}
        >
          All Items
        </button>
        {menuData.categories.map(category => (
          <button
            key={category.id}
            className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
            onClick={() => setSelectedCategory(category.id)}
          >
            {category.name}
          </button>
        ))}
      </div>

      {/* Menu Items Grid */}
      <div className="menu-grid">
        {filteredItems.length > 0 ? (
          filteredItems.map(item => (
            <MenuItem key={item.id} item={item} />
          ))
        ) : (
          <div className="no-items">
            <p>No items found in this category.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MenuPage;
