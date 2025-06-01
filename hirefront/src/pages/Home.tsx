import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import * as Form from '@radix-ui/react-form';
import { Briefcase, Building2, Star } from 'lucide-react';

const MotionDiv = motion.div;

const Home = () => {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Glowing Background */}
      <div className="glow" />

      {/* Hero Section */}
      <section className="py-24 md:py-32 text-center">
        <MotionDiv
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-brand-500 to-brand-600 bg-clip-text text-transparent">
            HireEasy: Connect Talent with Opportunity
          </h1>
          <p className="mt-6 text-lg md:text-xl text-gray-300 max-w-3xl mx-auto">
            Discover top talent or land your dream job with our intuitive platform designed for job seekers and companies.
          </p>
          <Form.Root className="mt-8 max-w-lg mx-auto">
            <Form.Field name="search" className="relative">
              <Form.Control asChild>
                <Input
                  type="text"
                  placeholder="Search for jobs..."
                  className="w-full rounded-full bg-gray-800/50 backdrop-blur-sm pl-12 pr-4 py-3 text-white border-brand-500 focus:ring-brand-500 focus:ring-opacity-50"
                />
              </Form.Control>
              <SearchIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            </Form.Field>
            <div className="mt-6 flex flex-col sm:flex-row justify-center gap-4">
              <Button asChild className="bg-brand-500 hover:bg-brand-600 rounded-full animate-pulse-glow">
                <Link to="/jobs">Explore Jobs</Link>
              </Button>
              <Button asChild variant="outline" className="border-brand-500 text-brand-500 hover:bg-brand-500/20 rounded-full">
                <Link to="/register">Join Now</Link>
              </Button>
            </div>
          </Form.Root>
        </MotionDiv>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
            Why Choose HireEasy?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: Briefcase,
                title: 'Find Your Dream Job',
                description: 'Browse thousands of opportunities tailored to your skills and aspirations.',
                delay: 0.2,
              },
              {
                icon: Building2,
                title: 'Hire Top Talent',
                description: 'Post jobs and connect with the best candidates effortlessly.',
                delay: 0.4,
              },
              {
                icon: Star,
                title: 'Trusted Reviews',
                description: 'Make informed decisions with authentic company reviews.',
                delay: 0.6,
              },
            ].map((feature) => (
              <MotionDiv
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: feature.delay }}
              >
                <Card className="bg-gray-800/80 border-none hover:shadow-2xl transition-shadow duration-300">
                  <CardHeader>
                    <feature.icon className="w-10 h-10 text-brand-500" />
                    <CardTitle className="text-white">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-300">{feature.description}</p>
                  </CardContent>
                </Card>
              </MotionDiv>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-white text-center mb-12">
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
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: testimonial.delay }}
              >
                <Card className="bg-gray-800/80 border-none relative">
                  <CardContent className="pt-6">
                    <Quote className="absolute top-4 left-4 w-8 h-8 text-brand-500 opacity-50" />
                    <p className="text-gray-300 italic">"{testimonial.quote}"</p>
                    <p className="mt-4 font-bold text-white">{testimonial.author}</p>
                    <p className="text-sm text-gray-400">{testimonial.role}</p>
                  </CardContent>
                </Card>
              </MotionDiv>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 bg-gray-900 text-center">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h3 className="text-2xl font-bold text-white">HireEasy</h3>
          <p className="mt-2 text-gray-400">Connecting talent and opportunity.</p>
          <div className="mt-6 flex justify-center gap-6">
            <Link to="/jobs" className="text-gray-300 hover:text-brand-500">Jobs</Link>
            <Link to="/companies" className="text-gray-300 hover:text-brand-500">Companies</Link>
            <Link to="/register" className="text-gray-300 hover:text-brand-500">Sign Up</Link>
            <Link to="/login" className="text-gray-300 hover:text-brand-500">Login</Link>
          </div>
          <p className="mt-4 text-sm text-gray-500">© 2025 HireEasy. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

// Lucide React icons
const SearchIcon = ({ className }: { className: string }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);

const Quote = ({ className }: { className: string }) => (
  <svg
    className={className}
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" />
    <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z" />
  </svg>
);

export default Home;