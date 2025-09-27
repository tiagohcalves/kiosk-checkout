import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Menu endpoints
export const getMenu = () => api.get('/menu');
export const getCategories = () => api.get('/categories');
export const getItems = (categoryId = null) => {
  const params = categoryId ? { category_id: categoryId } : {};
  return api.get('/items', { params });
};

// Order endpoints
export const createOrder = (orderData) => api.post('/orders', orderData);
export const getOrder = (orderId) => api.get(`/orders/${orderId}`);

export default api;
