import { motion } from 'framer-motion';

const MotionDiv = motion.div;

const Dashboard = () => {
  return (
    <MotionDiv
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mx-auto mt-10 max-w-3xl p-8"
    >
      <h2 className="text-3xl font-bold text-white">Dashboard</h2>
      <p className="text-white">Dashboard page coming soon...</p>
    </MotionDiv>
  );
};

export default Dashboard;