import { Box, Heading, Text, Button, VStack, SimpleGrid, Input, Icon } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { BriefcaseIcon, BuildingOffice2Icon, StarIcon } from '@heroicons/react/24/solid';
import { Link } from 'react-router-dom';

const MotionBox = motion(Box);
const MotionButton = motion(Button);

const Home = () => {
  return (
    <Box position="relative" minH="100vh" className="glow">
      {/* Hero Section */}
      <VStack py={20} textAlign="center" spacing={6}>
        <MotionBox
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Heading size="3xl" bgGradient="linear(to-r, brand.500, brand.600)" bgClip="text">
            HireEasy: Your Ultimate Hiring Solution
          </Heading>
          <Text fontSize="xl" mt={4} maxW="2xl">
            Discover top talent or land your dream job with our all-in-one platform for job seekers and companies.
          </Text>
          <Input
            placeholder="Search for jobs..."
            size="lg"
            maxW="md"
            mx="auto"
            mt={6}
            className="shadow-lg"
          />
          <MotionButton
            colorScheme="brand"
            size="lg"
            whileHover={{ scale: 1.1 }}
            as={Link}
            to="/jobs"
            mt={4}
          >
            Explore Jobs
          </MotionButton>
        </MotionBox>
      </VStack>
      {/* Features Section */}
      <SimpleGrid columns={[1, 2, 3]} spacing={10} p={8}>
        <MotionBox
          p={5}
          shadow="lg"
          borderWidth="1px"
          rounded="md"
          bg="gray.800"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Icon as={BriefcaseIcon} w={8} h={8} color="brand.500" />
          <Heading size="md" mt={4}>Find Your Dream Job</Heading>
          <Text>Explore thousands of opportunities tailored to your skills.</Text>
        </MotionBox>
        <MotionBox
          p={5}
          shadow="lg"
          borderWidth="1px"
          rounded="md"
          bg="gray.800"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Icon as={BuildingOffice2Icon} w={8} h={8} color="brand.500" />
          <Heading size="md" mt={4}>Hire Top Talent</Heading>
          <Text>Post jobs and find the perfect candidates with ease.</Text>
        </MotionBox>
        <MotionBox
          p={5}
          shadow="lg"
          borderWidth="1px"
          rounded="md"
          bg="gray.800"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Icon as={StarIcon} w={8} h={8} color="brand.500" />
          <Heading size="md" mt={4}>Trusted Reviews</Heading>
          <Text>Read authentic company reviews from real employees.</Text>
        </MotionBox>
      </SimpleGrid>
      {/* Testimonial Section */}
      <Box py={10} textAlign="center" bg="gray.700">
        <Heading size="xl" mb={6}>What Our Users Say</Heading>
        <SimpleGrid columns={[1, 2]} spacing={8} px={8}>
          <MotionBox
            p={5}
            shadow="lg"
            rounded="md"
            bg="gray.800"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Text>"HireEasy helped me land my dream job in just two weeks!"</Text>
            <Text mt={4} fontWeight="bold">— Jane Doe</Text>
          </MotionBox>
          <MotionBox
            p={5}
            shadow="lg"
            rounded="md"
            bg="gray.800"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <Text>"The easiest way to find top talent for our company."</Text>
            <Text mt={4} fontWeight="bold">— Acme Corp</Text>
          </MotionBox>
        </SimpleGrid>
      </Box>
    </Box>
  );
};

export default Home;