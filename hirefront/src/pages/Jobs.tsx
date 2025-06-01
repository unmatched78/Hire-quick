import { useQuery } from 'react-query';
import { getJobs } from '../api/jobs';
import { SimpleGrid, Box, Heading, Text } from '@chakra-ui/react';

const Jobs = () => {
  const { data, isLoading } = useQuery('jobs', getJobs);

  if (isLoading) return <Box>Loading...</Box>;

  return (
    <SimpleGrid columns={[1, 2, 3]} spacing={6} p={4}>
      {data?.map((job: any) => (
        <Box key={job.id} p={5} shadow="md" borderWidth="1px">
          <Heading size="md">{job.title}</Heading>
          <Text>{job.company.name}</Text>
          <Text>{job.location}</Text>
        </Box>
      ))}
    </SimpleGrid>
  );
};

export default Jobs;