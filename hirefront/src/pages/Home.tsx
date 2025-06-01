import { Box, Heading, Text, Button, VStack } from '@chakra-ui/react';

const Home = () => {
  return (
    <Box py={20} textAlign="center">
      <VStack spacing={6}>
        <Heading size="2xl">Welcome to Your Hiring Platform</Heading>
        <Text fontSize="xl">Connecting job seekers with top companies worldwide.</Text>
        <Button colorScheme="brand" size="lg">Get Started</Button>
      </VStack>
    </Box>
  );
};

export default Home;