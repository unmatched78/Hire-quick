import { Button } from '@/components/ui/button';
import { Button as HeroUIButton } from '@nextui-org/react';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';

const HeroContainer = styled.div`
  background: linear-gradient(135deg, #6b7280 0%, #1f2937 100%);
  padding: 4rem 2rem;
  text-align: center;
  color: white;
`;

const HeroSection = () => {
  return (
    <HeroContainer>
      <motion.h1
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-4xl md:text-6xl font-bold mb-4"
      >
        Your All-in-One Recruitment Platform
      </motion.h1>
      <motion.p
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="text-lg md:text-xl mb-6 max-w-2xl mx-auto"
      >
        Connect employers and job seekers seamlessly. From job listings to offer letters, we handle it all.
      </motion.p>
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="flex gap-4 justify-center"
      >
        <Button variant="default" size="lg" className="bg-blue-600 hover:bg-blue-700">
          Get Started
        </Button>
        <HeroUIButton color="primary" size="lg">
          Learn More
        </HeroUIButton>
      </motion.div>
    </HeroContainer>
  );
};

export default HeroSection;