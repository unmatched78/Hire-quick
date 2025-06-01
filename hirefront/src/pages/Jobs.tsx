import { motion } from 'framer-motion';

const MotionDiv = motion.div;

const Jobs = () => {
  return (
    <MotionDiv
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mx-auto mt-10 max-w-3xl p-8"
    >
      <h2 className="text-3xl font-bold text-white">Job Listings</h2>
      <p className="text-white">Job listings coming soon...</p>
    </MotionDiv>
  );
};

export default Jobs;