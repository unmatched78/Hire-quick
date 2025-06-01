import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  Navbar as NextUINavbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  NavbarMenuToggle,
  NavbarMenu,
  NavbarMenuItem,
} from '@nextui-org/react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import styled from '@emotion/styled';

const GlowingNavbar = styled(NextUINavbar)`
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
  backdrop-filter: blur(8px);
  box-shadow: 0 0 15px var(--glow);
  border-bottom: 1px solid rgba(59, 130, 246, 0.3);
  position: sticky;
  top: 0;
  z-index: 50;
`;

const Navbar = () => {
  const { t, i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  const menuItems = [
    { path: '/', label: 'nav_home' },
    { path: '/jobs', label: 'nav_jobs' },
    { path: '/employers', label: 'nav_employers' },
    { path: '/about', label: 'nav_about' },
    { path: '/contact', label: 'nav_contact' },
  ];

  return (
    <GlowingNavbar>
      <NavbarBrand>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="text-2xl font-bold text-white tracking-tight">HireMe</span>
        </motion.div>
      </NavbarBrand>
      <NavbarContent className="hidden sm:flex gap-6" justify="center">
        {menuItems.map((item, index) => (
          <NavbarItem key={item.path}>
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Link
                to={item.path}
                className="text-white hover:text-blue-400 glow-on-hover px-3 py-2 rounded-md"
              >
                {t(item.label)}
              </Link>
            </motion.div>
          </NavbarItem>
        ))}
      </NavbarContent>
      <NavbarContent justify="end">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Button
            variant="ghost"
            size="sm"
            className="text-white hover:bg-blue-500/20 glow-on-hover"
            onClick={() => changeLanguage('en')}
          >
            English
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-white hover:bg-blue-500/20 glow-on-hover"
            onClick={() => changeLanguage('rw')}
          >
            Kinyarwanda
          </Button>
        </motion.div>
      </NavbarContent>
      <NavbarMenuToggle className="sm:hidden text-white" />
      <NavbarMenu className="bg-gray-900/90 backdrop-blur-md">
        {menuItems.map((item, index) => (
          <NavbarMenuItem key={item.path}>
            <Link
              to={item.path}
              className="w-full text-white hover:text-blue-400 py-2"
            >
              {t(item.label)}
            </Link>
          </NavbarMenuItem>
        ))}
      </NavbarMenu>
    </GlowingNavbar>
  );
};

export default Navbar;