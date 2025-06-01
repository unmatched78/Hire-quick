import HeroSection from '@/components/HeroSection';
import FeaturesSection from '@/components/FeaturesSection';
import TestimonialsSection from '@/components/TestimonialsSection';
import CTASection from '@/components/CTASection';
import styled from '@emotion/styled';

const PageContainer = styled.div`
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  min-height: 100vh;
  color: white;
`;

const LandingPage = () => {
  return (
    <PageContainer>
      <HeroSection />
      <div className="max-w-7xl mx-auto space-y-16">
        <FeaturesSection />
        <TestimonialsSection />
        <CTASection />
      </div>
    </PageContainer>
  );
};

export default LandingPage;