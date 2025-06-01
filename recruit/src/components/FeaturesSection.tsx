import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { Briefcase, Search, CheckCircle, Video, FileText } from 'lucide-react';

const features = [
  { title: 'Job Listings', description: 'Easily create and manage job postings.', icon: Briefcase },
  { title: 'Screening', description: 'Automate candidate screening with smart filters.', icon: Search },
  { title: 'Shortlisting', description: 'Quickly shortlist top candidates.', icon: CheckCircle },
  { title: 'Interviewing', description: 'Schedule and conduct interviews seamlessly.', icon: Video },
  { title: 'Offer Letters', description: 'Generate professional offer letters.', icon: FileText },
];

const FeaturesSection = () => {
  return (
    <section className="py-12 px-4 bg-gray-100">
      <h2 className="text-3xl font-bold text-center mb-8">What We Do</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <Card>
              <CardHeader>
                <feature.icon className="h-8 w-8 text-blue-600" />
                <CardTitle>{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p>{feature.description}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default FeaturesSection;