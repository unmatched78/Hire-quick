import axios from 'axios';

export const getJobs = async () => {
  const response = await axios.get('http://your-backend-url/api/jobs/');
  return response.data;
};