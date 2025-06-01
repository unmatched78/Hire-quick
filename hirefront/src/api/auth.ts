import axios from 'axios';

export const login = async (username: string, password: string) => {
  const response = await axios.post('http://your-backend-url/api/token/', { username, password });
  localStorage.setItem('token', response.data.token);
  return response.data;
};