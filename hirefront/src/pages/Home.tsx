import { motion } from 'framer-motion';
import { BriefcaseIcon, BuildingOffice2Icon, StarIcon } from '@heroicons/react/24/solid';
import { Link } from 'react-router-dom';

const MotionDiv = motion.div;

const Home = () => {
  return (
    <div className="relative min-h-screen glow">
      {/* Hero Section */}
      <div className="py-20 text-center space-y-6">
        <MotionDiv
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-5xl font-bold bg-gradient-to-r from-brand-500 to-brand-600 bg-clip-text text-transparent">
            HireEasy: Your Ultimate Hiring Solution
          </h1>
          <p className="mt-4 text-xl text-white max-w-2xl mx-auto">
            Discover top talent or land your dream job with our all-in-one platform for job seekers and companies.
          </p>
          <input
            placeholder="Search for jobs..."
            className="mt-6 w-full max-w-md mx-auto rounded-md border border-gray-600 bg-gray-700 p-3 text-white focus:border-brand-500 focus:ring focus:ring-brand-500 focus:ring-opacity-50"
          />
          <Link
            to="/jobs"
            className="mt-4 inline-block rounded-md bg-brand-500 px-6 py-3 text-white hover:bg-brand-600"
          >
            Explore Jobs
          </Link>
        </MotionDiv>
      </div>
      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-10 p-8">
        <MotionDiv
          className="p-5 bg-gray-800 rounded-md shadow-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <BriefcaseIcon className="w-8 h-8 text-brand-500" />
          <h3 className="mt-4 text-xl font-bold text-white">Find Your Dream Job</h3>
          <p className="text-white">Explore thousands of opportunities tailored to your skills.</p>
        </MotionDiv>
        <MotionDiv
          className="p-5 bg-gray-800 rounded-md shadow-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <BuildingOffice2Icon className="w-8 h-8 text-brand-500" />
          <h3 className="mt-4 text-xl font-bold text-white">Hire Top Talent</h3>
          <p className="text-white">Post jobs and find the perfect candidates with ease.</p>
        </MotionDiv>
        <MotionDiv
          className="p-5 bg-gray-800 rounded-md shadow-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <StarIcon className="w-8 h-8 text-brand-500" />
          <h3 className="mt-4 text-xl font-bold text-white">Trusted Reviews</h3>
          <p className="text-white">Read authentic company reviews from real employees.</p>
        </MotionDiv>
      </div>
      {/* Testimonial Section */}
      <div className="py-10 text-center bg-gray-700">
        <h2 className="text-3xl font-bold text-white mb-6">What Our Users Say</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 px-8">
          <MotionDiv
            className="p-5 bg-gray-800 rounded-md shadow-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <p className="text-white">"HireEasy helped me land my dream job in just two weeks!"</p>
            <p className="mt-4 font-bold text-white">— Jane Doe</p>
          </MotionDiv>
          <MotionDiv
            className="p-5 bg-gray-800 rounded-md shadow-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <p className="text-white">"The easiest way to find top talent for our company."</p>
            <p className="mt-4 font-bold text-white">— Acme Corp</p>
          </MotionDiv>
        </div>
      </div>
    </div>
  );
};

export default Home;