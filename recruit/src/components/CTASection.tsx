import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';

const CTAContainer = styled.div`
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  padding: 6rem 2rem;
  text-align: center;
  box-shadow: 0 0 20px var(--glow);
  border-radius: 12px;
`;

const PulseButton = styled(Button)`
  animation: pulse 2s infinite;
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 var(--glow); }
    70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
    100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
  }
`;

const CTASection = () => {
  const { t } = useTranslation();
  return (
    <CTAContainer>
      <motion.h2
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-4xl md:text-5xl font-bold mb-6 text-white tracking-tight"
      >
        {t('cta_title')}
      </motion.h2>
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="text-xl mb-8 max-w-2xl mx-auto text-gray-200"
      >
        {t('cta_subtitle')}
      </motion.p>
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <PulseButton
          variant="default"
          size="lg"
          className="bg-white text-blue-600 hover:bg-gray-100 glow-on-hover text-lg"
        >
          {t('cta_button')}
        </PulseButton>
      </motion.div>
    </CTAContainer>
  );
};

export default CTASection;