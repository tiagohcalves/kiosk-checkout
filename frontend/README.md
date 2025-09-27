# Restaurant Checkout Kiosk - Frontend

A modern React-based frontend for a restaurant checkout kiosk system that integrates with a Django backend API. This application allows customers to browse menu items, manage their cart, and complete checkout with payment processing.

## Features

- **Menu Browsing**: View restaurant menu items with images, descriptions, and prices
- **Cart Management**: Add items to cart, adjust quantities, and remove items
- **Checkout Process**: Complete order with payment information
- **Responsive Design**: Modern UI that works on various screen sizes
- **Real-time Updates**: Cart badge shows current item count

## Technology Stack

- **React 18** - Frontend framework
- **React Router DOM** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API requests
- **Heroicons** - Icon library
- **Context API** - State management for cart

## Prerequisites

- Node.js (version 14 or higher)
- npm or yarn package manager
- Django backend running on `http://localhost:8000`

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Application

1. Ensure the Django backend is running on `http://localhost:8000`

2. Start the development server:
   ```bash
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App (irreversible)

## Project Structure

```
src/
├── api/
│   └── api.js              # API service layer
├── components/
│   ├── Header.js           # Navigation header with cart badge
│   ├── MenuItem.js         # Individual menu item component
│   ├── CartItem.js         # Cart item with quantity controls
│   └── PaymentForm.js      # Payment form with validation
├── context/
│   └── CartContext.js      # Cart state management
├── pages/
│   ├── MenuPage.js         # Main menu display page
│   ├── CartPage.js         # Shopping cart page
│   └── CheckoutPage.js     # Order summary and payment page
├── App.js                  # Main app component with routing
├── index.js               # React DOM entry point
├── App.css                # Global styles
└── index.css              # Base styles and Tailwind imports
```

## API Integration

The frontend communicates with the Django backend through the following endpoints:

- `GET /api/menu-items/` - Fetch all menu items
- `POST /api/cart/add/` - Add item to cart
- `PUT /api/cart/update/{id}/` - Update cart item quantity
- `DELETE /api/cart/remove/{id}/` - Remove item from cart
- `POST /api/checkout/` - Process payment and complete order

## Usage

1. **Browse Menu**: View available items on the main menu page
2. **Add to Cart**: Click "Add to Cart" on any menu item
3. **Manage Cart**: Navigate to cart to adjust quantities or remove items
4. **Checkout**: Proceed to checkout and enter payment information
5. **Complete Order**: Submit payment to finalize the order

## Configuration

The API base URL is configured in `src/api/api.js`. Update this if your backend is running on a different port or domain:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

## Build and Deployment

To build the application for production:

```bash
npm run build
```

This creates a `build` folder with optimized production files ready for deployment.

## Troubleshooting

### Common Issues

1. **API Connection Error**: Ensure the Django backend is running on `http://localhost:8000`
2. **CORS Issues**: Make sure CORS is properly configured in the Django backend
3. **Port Conflicts**: If port 3000 is in use, React will prompt to use a different port

### Development Tips

- Use browser developer tools to inspect API requests
- Check the browser console for any JavaScript errors
- Verify that the Django backend endpoints are accessible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational/demonstration purposes.
