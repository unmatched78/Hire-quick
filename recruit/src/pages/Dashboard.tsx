import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/stores/auth';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const { t } = useTranslation();
  const { user } = useAuthStore();

  return (
    <div className="py-16 px-4">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-4xl font-bold text-center mb-12 text-gray-900"
      >
        {t('dashboard_title', { username: user?.id })}
      </motion.h1>
      <div className="max-w-5xl mx-auto">
        <Card className="card glow-on-hover">
          <CardHeader>
            <CardTitle className="text-gray-900">
              {user?.user_type === 'job_seeker' ? t('job_seeker_dashboard') : t('company_rep_dashboard')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {user?.user_type === 'job_seeker' ? (
              <div className="space-y-4">
                <p className="text-gray-600">{t('job_seeker_welcome')}</p>
                <Link to="/jobs">
                  <Button className="glow-on-hover bg-gradient-to-r from-blue-500 to-purple-500 text-white">
                    {t('browse_jobs')}
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-gray-600">{t('company_rep_welcome')}</p>
                <Button className="glow-on-hover bg-gradient-to-r from-blue-500 to-purple-500 text-white">
                  {t('post_job')}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;