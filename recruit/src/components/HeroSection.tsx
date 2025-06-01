import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Button as NextUIButton } from '@nextui-org/react';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';
import Particles from 'react-particles';
import { loadFull } from 'tsparticles';
import type { Engine } from 'tsparticles-engine';

const HeroContainer = styled.div`
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  padding: 6rem 2rem;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 20px var(--glow);
`;

const GlowButton = styled(Button)`
  background: linear-gradient(45deg, #3b82f6, #8b5cf6);
  &:hover {
    background: linear-gradient(45deg, #2563eb, #7c3aed);
    box-shadow: 0 0 15px var(--glow);
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
            number: { value: 50 },
            color: { value: ['#3b82f6', '#8b5cf6'] },
            shape: { type: 'circle' },
            size: { value: { min: 1, max: 5 } },
            move: { enable: true, speed: 2, direction: 'none', random: true },
            opacity: { value: 0.5 },
          },
          interactivity: {
            events: {
              onHover: { enable: true, mode: 'repulse' },
            },
          },
        }}
        style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
      />
      <motion.h1
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-5xl md:text-7xl font-extrabold mb-6 text-white tracking-tight"
        style={{ textShadow: '0 0 10px var(--glow)' }}
      >
        {t('hero_title')}
      </motion.h1>
      <motion.p
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto text-gray-300"
      >
        {t('hero_subtitle')}
      </motion.p>
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="flex gap-4 justify-center"
      >
        <GlowButton variant="default" size="lg" className="text-white">
          {t('hero_cta')}
        </GlowButton>
        <NextUIButton
          color="primary"
          size="lg"
          className="glow-on-hover bg-gradient-to-r from-purple-500 to-blue-500"
        >
          {t('hero_learn_more')}
        </NextUIButton>
      </motion.div>
    </HeroContainer>
  );
};

export default HeroSection;