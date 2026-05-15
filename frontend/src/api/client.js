import axios from 'axios';

const apiClient = axios.create({
  // Use the IP address to avoid IPv6 resolution issues on Mac
  baseURL: 'http://127.0.0.1:8000/api', 
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // This will help us see exactly what the backend says if it fails again
    console.error("API Error Detail:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;