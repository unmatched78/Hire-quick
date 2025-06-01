// src/components/Footer.tsx
import { useTranslation } from 'react-i18next';
import styled from '@emotion/styled';

const FooterContainer = styled.footer`
  background: rgba(15, 23, 42, 0.95);
  padding: 2rem 4rem;
  text-align: center;
  border-top: 1px solid rgba(59, 130, 246, 0.3);
`;

const Footer = () => {
  const { t } = useTranslation();
  return (
    <FooterContainer>
      <p className="text-gray-300">&copy; 2025 HireMe. All rights reserved.</p>
      <div className="flex justify-center gap-4 mt-2">
        <a href="#" className="text-white hover:text-blue-400">{t('nav_contact')}</a>
        <a href="#" className="text-white hover:text-blue-400">Twitter</a>
        <a href="#" className="text-white hover:text-blue-400">LinkedIn</a>
      </div>
    </FooterContainer>
  );
};

export default Footer;