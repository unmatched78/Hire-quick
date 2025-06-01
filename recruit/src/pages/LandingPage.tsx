import { Toaster } from '@/components/ui/sonner';
import HeroSection from '@/components/HeroSection';
import FeaturesSection from '@/components/FeaturesSection';
import TestimonialsSection from '@/components/TestimonialsSection';
import CTASection from '@/components/CTASection';
import Footer from '@/components/Footer';
import styled from '@emotion/styled';

const PageContainer = styled.div`
  background: #ffffff;
  min-height: 100vh;
`;

const LandingPage = () => {
  return (
    <PageContainer>
      <Toaster richColors position="top-right" />
      <HeroSection />
      <div className="max-w-7xl mx-auto space-y-16 px-4">
        <FeaturesSection />
        <TestimonialsSection />
        <CTASection />
      </div>
      <Footer />
    </PageContainer>
  );
};

export default LandingPage;