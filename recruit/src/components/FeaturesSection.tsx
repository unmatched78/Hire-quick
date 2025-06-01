import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { Briefcase, Search, CheckCircle, Video, FileText } from 'lucide-react';

const features = [
  { title: 'features_listings', description: 'features_listings_desc', icon: Briefcase },
  { title: 'features_screening', description: 'features_screening_desc', icon: Search },
  { title: 'features_shortlisting', description: 'features_shortlisting_desc', icon: CheckCircle },
  { title: 'features_interviewing', description: 'features_interviewing_desc', icon: Video },
  { title: 'features_offers', description: 'features_offers_desc', icon: FileText },
];

const jobPreviews = [
  { title: 'Software Engineer', company: 'Tech Corp', location: 'Kigali', type: 'Full-time' },
  { title: 'Product Manager', company: 'Innovate Ltd', location: 'Remote', type: 'Contract' },
];

const FeaturesSection = () => {
  const { t } = useTranslation();
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
        {jobPreviews.map((job, index) => (
          <motion.div
            key={job.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: (index + features.length) * 0.1 }}
          >
            <Card className="card flex flex-col glow-on-hover">
              <CardHeader>
                <CardTitle className="text-gray-900">{job.title}</CardTitle>
              </CardHeader>
              <CardContent className="flex-grow">
                <p className="text-gray-600">{job.company} • {job.location} • {job.type}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default FeaturesSection;