import { useQuery } from 'react-query';
import { SimpleGrid, Box, Heading, Text, Button } from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import { BriefcaseIcon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';
import axios from 'axios';

const MotionBox = motion(Box);

const getJobs = async () => {
  const response = await axios.get('http://your-backend-url/api/jobs/');
  return response.data;
};

const Jobs = () => {
  const { data, isLoading } = useQuery('jobs', getJobs);

  if (isLoading) return <Box>Loading...</Box>;

  return (
    <Box p={8}>
      <Heading mb={6}>Find Your Next Job</Heading>
      <SimpleGrid columns={[1, 2, 3]} spacing={6}>
        {data?.map((job: any) => (
          <MotionBox
            key={job.id}
            p={5}
            shadow="lg"
            borderWidth="1px"
            rounded="md"
            bg="gray.800"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Heading size="md">{job.title}</Heading>
            <Text mt={2}>{job.posted_by.name}</Text>
            <Text>{job.location}</Text>
            <Text>{job.job_type}</Text>
            <Button
              as={Link}
              to={`/jobs/${job.id}`}
              colorScheme="brand"
              mt={4}
              leftIcon={<BriefcaseIcon className="w-5 h-5" />}
            >
              View Details
            </Button>
          </MotionBox>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default Jobs;