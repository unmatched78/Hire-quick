import { Box, Heading, Input, Button, VStack, Select, FormControl, FormLabel } from '@chakra-ui/react';
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
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    try {
      await axios.post('http://your-backend-url/api/users/', formData);
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
    >
      <VStack spacing={4}>
        <Heading>Sign Up</Heading>
        <Form.Root>
          <FormControl asChild>
            <Form.Field name="username">
              <FormLabel>Username</FormLabel>
              <Input name="username" value={formData.username} onChange={handleChange} placeholder="Username" />
            </Form.Field>
          </FormControl>
          <FormControl asChild>
            <Form.Field name="email">
              <FormLabel>Email</FormLabel>
              <Input name="email" type="email" value={formData.email} onChange={handleChange} placeholder="Email" />
            </Form.Field>
          </FormControl>
          <FormControl asChild>
            <Form.Field name="password">
              <FormLabel>Password</FormLabel>
              <Input name="password" type="password" value={formData.password} onChange={handleChange} placeholder="Password" />
            </Form.Field>
          </FormControl>
          <FormControl asChild>
            <Form.Field name="user_type">
              <FormLabel>User Type</FormLabel>
              <Select name="user_type" value={formData.user_type} onChange={handleChange}>
                <option value="">Select Type</option>
                <option value="job_seeker">Job Seeker</option>
                <option value="company_rep">Company Representative</option>
              </Select>
            </Form.Field>
          </FormControl>
          <Button colorScheme="brand" mt={4} onClick={handleSubmit}>
            Register
          </Button>
        </Form.Root>
      </VStack>
    </MotionBox>
  );
};

export default Register;