import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button as NextUIButton } from '@nextui-org/react';
import { Dialog, DialogContent, DialogTrigger } from '@radix-ui/react-dialog';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { Briefcase, Search, CheckCircle, Video, FileText } from 'lucide-react';

const PageContainer = styled.div`
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  min-height: 100vh;
  color: white;
`;

const GlowingSection = styled.section`
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.8);
`;

const HeroSection = () => {
  const { t } = useTranslation();
  return (
    <GlowingSection className="py-16 px-4 text-center">
      <motion.h1
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-4xl md:text-6xl font-bold mb-4"
      >
        {t('hero_title')}
      </motion.h1>
      <motion.p
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="text-lg md:text-xl mb-6 max-w-2xl mx-auto"
      >
        {t('hero_subtitle')}
      </motion.p>
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="flex gap-4 justify-center"
      >
        <Button variant="default" size="lg" className="bg-blue-600 hover:bg-blue-700">
          {t('hero_cta')}
        </Button>
        <NextUIButton color="primary" size="lg">
          {t('hero_learn_more')}
        </NextUIButton>
      </motion.div>
    </GlowingSection>
  );
};

const features = [
  { title: 'features_listings', description: 'features_listings_desc', icon: Briefcase },
  { title: 'features_screening', description: 'features_screening_desc', icon: Search },
  { title: 'features_shortlisting', description: 'features_shortlisting_desc', icon: CheckCircle },
  { title: 'features_interviewing', description: 'features_interviewing_desc', icon: Video },
  { title: 'features_offers', description: 'features_offers_desc', icon: FileText },
];

const FeaturesSection = () => {
  const { t } = useTranslation();
  return (
    <GlowingSection className="py-12 px-4">
      <h2 className="text-3xl font-bold text-center mb-8">{t('features_title')}</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <Card className="bg-gray-800 border-none">
              <CardHeader>
                <feature.icon className="h-8 w-8 text-blue-400" />
                <CardTitle className="text-white">{t(feature.title)}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">{t(feature.description)}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </GlowingSection>
  );
};

const TestimonialsSection = () => {
  const { t } = useTranslation();
  return (
    <GlowingSection className="py-12 px-4">
      <h2 className="text-3xl font-bold text-center mb-8">{t('testimonials_title')}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
          <Card className="bg-gray-800 border-none">
            <CardContent className="pt-6">
              <p className="text-gray-300 mb-4">{t('testimonial_1')}</p>
              <p className="font-bold text-white">{t('testimonial_1_author')}</p>
              <Dialog>
                <DialogTrigger asChild>
                  <NextUIButton color="primary" size="sm" className="mt-2">
                    {t('hero_learn_more')}
                  </NextUIButton>
                </DialogTrigger>
                <DialogContent className="p-6 bg-gray-800 rounded-lg max-w-md mx-auto text-white">
                  <p>{t('testimonial_1')}</p>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.2 }}>
          <Card className="bg-gray-800 border-none">
            <CardContent className="pt-6">
              <p className="text-gray-300 mb-4">{t('testimonial_2')}</p>
              <p className="font-bold text-white">{t('testimonial_2_author')}</p>
              <Dialog>
                <DialogTrigger asChild>
                  <NextUIButton color="primary" size="sm" className="mt-2">
                    {t('hero_learn_more')}
                  </NextUIButton>
                </DialogTrigger>
                <DialogContent className="p-6 bg-gray-800 rounded-lg max-w-md mx-auto text-white">
                  <p>{t('testimonial_2')}</p>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </GlowingSection>
  );
};

const CTASection = () => {
  const { t } = useTranslation();
  return (
    <GlowingSection className="py-16 px-4 text-center">
      <motion.h2
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-3xl md:text-4xl font-bold mb-4"
      >
        {t('cta_title')}
      </motion.h2>
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="text-lg mb-6"
      >
        {t('cta_subtitle')}
      </motion.p>
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <Button variant="default" size="lg" className="bg-blue-600 hover:bg-blue-700">
          {t('cta_button')}
        </Button>
      </motion.div>
    </GlowingSection>
  );
};

const LandingPage = () => {
  return (
    <PageContainer>
      <HeroSection />
      <FeaturesSection />
      <TestimonialsSection />
      <CTASection />
    </PageContainer>
  );
};

export default LandingPage;