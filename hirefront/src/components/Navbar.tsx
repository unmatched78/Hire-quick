import { Link } from 'react-router-dom';
import { UserIcon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

const MotionButton = motion.button;

const Navbar = () => {
  return (
    <nav className="bg-gray-800 px-4 py-3 shadow-lg">
      <div className="flex h-16 items-center justify-between">
        <span className="text-2xl font-bold text-brand-500">HireEasy</span>
        <div className="flex items-center gap-6">
          <Link to="/" className="text-white hover:text-brand-500">Home</Link>
          <Link to="/jobs" className="text-white hover:text-brand-500">Jobs</Link>
          <Link to="/companies" className="text-white hover:text-brand-500">Companies</Link>
          <Link to="/dashboard" className="text-white hover:text-brand-500">Dashboard</Link>
          <MotionButton
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-2 rounded-md border border-brand-500 px-4 py-2 text-white hover:bg-brand-500"
          >
            <UserIcon className="w-5 h-5" />
            <Link to="/login">Login</Link>
          </MotionButton>
          <MotionButton
            whileHover={{ scale: 1.05 }}
            className="rounded-md bg-brand-500 px-4 py-2 text-white hover:bg-brand-600"
          >
            <Link to="/register">Sign Up</Link>
          </MotionButton>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;