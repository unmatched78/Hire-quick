import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { Briefcase, Search, CheckCircle, Video, FileText } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
import { toast } from 'sonner';

const features = [
  { title: 'features_listings', description: 'features_listings_desc', icon: Briefcase },
  { title: 'features_screening', description: 'features_screening_desc', icon: Search },
  { title: 'features_shortlisting', description: 'features_shortlisting_desc', icon: CheckCircle },
  { title: 'features_interviewing', description: 'features_interviewing_desc', icon: Video },
  { title: 'features_offers', description: 'features_offers_desc', icon: FileText },
];

interface Job {
  id: number;
  title: string;
  company: { name: string };
  location: string;
  job_type: string;
}

const fetchJobs = async (): Promise<Job[]> => {
  const response = await apiClient.get('/jobs/');
  return response.data;
};

const FeaturesSection = () => {
  const { t } = useTranslation();
  const { data: jobs, isLoading, error } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
  });

  if (error) {
    toast.error(t('jobs_fetch_error'));
  }

  return (
    <section className="py-16 px-4">
      <motion.h2
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-4xl font-bold text-center mb-12 text-gray-900"
      >
        {t('features_title')}
      </motion.h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <Card className="card flex flex-col glow-on-hover">
              <CardHeader>
                <feature.icon className="h-8 w-8 text-blue-500" />
                <CardTitle className="text-gray-900">{t(feature.title)}</CardTitle>
              </CardHeader>
              <CardContent className="flex-grow">
                <p className="text-gray-600">{t(feature.description)}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
      <motion.h3
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        className="text-2xl font-bold text-center mt-12 mb-6 text-gray-900"
      >
        {t('features_title')} Preview
      </motion.h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
        {isLoading ? (
          <p className="text-gray-600 text-center col-span-2">{t('loading_jobs')}</p>
        ) : error ? (
          <p className="text-red-500 text-center col-span-2">{t('jobs_fetch_error')}</p>
        ) : (
          jobs?.slice(0, 2).map((job, index) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: (index + features.length) * 0.1 }}
            >
              <Card className="card flex flex-col glow-on-hover">
                <CardHeader>
                  <CardTitle className="text-gray-900">{job.title}</CardTitle>
                </CardHeader>
                <CardContent className="flex-grow">
                  <p className="text-gray-600">{job.company.name} • {job.location} • {job.job_type}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))
        )}
      </div>
    </section>
  );
};

export default FeaturesSection;