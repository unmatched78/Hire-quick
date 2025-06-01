import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import * as Form from '@radix-ui/react-form';

const MotionDiv = motion.div;

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    user_type: '',
  });
  const [errors, setErrors] = useState({ username: '', email: '', password: '', user_type: '' });
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: '' });
  };

  const handleSubmit = async () => {
    let newErrors = { username: '', email: '', password: '', user_type: '' };
    if (!formData.username) newErrors.username = 'Username is required';
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    if (!formData.user_type) newErrors.user_type = 'User type is required';
    setErrors(newErrors);

    if (Object.values(newErrors).every((error) => !error)) {
      try {
        await axios.post('http://localhost:8000/api/users/', formData);
        navigate('/login');
      } catch (error) {
        console.error('Registration failed', error);
        setErrors({ ...errors, email: 'Registration failed. Email may already exist.' });
      }
    }
  };

  return (
    <MotionDiv
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mx-auto mt-10 max-w-md rounded-lg bg-gray-800 p-8 shadow-lg glow"
    >
      <Form.Root>
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-white">Sign Up</h2>
          <Form.Field name="username" className="space-y-1">
            <Form.Label className="text-white">Username</Form.Label>
            <Form.Control asChild>
              <input
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Username"
                className="w-full rounded-md border border-gray-600 bg-gray-700 p-2 text-white focus:border-brand-500 focus:ring focus:ring-brand-500 focus:ring-opacity-50"
              />
            </Form.Control>
            {errors.username && <Form.Message className="text-red-500">{errors.username}</Form.Message>}
          </Form.Field>
          <Form.Field name="email" className="space-y-1">
            <Form.Label className="text-white">Email</Form.Label>
            <Form.Control asChild>
              <input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Email"
                className="w-full rounded-md border border-gray-600 bg-gray-700 p-2 text-white focus:border-brand-500 focus:ring focus:ring-brand-500 focus:ring-opacity-50"
              />
            </Form.Control>
            {errors.email && <Form.Message className="text-red-500">{errors.email}</Form.Message>}
          </Form.Field>
          <Form.Field name="password" className="space-y-1">
            <Form.Label className="text-white">Password</Form.Label>
            <Form.Control asChild>
              <input
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Password"
                className="w-full rounded-md border border-gray-600 bg-gray-700 p-2 text-white focus:border-brand-500 focus:ring focus:ring-brand-500 focus:ring-opacity-50"
              />
            </Form.Control>
            {errors.password && <Form.Message className="text-red-500">{errors.password}</Form.Message>}
          </Form.Field>
          <Form.Field name="user_type" className="space-y-1">
            <Form.Label className="text-white">User Type</Form.Label>
            <Form.Control asChild>
              <select
                name="user_type"
                value={formData.user_type}
                onChange={handleChange}
                className="w-full rounded-md border border-gray-600 bg-gray-700 p-2 text-white focus:border-brand-500 focus:ring focus:ring-brand-500 focus:ring-opacity-50"
              >
                <option value="" disabled>
                  Select Type
                </option>
                <option value="job_seeker">Job Seeker</option>
                <option value="company_rep">Company Representative</option>
              </select>
            </Form.Control>
            {errors.user_type && <Form.Message className="text-red-500">{errors.user_type}</Form.Message>}
          </Form.Field>
          <button
            type="button"
            onClick={handleSubmit}
            className="mt-4 w-full rounded-md bg-brand-500 px-4 py-2 text-white hover:bg-brand-600"
          >
            Register
          </button>
        </div>
      </Form.Root>
    </MotionDiv>
  );
};

export default Register;