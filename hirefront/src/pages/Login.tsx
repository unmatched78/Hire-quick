import { Box, Heading, VStack, Button, Input, FormLabel, FormErrorMessage } from '@chakra-ui/react';
import { FormControl } from '@chakra-ui/form-control'; // Correct import
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';

const MotionBox = motion(Box);

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
        <Heading>Login</Heading>
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
        <Button
          colorScheme="brand"
          mt={4}
          onClick={handleSubmit}
          _hover={{ bg: 'brand.600' }}
        >
          Login
        </Button>
      </VStack>
    </MotionBox>
  );
};

export default Login;