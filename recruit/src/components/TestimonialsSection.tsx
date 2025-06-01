import { Dialog, DialogContent, DialogTrigger } from '@radix-ui/react-dialog';
import { Button as HeroUIButton } from '@nextui-org/react';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';

const TestimonialCard = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const TestimonialsSection = () => {
  return (
    <section className="py-12 px-4 bg-white">
      <h2 className="text-3xl font-bold text-center mb-8">What Our Users Say</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
          <TestimonialCard>
            <p className="mb-4">"This platform made hiring so easy! We found top talent in days."</p>
            <p className="font-bold">— Jane Doe, HR Manager</p>
            <Dialog>
              <DialogTrigger asChild>
                <HeroUIButton color="primary" size="sm" className="mt-2">
                  Read More
                </HeroUIButton>
              </DialogTrigger>
              <DialogContent className="p-6 bg-white rounded-lg max-w-md mx-auto">
                <p>Full testimonial: The platform streamlined our entire recruitment process...</p>
              </DialogContent>
            </Dialog>
          </TestimonialCard>
        </motion.div>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.2 }}>
          <TestimonialCard>
            <p className="mb-4">"I landed my dream job thanks to this platform!"</p>
            <p className="font-bold">— John Smith, Software Engineer</p>
            <Dialog>
              <DialogTrigger asChild>
                <HeroUIButton color="primary" size="sm" className="mt-2">
                  Read More
                </HeroUIButton>
              </DialogTrigger>
              <DialogContent className="p-6 bg-white rounded-lg max-w-md mx-auto">
                <p>Full testimonial: The job search was intuitive and fast...</p>
              </DialogContent>
            </Dialog>
          </TestimonialCard>
        </motion.div>
      </div>
    </section>
  );
};

export default TestimonialsSection;