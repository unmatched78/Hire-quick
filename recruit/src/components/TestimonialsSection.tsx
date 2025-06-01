import { useTranslation } from 'react-i18next';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { User } from 'lucide-react';

const TestimonialsSection = () => {
  const { t } = useTranslation();

  const handleReadMore = (author: string) => {
    toast.success(`Viewing testimonial from ${author}`, {
      position: 'top-right',
      className: 'glow-on-hover',
    });
  };

  return (
    <section className="py-16 px-4">
      <motion.h2
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-4xl font-bold text-center mb-12 text-gray-900"
      >
        {t('testimonials_title')}
      </motion.h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="card flex flex-col glow-on-hover">
            <CardContent className="pt-6 flex-grow">
              <div className="flex items-center mb-4">
                <User className="h-8 w-8 text-blue-500 mr-2" />
                <p className="font-bold text-gray-900">{t('testimonial_1_author')}</p>
              </div>
              <p className="text-gray-600 mb-4">{t('testimonial_1')}</p>
              <Dialog>
                <DialogTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="glow-on-hover border-blue-500 text-gray-900 hover:bg-blue-500/10"
                    onClick={() => handleReadMore(t('testimonial_1_author'))}
                  >
                    {t('hero_learn_more')}
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-white border border-gray-200 rounded-lg glow-on-hover max-w-md mx-auto">
                  <DialogHeader>
                    <DialogTitle className="text-gray-900">{t('testimonial_1_author')}</DialogTitle>
                    <DialogDescription className="text-gray-600">{t('testimonial_1')}</DialogDescription>
                  </DialogHeader>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="card flex flex-col glow-on-hover">
            <CardContent className="pt-6 flex-grow">
              <div className="flex items-center mb-4">
                <User className="h-8 w-8 text-blue-500 mr-2" />
                <p className="font-bold text-gray-900">{t('testimonial_2_author')}</p>
              </div>
              <p className="text-gray-600 mb-4">{t('testimonial_2')}</p>
              <Dialog>
                <DialogTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="glow-on-hover border-blue-500 text-gray-900 hover:bg-blue-500/10"
                    onClick={() => handleReadMore(t('testimonial_2_author'))}
                  >
                    {t('hero_learn_more')}
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-white border border-gray-200 rounded-lg glow-on-hover max-w-md mx-auto">
                  <DialogHeader>
                    <DialogTitle className="text-gray-900">{t('testimonial_2_author')}</DialogTitle>
                    <DialogDescription className="text-gray-600">{t('testimonial_2')}</DialogDescription>
                  </DialogHeader>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  );
};

export default TestimonialsSection;