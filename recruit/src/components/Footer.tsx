import { useTranslation } from 'react-i18next';
import styled from '@emotion/styled';

const FooterContainer = styled.footer`
  background: #ffffff;
  padding: 2rem 4rem;
  text-align: center;
  border-top: 1px solid rgba(59, 130, 246, 0.2);
  box-shadow: 0 0 10px var(--glow-blue);
`;

const Footer = () => {
  const { t } = useTranslation();
  return (
    <FooterContainer className="mt-16">
      <p className="text-gray-600">© 2025 HireMe. All rights reserved.</p>
      <div className="flex justify-center gap-4 mt-2">
        <a href="#" className="text-gray-900 hover:text-blue-500 glow-on-hover">{t('nav_contact')}</a>
        <a href="#" className="text-gray-900 hover:text-blue-500 glow-on-hover">Twitter</a>
        <a href="#" className="text-gray-900 hover:text-blue-500 glow-on-hover">LinkedIn</a>
      </div>
    </FooterContainer>
  );
};

export default Footer;