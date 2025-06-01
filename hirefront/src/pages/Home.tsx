import { Box, Heading, Text, Button, VStack, SimpleGrid, Icon } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { BriefcaseIcon, BuildingOffice2Icon } from '@heroicons/react/24/solid';

const MotionBox = motion(Box);
const MotionButton = motion(Button);

const Home = () => {
  return (
    <Box position="relative" minH="100vh">
      {/* Glowing Background */}
      <Box className="glow" />
      {/* Hero Section */}
      <VStack py={20} textAlign="center" spacing={6}>
        <MotionBox
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Heading size="2xl" bgGradient="linear(to-r, brand.500, brand.600)" bgClip="text">
            HireEasy: Your All-in-One Hiring Platform
          </Heading>
          <Text fontSize="xl" mt={4}>
            Connect job seekers with top companies effortlessly.
          </Text>
        </MotionBox>
        <MotionButton
          colorScheme="brand"
          size="lg"
          whileHover={{ scale: 1.1 }}
          as={Link}
          to="/register"
        >
          Get Started
        </MotionButton>
      </VStack>
      {/* Features Section */}
      <SimpleGrid columns={[1, 2, 3]} spacing={10} p={8}>
        <MotionBox
          p={5}
          shadow="lg"
          borderWidth="1px"
          rounded="md"
          bg="gray.800"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <Icon as={BriefcaseIcon} w={8} h={8} color="brand.500" />
          <Heading size="md" mt={4}>Find Jobs</Heading>
          <Text>Explore thousands of opportunities tailored to your skills.</Text>
        </MotionBox>
        <MotionBox
          p={5}
          shadow="lg"
          borderWidth="1px"
          rounded="md"
          bg="gray.800"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <Icon as={BuildingOffice2Icon} w={8} h={8} color="brand.500" />
          <Heading size="md" mt={4}>Hire Talent</Heading>
          <Text>Post jobs and find the perfect candidates with ease.</Text>
        </MotionBox>
      </SimpleGrid>
    </Box>
  );
};

export default Home;