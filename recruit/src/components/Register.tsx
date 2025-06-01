import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import apiClient from '@/api/client';
import { useAuthStore } from '@/stores/auth';
import { useNavigate } from 'react-router-dom';

interface RegisterForm {
  username: string;
  email: string;
  password: string;
  user_type: 'job_seeker' | 'company_rep';
}

const Register = () => {
  const { t } = useTranslation();
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterForm>();
  const setTokens = useAuthStore((state) => state.setTokens);
  const navigate = useNavigate();

  const onSubmit = async (data: RegisterForm) => {
    try {
      await apiClient.post('/register/', data);
      const response = await apiClient.post('/token/', {
        username: data.username,
        password: data.password,
      });
      setTokens(response.data.access, response.data.refresh);
      toast.success(t('register_success'));
      navigate('/');
    } catch (error) {
      toast.error(t('register_failed'));
    }
  };

  return (
    <div className="max-w-md mx-auto py-16 px-4">
      <Card className="card glow-on-hover">
        <CardHeader>
          <CardTitle className="text-gray-900">{t('register_title')}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <Input
                placeholder={t('username')}
                {...register('username', { required: t('username_required') })}
                className="w-full"
              />
              {errors.username && <p className="text-red-500 text-sm">{errors.username.message}</p>}
            </div>
            <div>
              <Input
                type="email"
                placeholder={t('email')}
                {...register('email', {
                  required: t('email_required'),
                  pattern: { value: /^\S+@\S+$/i, message: t('email_invalid') },
                })}
                className="w-full"
              />
              {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
            </div>
            <div>
              <Input
                type="password"
                placeholder={t('password')}
                {...register('password', { required: t('password_required'), minLength: { value: 6, message: t('password_min') } })}
                className="w-full"
              />
              {errors.password && <p className="text-red-500 text-sm">{errors.password.message}</p>}
            </div>
            <div>
              <Select {...register('user_type', { required: t('user_type_required') })}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder={t('select_user_type')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="job_seeker">{t('job_seeker')}</SelectItem>
                  <SelectItem value="company_rep">{t('company_rep')}</SelectItem>
                </SelectContent>
              </Select>
              {errors.user_type && <p className="text-red-500 text-sm">{errors.user_type.message}</p>}
            </div>
            <Button
              type="submit"
              className="w-full glow-on-hover bg-gradient-to-r from-blue-500 to-purple-500 text-white"
            >
              {t('register_button')}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Register;