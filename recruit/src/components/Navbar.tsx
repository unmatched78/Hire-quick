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
import { useAuthStore } from '@/stores/auth';
import { toast } from 'sonner';

const GlowingNavbar = styled(NextUINavbar)`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  box-shadow: 0 0 15px var(--glow-blue);
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  position: sticky;
  top: 0;
  z-index: 50;
`;

const Navbar = () => {
  const { t, i18n } = useTranslation();
  const { isAuthenticated, clearAuth } = useAuthStore();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  const handleLogout = () => {
    clearAuth();
    toast.success(t('logout_success'));
  };

  const menuItems = [
    { path: '/', label: 'nav_home' },
    { path: '/jobs', label: 'nav_jobs' },
    ...(isAuthenticated ? [{ path: '/dashboard', label: 'nav_dashboard' }] : []),
  ];

  return (
    <GlowingNavbar>
      <NavbarBrand>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <span className="text-2xl font-bold text-gray-900">HireMe</span>
        </motion.div>
      </NavbarBrand>
      <NavbarContent className="hidden sm:flex gap-4" justify="center">
        {menuItems.map((item, index) => (
          <NavbarItem key={item.path}>
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Link
                to={item.path}
                className="text-gray-900 hover:text-blue-500 glow-on-hover px-3 py-2 rounded-md font-medium"
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
          className="flex gap-2"
        >
          <Button
            variant="outline"
            size="sm"
            className="w-24 text-gray-900 border-blue-500 hover:bg-blue-500/10 glow-on-hover"
            onClick={() => changeLanguage('en')}
          >
            English
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="w-24 text-gray-900 border-blue-500 hover:bg-blue-500/10 glow-on-hover"
            onClick={() => changeLanguage('rw')}
          >
            Kinyarwanda
          </Button>
          {isAuthenticated ? (
            <Button
              variant="outline"
              size="sm"
              className="w-24 text-gray-900 border-blue-500 hover:bg-blue-500/10 glow-on-hover"
              onClick={handleLogout}
            >
              {t('logout')}
            </Button>
          ) : (
            <>
              <Link to="/login">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-24 text-gray-900 border-blue-500 hover:bg-blue-500/10 glow-on-hover"
                >
                  {t('login')}
                </Button>
              </Link>
              <Link to="/register">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-24 text-gray-900 border-blue-500 hover:bg-blue-500/10 glow-on-hover"
                >
                  {t('register')}
                </Button>
              </Link>
            </>
          )}
        </motion.div>
      </NavbarContent>
      <NavbarMenuToggle className="sm:hidden text-gray-900" />
      <NavbarMenu className="bg-white/90 backdrop-blur-md">
        {menuItems.map((item) => (
          <NavbarMenuItem key={item.path}>
            <Link
              to={item.path}
              className="w-full text-gray-900 hover:text-blue-500 py-2"
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