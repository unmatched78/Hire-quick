import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import * as Form from '@radix-ui/react-form';

const MotionDiv = motion.div;

const Login = () => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [errors, setErrors] = useState({ username: '', password: '' });
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: '' });
  };

  const handleSubmit = async () => {
    let newErrors = { username: '', password: '' };
    if (!formData.username) newErrors.username = 'Username is required';
    if (!formData.password) newErrors.password = 'Password is required';
    setErrors(newErrors);

    if (Object.values(newErrors).every((error) => !error)) {
      try {
        const response = await axios.post('http://localhost:8000/api/token/', formData);
        localStorage.setItem('token', response.data.token);
        navigate('/dashboard');
      } catch (error) {
        console.error('Login failed', error);
        setErrors({ ...errors, password: 'Invalid credentials' });
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
          <h2 className="text-2xl font-bold text-white">Login</h2>
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
          <button
            type="button"
            onClick={handleSubmit}
            className="mt-4 w-full rounded-md bg-brand-500 px-4 py-2 text-white hover:bg-brand-600"
          >
            Login
          </button>
        </div>
      </Form.Root>
    </MotionDiv>
  );
};

export default Login;