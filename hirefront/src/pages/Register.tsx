import { Box, Heading, VStack, Button } from '@chakra-ui/react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import * as Form from '@radix-ui/react-form';
import { Input } from 'flowbite-react';

const MotionBox = motion(Box);

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    user_type: '',
  });
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      await axios.post('http://localhost:8000/api/users/', formData);
      navigate('/login');
    } catch (error) {
      console.error('Registration failed', error);
    }
  };

  return (
    <MotionBox
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      p={8}
      maxW="md"
      mx="auto"
      mt={10}
      bg="gray.800"
      rounded="lg"
      shadow="lg"
      className="glow"
    >
      <VStack spacing={4}>
        <Heading>Sign Up</Heading>
        <Form.Root>
          <Form.Field name="username">
            <Form.Label className="text-white">Username</Form.Label>
            <Input name="username" value={formData.username} onChange={handleChange} placeholder="Username" />
          </Form.Field>
          <Form.Field name="email">
            <Form.Label className="text-white">Email</Form.Label>
            <Input name="email" type="email" value={formData.email} onChange={handleChange} placeholder="Email" />
          </Form.Field>
          <Form.Field name="password">
            <Form.Label className="text-white">Password</Form.Label>
            <Input name="password" type="password" value={formData.password} onChange={handleChange} placeholder="Password" />
          </Form.Field>
          <Form.Field name="user_type">
            <Form.Label className="text-white">User Type</Form.Label>
            <select
              name="user_type"
              value={formData.user_type}
              onChange={handleChange}
              className="block w-full mt-1 rounded-md border-gray-300 shadow-sm focus:border-brand-500 focus:ring focus:ring-brand-500 focus:ring-opacity-50"
            >
              <option value="">Select Type</option>
              <option value="job_seeker">Job Seeker</option>
              <option value="company_rep">Company Representative</option>
            </select>
          </Form.Field>
          <Button colorScheme="brand" mt={4} onClick={handleSubmit}>
            Register
          </Button>
        </Form.Root>
      </VStack>
    </MotionBox>
  );
};

export default Register;