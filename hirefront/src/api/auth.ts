import axios from 'axios';

export const login = async (username: string, password: string) => {
  const response = await axios.post('http://localhost:8000/api/token/', { username, password });
  localStorage.setItem('token', response.data.token);
  return response.data;
};