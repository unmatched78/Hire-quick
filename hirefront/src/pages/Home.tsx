import { motion } from 'framer-motion';
import { BriefcaseIcon, BuildingOffice2Icon, StarIcon } from '@heroicons/react/24/solid';
import { Link } from 'react-router-dom';
import * as Form from '@radix-ui/react-form';

const MotionDiv = motion.div;

const Home = () => {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Glowing Background */}
      <div className="glow" />

      {/* Hero Section */}
      <section className="relative py-24 md:py-32 text-center">
        <MotionDiv
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          <h1 className="text-4xl md:text-6xl font-bold font-poppins bg-gradient-to-r from-brand-500 to-brand-600 bg-clip-text text-transparent">
            HireEasy: Connect Talent with Opportunity
          </h1>
          <p className="mt-6 text-lg md:text-xl text-gray-300 font-inter max-w-3xl mx-auto">
            Your all-in-one platform to discover top talent or land your dream job with ease and confidence.
          </p>
          <Form.Root className="mt-8 max-w-lg mx-auto">
            <Form.Field name="search" className="relative">
              <Form.Control asChild>
                <input
                  type="text"
                  placeholder="Search for jobs..."
                  className="w-full rounded-full border border-gray-600 bg-gray-800/50 backdrop-blur-sm p-4 pl-12 text-white focus:border-brand-500 focus:ring-2 focus:ring-brand-500 focus:ring-opacity-50 transition-all"
                />
              </Form.Control>
              <svg
                className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </Form.Field>
            <div className="mt-6 flex flex-col sm:flex-row justify-center gap-4">
              <Link to="/jobs" className="btn-primary animate-pulse-glow">
                Explore Jobs
              </Link>
              <Link to="/register" className="rounded-full border border-brand-500 px-6 py-3 text-white font-semibold hover:bg-brand-500/20 transition-all">
                Join Now
              </Link>
            </div>
          </Form.Root>
        </MotionDiv>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold font-poppins text-white text-center mb-12">
            Why Choose HireEasy?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: BriefcaseIcon,
                title: 'Find Your Dream Job',
                description: 'Browse thousands of opportunities tailored to your skills and aspirations.',
                delay: 0.2,
              },
              {
                icon: BuildingOffice2Icon,
                title: 'Hire Top Talent',
                description: 'Post jobs and connect with the best candidates effortlessly.',
                delay: 0.4,
              },
              {
                icon: StarIcon,
                title: 'Trusted Reviews',
                description: 'Make informed decisions with authentic company reviews.',
                delay: 0.6,
              },
            ].map((feature) => (
              <MotionDiv
                key={feature.title}
                className="p-6 bg-gray-800/80 rounded-xl shadow-xl hover:shadow-2xl transition-shadow duration-300"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: feature.delay }}
              >
                <feature.icon className="w-10 h-10 text-brand-500 mb-4" />
                <h3 className="text-xl font-semibold font-poppins text-white">{feature.title}</h3>
                <p className="mt-2 text-gray-300 font-inter">{feature.description}</p>
              </MotionDiv>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold font-poppins text-white text-center mb-12">
            What Our Users Say
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[
              {
                quote: 'HireEasy helped me land my dream job in just two weeks! The platform is intuitive and user-friendly.',
                author: 'Jane Doe',
                role: 'Software Engineer',
                delay: 0.2,
              },
              {
                quote: 'The easiest way to find top talent for our company. HireEasy streamlined our hiring process.',
                author: 'Acme Corp',
                role: 'Hiring Manager',
                delay: 0.4,
              },
            ].map((testimonial) => (
              <MotionDiv
                key={testimonial.author}
                className="p-6 bg-gray-800/80 rounded-xl shadow-xl relative"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: testimonial.delay }}
              >
                <svg
                  className="absolute top-4 left-4 w-8 h-8 text-brand-500 opacity-50"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M3 3h18v18H3V3zm16 16V5H5v14h14zm-2-2H7v-2h10v2zm0-4H7v-2h10v2zm0-4H7V7h10v2z" />
                </svg>
                <p className="text-gray-300 font-inter italic">"{testimonial.quote}"</p>
                <p className="mt-4 font-bold text-white font-poppins">{testimonial.author}</p>
                <p className="text-sm text-gray-400 font-inter">{testimonial.role}</p>
              </MotionDiv>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-gray-900 text-center">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-2xl font-bold font-poppins text-white">HireEasy</h3>
          <p className="mt-2 text-gray-400 font-inter">Connecting talent and opportunity.</p>
          <div className="mt-6 flex justify-center gap-6">
            <Link to="/jobs" className="text-gray-300 hover:text-brand-500 font-inter">Jobs</Link>
            <Link to="/companies" className="text-gray-300 hover:text-brand-500 font-inter">Companies</Link>
            <Link to="/register" className="text-gray-300 hover:text-brand-500 font-inter">Sign Up</Link>
            <Link to="/login" className="text-gray-300 hover:text-brand-500 font-inter">Login</Link>
          </div>
          <p className="mt-4 text-sm text-gray-500 font-inter">&copy; 2025 HireEasy. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;