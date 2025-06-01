import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  config: {
    initialColorMode: 'dark',
    useSystemColorMode: false,
  },
  colors: {
    brand: {
      500: '#7928CA', // Neon purple
      600: '#FF0080', // Neon pink
      700: '#00DDEB', // Neon cyan
    },
  },
  fonts: {
    heading: 'Inter, sans-serif',
    body: 'Inter, sans-serif',
  },
  styles: {
    global: {
      body: {
        bg: 'gray.900',
        color: 'white',
        backgroundImage: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)',
      },
    },
  },
});

export default theme;