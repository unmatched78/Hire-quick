import { Box, Flex, Button, Text } from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import { UserIcon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

const MotionButton = motion(Button);

const Navbar = () => {
  return (
    <Box bg="gray.800" px={4} py={3} shadow="lg">
      <Flex h={16} alignItems="center" justifyContent="space-between">
        <Text fontSize="2xl" fontWeight="bold" color="brand.500">
          HireEasy
        </Text>
        <Flex gap={6} alignItems="center">
          <Link to="/" className="text-white hover:text-brand-500">Home</Link>
          <Link to="/jobs" className="text-white hover:text-brand-500">Jobs</Link>
          <Link to="/companies" className="text-white hover:text-brand-500">Companies</Link>
          <Link to="/dashboard" className="text-white hover:text-brand-500">Dashboard</Link>
          <MotionButton
            colorScheme="brand"
            variant="outline"
            whileHover={{ scale: 1.05 }}
            leftIcon={<UserIcon className="w-5 h-5" />}
          >
            <Link to="/login">Login</Link>
          </MotionButton>
          <MotionButton
            colorScheme="brand"
            whileHover={{ scale: 1.05 }}
            as={Link}
            to="/register"
          >
            Sign Up
          </MotionButton>
        </Flex>
      </Box>
    </Flex>
  );
};

export default Navbar;