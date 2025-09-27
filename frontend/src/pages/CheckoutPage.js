import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { createOrder } from '../api/api';
import LoadingSpinner from '../components/LoadingSpinner';
import './CheckoutPage.css';

/**
 * CheckoutPage component for payment form and order submission
 */
const CheckoutPage = () => {
  const { cart, clearCart } = useCart();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [orderId, setOrderId] = useState(null);

  const [formData, setFormData] = useState({
    cardNumber: '',
    cardHolderName: '',
    expiryMonth: '',
    expiryYear: '',
    cvv: '',
    billingAddress: {
      street: '',
      city: '',
      state: '',
      zip: ''
    }
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name.startsWith('billing.')) {
      const field = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        billingAddress: {
          ...prev.billingAddress,
          [field]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const validateForm = () => {
    const errors = [];
    
    if (!formData.cardNumber || formData.cardNumber.length < 16) {
      errors.push('Please enter a valid card number');
    }
    if (!formData.cardHolderName.trim()) {
      errors.push('Please enter the card holder name');
    }
    if (!formData.expiryMonth || formData.expiryMonth < 1 || formData.expiryMonth > 12) {
      errors.push('Please enter a valid expiry month');
    }
    if (!formData.expiryYear || formData.expiryYear < new Date().getFullYear()) {
      errors.push('Please enter a valid expiry year');
    }
    if (!formData.cvv || formData.cvv.length < 3) {
      errors.push('Please enter a valid CVV');
    }
    
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationErrors = validateForm();
    if (validationErrors.length > 0) {
      setError(validationErrors.join(', '));
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const orderData = {
        items: cart.items.map(item => ({
          item_id: item.id,
          quantity: item.quantity
        })),
        total: parseFloat((cart.total).toFixed(2)),
        payment: {
          card_number: formData.cardNumber,
          card_holder_name: formData.cardHolderName,
          expiry_month: parseInt(formData.expiryMonth),
          expiry_year: parseInt(formData.expiryYear),
          cvv: formData.cvv,
          billing_address: formData.billingAddress
        }
      };

      const response = await createOrder(orderData);
      setOrderId(response.data.id);
      clearCart();
      
      // Show success message for a moment, then redirect
      setTimeout(() => {
        navigate('/', { replace: true });
      }, 3000);
      
    } catch (err) {
      console.error('Error creating order:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to process order. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Redirect to cart if cart is empty and no successful order
  if (cart.items.length === 0 && !orderId) {
    navigate('/cart');
    return null;
  }

  // Success message
  if (orderId) {
    return (
      <div className="checkout-page">
        <div className="success-message">
          <div className="success-icon">✅</div>
          <h2>Order Placed Successfully!</h2>
          <p>Your order #{orderId} has been received and is being prepared.</p>
          <p>Thank you for your business!</p>
          <p className="redirect-message">Redirecting to menu...</p>
        </div>
      </div>
    );
  }

  const total = cart.total;

  return (
    <div className="checkout-page">
      <div className="checkout-content">
        <div className="checkout-form">
          <h1>Checkout</h1>
          
          {error && (
            <div className="error-alert">
              <p>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-section">
              <h3>Payment Information</h3>
              
              <div className="form-group">
                <label htmlFor="cardNumber">Card Number</label>
                <input
                  type="text"
                  id="cardNumber"
                  name="cardNumber"
                  value={formData.cardNumber}
                  onChange={handleInputChange}
                  placeholder="1234 5678 9012 3456"
                  maxLength="16"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="cardHolderName">Card Holder Name</label>
                <input
                  type="text"
                  id="cardHolderName"
                  name="cardHolderName"
                  value={formData.cardHolderName}
                  onChange={handleInputChange}
                  placeholder="John Doe"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="expiryMonth">Month</label>
                  <select
                    id="expiryMonth"
                    name="expiryMonth"
                    value={formData.expiryMonth}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">MM</option>
                    {Array.from({ length: 12 }, (_, i) => (
                      <option key={i + 1} value={i + 1}>
                        {String(i + 1).padStart(2, '0')}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="expiryYear">Year</label>
                  <select
                    id="expiryYear"
                    name="expiryYear"
                    value={formData.expiryYear}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">YYYY</option>
                    {Array.from({ length: 10 }, (_, i) => {
                      const year = new Date().getFullYear() + i;
                      return (
                        <option key={year} value={year}>
                          {year}
                        </option>
                      );
                    })}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="cvv">CVV</label>
                  <input
                    type="text"
                    id="cvv"
                    name="cvv"
                    value={formData.cvv}
                    onChange={handleInputChange}
                    placeholder="123"
                    maxLength="4"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Billing Address</h3>
              
              <div className="form-group">
                <label htmlFor="street">Street Address</label>
                <input
                  type="text"
                  id="street"
                  name="billing.street"
                  value={formData.billingAddress.street}
                  onChange={handleInputChange}
                  placeholder="123 Main St"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="city">City</label>
                  <input
                    type="text"
                    id="city"
                    name="billing.city"
                    value={formData.billingAddress.city}
                    onChange={handleInputChange}
                    placeholder="New York"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="state">State</label>
                  <input
                    type="text"
                    id="state"
                    name="billing.state"
                    value={formData.billingAddress.state}
                    onChange={handleInputChange}
                    placeholder="NY"
                    maxLength="2"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="zip">ZIP Code</label>
                  <input
                    type="text"
                    id="zip"
                    name="billing.zip"
                    value={formData.billingAddress.zip}
                    onChange={handleInputChange}
                    placeholder="10001"
                    maxLength="5"
                  />
                </div>
              </div>
            </div>

            <button 
              type="submit" 
              className="place-order-btn"
              disabled={loading}
            >
              {loading ? <LoadingSpinner size="small" /> : `Place Order`}
            </button>
          </form>
        </div>

        <div className="order-summary">
          <div className="summary-card">
            <h3>Order Summary</h3>
            
            <div className="order-items">
              {cart.items.map(item => (
                <div key={item.id} className="order-item">
                  <span className="item-name">{item.name}</span>
                  <span className="item-details">
                    ${item.price.toFixed(2)} × {item.quantity}
                  </span>
                  <span className="item-total">
                    ${(item.price * item.quantity).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
            <div className="order-totals">
              <div className="total-row total-final">
                <span>Total</span>
                <span>${total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
