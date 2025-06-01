import { useTranslation } from 'react-i18next';
import { Dialog, DialogContent, DialogTrigger } from '@radix-ui/react-dialog';
import { Button as NextUIButton } from '@nextui-org/react';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import { User } from 'lucide-react';

const GlowingCard = styled.div`
  background: rgba(15, 23, 42, 0.9);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
  &:hover {
    box-shadow: 0 0 15px var(--glow);
  }
`;

const GlowingDialog = styled(DialogContent)`
  background: rgba(15, 23, 42, 0.95);
  border-radius: 12px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 0 20px var(--glow);
`;

const TestimonialsSection = () => {
  const { t } = useTranslation();
  return (
    <section className="py-16 px-4 bg-transparent">
      <motion.h2
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-4xl font-bold text-center mb-12 text-white"
      >
        {t('testimonials_title')}
      </motion.h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <GlowingCard>
            <div className="flex items-center mb-4">
              <User className="h-8 w-8 text-blue-400 mr-2" />
              <p className="font-bold text-white">{t('testimonial_1_author')}</p>
            </div>
            <p className="text-gray-300 mb-4">{t('testimonial_1')}</p>
            <Dialog>
              <DialogTrigger asChild>
                <NextUIButton color="primary" size="sm" className="glow-on-hover">
                  {t('hero_learn_more')}
                </NextUIButton>
              </DialogTrigger>
              <GlowingDialog className="p-6 max-w-md mx-auto text-white">
                <p>{t('testimonial_1')}</p>
              </GlowingDialog>
            </Dialog>
          </GlowingCard>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <GlowingCard>
            <div className="flex items-center mb-4">
              <User className="h-8 w-8 text-blue-400 mr-2" />
              <p className="font-bold text-white">{t('testimonial_2_author')}</p>
            </div>
            <p className="text-gray-300 mb-4">{t('testimonial_2')}</p>
            <Dialog>
              <DialogTrigger asChild>
                <NextUIButton color="primary" size="sm" className="glow-on-hover">
                  {t('hero_learn_more')}
                </NextUIButton>
              </DialogTrigger>
              <GlowingDialog className="p-6 max-w-md mx-auto text-white">
                <p>{t('testimonial_2')}</p>
              </GlowingDialog>
            </Dialog>
          </GlowingCard>
        </motion.div>
      </div>
    </section>
  );
};

export default TestimonialsSection;