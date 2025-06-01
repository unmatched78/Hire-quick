import React from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuLink } from "@radix-ui/react-navigation-menu";
import { cn } from "@/lib/utils";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-100 to-purple-50 text-gray-800">
      {/* Navigation Bar */}
      <header className="w-full bg-white/60 backdrop-blur-md sticky top-0 z-50">
        <nav className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="text-xl font-extrabold text-indigo-600">RecruitPro</div>
          </div>
          <NavigationMenu>
            <NavigationMenuList className="flex space-x-6">
              <NavigationMenuItem>
                <NavigationMenuLink href="#home" className="text-base font-medium hover:text-indigo-600">
                  Home
                </NavigationMenuLink>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <NavigationMenuLink href="#about" className="text-base font-medium hover:text-indigo-600">
                  About
                </NavigationMenuLink>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <NavigationMenuLink href="#features" className="text-base font-medium hover:text-indigo-600">
                  Features
                </NavigationMenuLink>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <NavigationMenuLink href="#contact" className="text-base font-medium hover:text-indigo-600">
                  Contact
                </NavigationMenuLink>
              </NavigationMenuItem>
            </NavigationMenuList>
          </NavigationMenu>
        </nav>
      </header>

      {/* Hero Section */}
      <section id="home" className="relative flex items-center justify-center h-screen px-6">
        <div className="absolute inset-0 bg-[url('/images/hero-bg.jpg')] bg-cover bg-center opacity-30" />
        <motion.div
          className="relative z-10 text-center max-w-3xl"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-5xl font-extrabold mb-4">
            Your Next Career Move Starts Here
          </h1>
          <p className="text-lg mb-6">
            We connect top talent with leading companies. Post jobs, find candidates, and build your dream team.
          </p>
          <Button size="lg" variant="primary" className="mr-4">
            Get Started
          </Button>
          <Button size="lg" variant="outline">
            Learn More
          </Button>
        </motion.div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-white">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <motion.h2
            className="text-4xl font-bold mb-4 text-indigo-600"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            About RecruitPro
          </motion.h2>
          <motion.p
            className="text-gray-600 text-lg max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            RecruitPro is a modern recruitment and job posting platform designed to streamline the hiring process for companies of all sizes. Whether you’re a startup seeking your first hire or an enterprise managing hundreds of positions, RecruitPro offers the tools and insights you need.
          </motion.p>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-gradient-to-b from-white to-blue-50">
        <div className="max-w-6xl mx-auto px-6">
          <motion.h2
            className="text-3xl md:text-4xl font-bold text-center mb-12 text-indigo-700"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            Platform Features
          </motion.h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature Card 1 */}
            <motion.div
              className="bg-white rounded-2xl shadow-lg p-6 flex flex-col items-center"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <div className="text-4xl mb-4 text-indigo-500">📋</div>
              <h3 className="text-xl font-semibold mb-2">Post Jobs Effortlessly</h3>
              <p className="text-gray-600 text-center">
                Create, customize, and publish job listings in minutes with our intuitive interface.
              </p>
            </motion.div>

            {/* Feature Card 2 */}
            <motion.div
              className="bg-white rounded-2xl shadow-lg p-6 flex flex-col items-center"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <div className="text-4xl mb-4 text-indigo-500">🔍</div>
              <h3 className="text-xl font-semibold mb-2">Candidate Search</h3>
              <p className="text-gray-600 text-center">
                Utilize advanced filters to find the perfect fit for your open positions.
              </p>
            </motion.div>

            {/* Feature Card 3 */}
            <motion.div
              className="bg-white rounded-2xl shadow-lg p-6 flex flex-col items-center"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              <div className="text-4xl mb-4 text-indigo-500">💬</div>
              <h3 className="text-xl font-semibold mb-2">Secure Messaging</h3>
              <p className="text-gray-600 text-center">
                Communicate directly with candidates through our built-in messaging system.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Call-to-Action Section */}
      <section className="py-20 bg-indigo-600">
        <div className="max-w-4xl mx-auto px-6 text-center text-white">
          <motion.h2
            className="text-3xl md:text-4xl font-bold mb-4"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            Ready to Revolutionize Your Hiring?
          </motion.h2>
          <motion.p
            className="mb-6 text-lg"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Join RecruitPro today and experience a smarter way to hire.
          </motion.p>
          <Button size="lg" variant="secondary">
            Sign Up Now
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white py-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center">
          <div className="text-sm text-gray-500">© {new Date().getFullYear()} RecruitPro. All rights reserved.</div>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className="text-gray-500 hover:text-indigo-600 text-sm">Privacy Policy</a>
            <a href="#" className="text-gray-500 hover:text-indigo-600 text-sm">Terms of Service</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
