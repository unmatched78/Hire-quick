import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Heading, Text, Button, VStack, Icon, Spinner, Flex } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import { BriefcaseIcon } from '@heroicons/react/24/solid';
import axios from 'axios';

const MotionBox = motion(Box);
const MotionButton = motion(Button);

interface Job {
  id: number;
  title: string;
  description: string;
  location: string;
  salary_min?: number;
  salary_max?: number;
  job_type: string;
  posted_by: { name: string };
  date_posted: string;
}

const JobDetail = () => {
  const { id } = useParams<{ id: string }>(); // Get job ID from URL
  const navigate = useNavigate();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/jobs/${id}/`);
        setJob(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load job details');
        setLoading(false);
      }
    };
    fetchJob();
  }, [id]);

  const handleApply = () => {
    // Placeholder for apply logic (e.g., redirect to application form or API call)
    navigate('/apply'); // Update with actual application route
  };

  if (loading) return <Spinner size="xl" color="brand.500" />;
  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <MotionBox
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      p={8}
      maxW="3xl"
      mx="auto"
      mt={10}
      bg="gray.800"
      rounded="lg"
      shadow="lg"
      className="glow"
    >
      <VStack spacing={6} align="start">
        <Heading size="2xl" bgGradient="linear(to-r, brand.500, brand.600)" bgClip="text">
          {job?.title}
        </Heading>
        <Flex align="center">
          <Icon as={BriefcaseIcon} w={6} h={6} color="brand.500" mr={2} />
          <Text fontSize="lg" fontWeight="bold">{job?.posted_by.name}</Text>
        </Flex>
        <Text><strong>Location:</strong> {job?.location}</Text>
        <Text><strong>Job Type:</strong> {job?.job_type}</Text>
        {(job?.salary_min || job?.salary_max) && (
          <Text>
            <strong>Salary:</strong> ${job?.salary_min?.toLocaleString()} - ${job?.salary_max?.toLocaleString()}
          </Text>
        )}
        <Text><strong>Posted:</strong> {new Date(job?.date_posted || '').toLocaleDateString()}</Text>
        <Text><strong>Description:</strong> {job?.description}</Text>
        <MotionButton
          colorScheme="brand"
          size="lg"
          whileHover={{ scale: 1.1 }}
          onClick={handleApply}
        >
          Apply Now
        </MotionButton>
      </VStack>
    </MotionBox>
  );
};

export default JobDetail;