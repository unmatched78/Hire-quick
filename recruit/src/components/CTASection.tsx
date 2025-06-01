import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';

const CTAContainer = styled.div`
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  padding: 4rem 2rem;
  text-align: center;
  color: white;
`;

const CTASection = () => {
  return (
    <CTAContainer>
      <motion.h2
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-3xl md:text-4xl font-bold mb-4"
      >
        Ready to Transform Recruitment?
      </motion.h2>
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="text-lg mb-6"
      >
        Join thousands of employers and job seekers today.
      </motion.p>
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <Button variant="default" size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
          Sign Up Now
        </Button>
      </motion.div>
    </CTAContainer>
  );
};

export default CTASection;