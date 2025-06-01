import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: {
          // Navigation
          nav_home: 'Home',
          nav_jobs: 'Jobs',
          nav_employers: 'For Employers',
          nav_about: 'About',
          nav_contact: 'Contact',
          // Hero Section
          hero_title: 'Your All-in-One Recruitment Platform',
          hero_subtitle: 'Connect employers and job seekers seamlessly. From job listings to offer letters, we handle it all.',
          hero_cta: 'Get Started',
          hero_learn_more: 'Learn More',
          // Features Section
          features_title: 'What We Do',
          features_listings: 'Job Listings',
          features_listings_desc: 'Easily create and manage job postings.',
          features_screening: 'Screening',
          features_screening_desc: 'Automate candidate screening with smart filters.',
          features_shortlisting: 'Shortlisting',
          features_shortlisting_desc: 'Quickly shortlist top candidates.',
          features_interviewing: 'Interviewing',
          features_interviewing_desc: 'Schedule and conduct interviews seamlessly.',
          features_offers: 'Offer Letters',
          features_offers_desc: 'Generate professional offer letters.',
          // Testimonials Section
          testimonials_title: 'What Our Users Say',
          testimonial_1: 'This platform made hiring so easy! We found top talent in days.',
          testimonial_1_author: 'Jane Doe, HR Manager',
          testimonial_2: 'I landed my dream job thanks to this platform!',
          testimonial_2_author: 'John Smith, Software Engineer',
          // CTA Section
          cta_title: 'Ready to Transform Recruitment?',
          cta_subtitle: 'Join thousands of employers and job seekers today.',
          cta_button: 'Sign Up Now',
        },
      },
      rw: {
        translation: {
          // Navigation
          nav_home: 'Ahabanza',
          nav_jobs: 'Imirimo',
          nav_employers: 'Kuri abakoresha',
          nav_about: 'Ibyerekeye',
          nav_contact: 'Twandikire',
          // Hero Section
          hero_title: 'Urubuga rwacu rw’uburyo bwose bwo gutanga akazi',
          hero_subtitle: 'Ongera hamwe abakoresha n’abashaka akazi nta nkomyi. Kuva ku itangazo ry’akazi kugeza ku ibaruwa y’akazi, twakemura byose.',
          hero_cta: 'Tangira nonaha',
          hero_learn_more: 'Menya byinshi',
          // Features Section
          features_title: 'Ibyo dukora',
          features_listings: 'Amatangazo y’akazi',
          features_listings_desc: 'Kora kandi ugenzure amatangazo y’akazi byoroshye.',
          features_screening: 'Gusuzuma',
          features_screening_desc: 'Gusuzuma abasabye akazi byikoresha n’amabwiriza y’umwuga.',
          features_shortlisting: 'Guhitamo abanza',
          features_shortlisting_desc: 'Hitamo vuba abasabye akazi beza.',
          features_interviewing: 'Ikiganiro',
          features_interviewing_desc: 'Tegura kandi ukore ibiganiro nta nkomyi.',
          features_offers: 'Ibaruwa z’akazi',
          features_offers_desc: 'Kora ibaruwa z’akazi z’umwuga.',
          // Testimonials Section
          testimonials_title: 'Ibyo abakoresha bacu bavuga',
          testimonial_1: 'Uru rubuga rwatugiriye byoroshye cyane kugira abakozi! Twabonye abahanga mu minsi mike.',
          testimonial_1_author: 'Jane Doe, Umuyobozi w’abakozi',
          testimonial_2: 'Nabonye akazi kanjye ka impano kubera uru rubuga!',
          testimonial_2_author: 'John Smith, Injineli ya Software',
          // CTA Section
          cta_title: 'Witeguye guhindura uburyo bwo gutanga akazi?',
          cta_subtitle: 'Injira mu bihumbi by’abakoresha n’abashaka akazi uyu munsi.',
          cta_button: 'Iyandikishe nonaha',
        },
      },
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;