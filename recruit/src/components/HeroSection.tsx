import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import Particles from 'react-particles';
import { loadFull } from 'tsparticles';
import type { Engine } from 'tsparticles-engine';

const HeroContainer = styled.div`
  background: #ffffff;
  padding: 6rem 1rem;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 15px var(--glow-blue);
`;

const GlowButton = styled(Button)`
  background: linear-gradient(45deg, #3b82f6, #8b5cf6);
  color: white;
  &:hover {
    background: linear-gradient(45deg, #2563eb, #7c3aed);
    box-shadow: 0 0 15px var(--glow-purple);
  }
`;

const HeroSection = () => {
  const { t } = useTranslation();

  const particlesInit = async (engine: Engine) => {
    await loadFull(engine);
  };

  return (
    <HeroContainer>
      <Particles
        id="tsparticles"
        init={particlesInit}
        options={{
          particles: {
            number: { value: 30 },
            color: { value: ['#3b82f6', '#8b5cf6'] },
            shape: { type: 'circle' },
            size: { value: { min: 1, max: 4 } },
            move: { enable: true, speed: 1, direction: 'none', random: true },
            opacity: { value: 0.3 },
          },
          interactivity: {
            events: { onHover: { enable: true, mode: 'repulse' } },
          },
        }}
        style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
      />
      <div className="max-w-5xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-4xl md:text-6xl font-extrabold mb-6 text-gray-900"
          style={{ textShadow: '0 0 10px var(--glow-blue)' }}
        >
          {t('hero_title')}
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-lg md:text-xl mb-8 text-gray-600 max-w-3xl mx-auto"
        >
          {t('hero_subtitle')}
        </motion.p>
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex justify-center gap-4"
        >
          <GlowButton size="lg" className="w-40">
            {t('hero_cta')}
          </GlowButton>
          <Button
            variant="outline"
            size="lg"
            className="w-40 glow-on-hover border-blue-500 text-gray-900 hover:bg-blue-500/10"
          >
            {t('hero_learn_more')}
          </Button>
        </motion.div>
      </div>
    </HeroContainer>
  );
};

export default HeroSection;