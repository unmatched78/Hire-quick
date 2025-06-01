import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
import { toast } from 'sonner';

interface Job {
  id: number;
  title: string;
  company: { name: string };
  location: string;
  job_type: string;
  description: string;
}

const fetchJobs = async (): Promise<Job[]> => {
  const response = await apiClient.get('/jobs/');
  return response.data;
};

const JobsPage = () => {
  const { t } = useTranslation();
  const { data: jobs, isLoading, error } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
  });

  if (error) {
    toast.error(t('jobs_fetch_error'));
  }

  return (
    <div className="py-16 px-4">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-4xl font-bold text-center mb-12 text-gray-900"
      >
        {t('jobs_title')}
      </motion.h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
        {isLoading ? (
          <p className="text-gray-600 text-center col-span-full">{t('loading_jobs')}</p>
        ) : error ? (
          <p className="text-red-500 text-center col-span-full">{t('jobs_fetch_error')}</p>
        ) : (
          jobs?.map((job, index) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="card flex flex-col glow-on-hover">
                <CardHeader>
                  <CardTitle className="text-gray-900">{job.title}</CardTitle>
                </CardHeader>
                <CardContent className="flex-grow">
                  <p className="text-gray-600 mb-2">{job.company.name} • {job.location} • {job.job_type}</p>
                  <p className="text-gray-600 line-clamp-3">{job.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default JobsPage;