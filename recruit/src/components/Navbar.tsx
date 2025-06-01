import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Navbar as NextUINavbar, NavbarBrand, NavbarContent, NavbarItem } from '@nextui-org/react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';

const GlowingNavbar = styled(NextUINavbar)`
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
  border-bottom: 1px solid rgba(59, 130, 246, 0.3);
`;

const Navbar = () => {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  return (
    <GlowingNavbar>
      <NavbarBrand>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
          <span className="text-2xl font-bold text-white">HireMe</span>
        </motion.div>
      </NavbarBrand>
      <NavbarContent className="hidden sm:flex gap-4" justify="center">
        <NavbarItem>
          <Link to="/" className="text-white hover:text-blue-400">{t('nav_home')}</Link>
        </NavbarItem>
        <NavbarItem>
          <Link to="/jobs" className="text-white hover:text-blue-400">{t('nav_jobs')}</Link>
        </NavbarItem>
        <NavbarItem>
          <Link to="/employers" className="text-white hover:text-blue-400">{t('nav_employers')}</Link>
        </NavbarItem>
        <NavbarItem>
          <Link to="/about" className="text-white hover:text-blue-400">{t('nav_about')}</Link>
        </NavbarItem>
        <NavbarItem>
          <Link to="/contact" className="text-white hover:text-blue-400">{t('nav_contact')}</Link>
        </NavbarItem>
      </NavbarContent>
      <NavbarContent justify="end">
        <Button
          variant="ghost"
          size="sm"
          className="text-white hover:bg-blue-500/20"
          onClick={() => changeLanguage('en')}
        >
          English
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="text-white hover:bg-blue-500/20"
          onClick={() => changeLanguage('rw')}
        >
          Kinyarwanda
        </Button>
      </NavbarContent>
    </GlowingNavbar>
  );
};

export default Navbar;