import axios from 'axios';

export const getJobs = async () => {
  const response = await axios.get('http://localhost:8000/api/jobs/');
  return response.data;
};