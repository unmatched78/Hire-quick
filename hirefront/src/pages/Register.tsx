import { Box, Heading, VStack, Button, Select, Input, FormControl, FormLabel, FormErrorMessage } from '@chakra-ui/react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import * as Form from '@radix-ui/react-form';

const MotionBox = motion(Box);

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
    setErrors({ ...errors, [e.target.name]: '' }); // Clear error on change
  };

  const handleSubmit = async () => {
    // Basic client-side validation
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
          <FormControl isInvalid={!!errors.username}>
            <FormLabel>Username</FormLabel>
            <Input
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Username"
              bg="gray.700"
              borderColor="gray.600"
              _focus={{ borderColor: 'brand.500', boxShadow: '0 0 0 1px #7928CA' }}
            />
            <FormErrorMessage>{errors.username}</FormErrorMessage>
          </FormControl>
          <FormControl isInvalid={!!errors.email}>
            <FormLabel>Email</FormLabel>
            <Input
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Email"
              bg="gray.700"
              borderColor="gray.600"
              _focus={{ borderColor: 'brand.500', boxShadow: '0 0 0 1px #7928CA' }}
            />
            <FormErrorMessage>{errors.email}</FormErrorMessage>
          </FormControl>
          <FormControl isInvalid={!!errors.password}>
            <FormLabel>Password</FormLabel>
            <Input
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Password"
              bg="gray.700"
              borderColor="gray.600"
              _focus={{ borderColor: 'brand.500', boxShadow: '0 0 0 1px #7928CA' }}
            />
            <FormErrorMessage>{errors.password}</FormErrorMessage>
          </FormControl>
          <FormControl isInvalid={!!errors.user_type}>
            <FormLabel>User Type</FormLabel>
            <Select
              name="user_type"
              value={formData.user_type}
              onChange={handleChange}
              placeholder="Select Type"
              bg="gray.700"
              borderColor="gray.600"
              _focus={{ borderColor: 'brand.500', boxShadow: '0 0 0 1px #7928CA' }}
            >
              <option value="job_seeker">Job Seeker</option>
              <option value="company_rep">Company Representative</option>
            </Select>
            <FormErrorMessage>{errors.user_type}</FormErrorMessage>
          </FormControl>
          <Button
            colorScheme="brand"
            mt={4}
            onClick={handleSubmit}
            _hover={{ bg: 'brand.600' }}
          >
            Register
          </Button>
        </Form.Root>
      </VStack>
    </MotionBox>
  );
};

export default Register;