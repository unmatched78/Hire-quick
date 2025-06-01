import React from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuLink,
} from "@radix-ui/react-navigation-menu";

export default function Home() {
  return (
    <div className="relative min-h-screen bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900 overflow-hidden text-white">
      {/* 1st Glowing Blob */}
      <div className="absolute -top-32 -left-32 w-96 h-96 bg-gradient-to-tr from-indigo-500 to-purple-500 opacity-70 rounded-full blur-3xl animate-slow-pulse"></div>
      {/* 2nd Glowing Blob */}
      <div className="absolute -bottom-48 -right-48 w-[600px] h-[600px] bg-gradient-to-bl from-pink-500 to-indigo-500 opacity-60 rounded-full blur-3xl animate-slow-pulse"></div>

      {/* Navigation Bar */}
      <header className="w-full bg-black bg-opacity-40 backdrop-blur-lg sticky top-0 z-50">
        <nav className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 to-pink-400">
              RecruitPro
            </span>
          </div>
          <NavigationMenu>
            <NavigationMenuList className="flex space-x-8">
              {["home", "about", "features", "contact"].map((item) => (
                <NavigationMenuItem key={item}>
                  <NavigationMenuLink
                    href={`#${item}`}
                    className="relative text-lg font-medium uppercase tracking-wide text-white hover:text-pink-400 transition-colors
                               after:absolute after:-bottom-1 after:left-0 after:h-0.5 after:w-0 after:bg-pink-400
                               hover:after:w-full hover:after:transition-all after:transition-all"
                  >
                    {item}
                  </NavigationMenuLink>
                </NavigationMenuItem>
              ))}
            </NavigationMenuList>
          </NavigationMenu>
        </nav>
      </header>

      {/* Hero Section */}
      <section id="home" className="relative flex flex-col items-center justify-center h-screen px-8 text-center">
        <motion.div
          className="relative z-10 max-w-3xl"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1 }}
        >
          <h1 className="text-6xl md:text-7xl font-extrabold mb-6 leading-tight tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-200 to-pink-300 drop-shadow-lg">
            Elevate Your Hiring Experience
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-gray-200">
            Empower companies and candidates with seamless recruiting and job posting. Discover opportunities. Connect talent.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Button size="lg" className="bg-pink-500 hover:bg-pink-600 shadow-lg shadow-pink-500/50 text-white transition-all">
              Get Started
            </Button>
            <Button size="lg" variant="outline" className="border-pink-500 text-white hover:bg-pink-500 hover:text-white hover:shadow-lg hover:shadow-pink-500/50 transition-all">
              Learn More
            </Button>
          </div>
        </motion.div>
      </section>

      {/* About Section */}
      <section id="about" className="relative z-10 py-24">
        <div className="max-w-4xl mx-auto px-8 text-center">
          <motion.h2
            className="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-pink-300"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            About RecruitPro
          </motion.h2>
          <motion.p
            className="text-lg text-gray-200 md:text-xl"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            RecruitPro is a state-of-the-art recruitment and job posting platform built to streamline the hiring process. From startups to enterprises, we deliver powerful tools for job creation, candidate discovery, and communication.
          </motion.p>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 py-24">
        <div className="max-w-6xl mx-auto px-8">
          <motion.h2
            className="text-4xl md:text-5xl font-bold text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-pink-300"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
          >
            Platform Features
          </motion.h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            <motion.div
              className="bg-black bg-opacity-50 rounded-3xl shadow-xl p-8 flex flex-col items-center transform hover:scale-105 transition-transform"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <div className="text-5xl mb-4 text-pink-500 animate-slow-pulse">📋</div>
              <h3 className="text-2xl font-semibold mb-3">Post Jobs Effortlessly</h3>
              <p className="text-gray-300 text-center">
                Create and customize job listings in seconds with our intuitive editor and templates.
              </p>
            </motion.div>
            <motion.div
              className="bg-black bg-opacity-50 rounded-3xl shadow-xl p-8 flex flex-col items-center transform hover:scale-105 transition-transform"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <div className="text-5xl mb-4 text-indigo-400 animate-slow-pulse">🔍</div>
              <h3 className="text-2xl font-semibold mb-3">Advanced Candidate Search</h3>
              <p className="text-gray-300 text-center">
                Filter, sort, and connect with top talent using smart search and AI-driven recommendations.
              </p>
            </motion.div>
            <motion.div
              className="bg-black bg-opacity-50 rounded-3xl shadow-xl p-8 flex flex-col items-center transform hover:scale-105 transition-transform"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              <div className="text-5xl mb-4 text-purple-400 animate-slow-pulse">💬</div>
              <h3 className="text-2xl font-semibold mb-3">Secure Messaging</h3>
              <p className="text-gray-300 text-center">
                Communicate directly with candidates in real time with our encrypted messaging system.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Call-to-Action Section */}
      <section id="contact" className="relative z-10 py-24 bg-gradient-to-br from-indigo-800 to-pink-800 text-center">
        <motion.h2
          className="text-4xl md:text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-indigo-200 to-pink-200"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          Ready to Transform Your Hiring?
        </motion.h2>
        <motion.p
          className="text-lg md:text-xl mb-8 text-gray-200"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          Join RecruitPro today and access the tools you need to hire smarter, faster, and more effectively.
        </motion.p>
        <Button size="lg" className="bg-indigo-500 hover:bg-indigo-600 shadow-lg shadow-indigo-500/50 text-white transition-all">
          Sign Up Now
        </Button>
      </section>

      {/* Footer */}
      <footer className="relative z-10 bg-black bg-opacity-60 py-8">
        <div className="max-w-7xl mx-auto px-8 flex flex-col md:flex-row justify-between items-center">
          <span className="text-sm text-gray-400">© {new Date().getFullYear()} RecruitPro. All rights reserved.</span>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="#" className="text-gray-400 hover:text-pink-400 text-sm transition-colors">Privacy Policy</a>
            <a href="#" className="text-gray-400 hover:text-pink-400 text-sm transition-colors">Terms of Service</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
