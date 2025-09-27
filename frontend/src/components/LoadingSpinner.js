import React from 'react';
import './LoadingSpinner.css';

/**
 * LoadingSpinner component for showing loading states
 * @param {string} size - Size of the spinner ('small', 'medium', 'large')
 * @param {string} message - Optional loading message
 */
const LoadingSpinner = ({ size = 'medium', message }) => {
  return (
    <div className="loading-container">
      <div className={`loading-spinner loading-spinner-${size}`}>
        <div className="spinner-circle"></div>
      </div>
      {message && <p className="loading-message">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;
