import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import apiClient from '@/api/client';
import { useAuthStore } from '@/stores/auth';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const { t } = useTranslation();
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const setTokens = useAuthStore((state) => state.setTokens);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiClient.post('/token/', credentials);
      setTokens(response.data.access, response.data.refresh);
      toast.success(t('login_success'));
      navigate('/');
    } catch (error) {
      toast.error(t('login_failed'));
    }
  };

  return (
    <div className="max-w-md mx-auto py-16 px-4">
      <Card className="card glow-on-hover">
        <CardHeader>
          <CardTitle className="text-gray-900">{t('login_title')}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="text"
              placeholder={t('username')}
              value={credentials.username}
              onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
              className="w-full"
            />
            <Input
              type="password"
              placeholder={t('password')}
              value={credentials.password}
              onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
              className="w-full"
            />
            <Button
              type="submit"
              className="w-full glow-on-hover bg-gradient-to-r from-blue-500 to-purple-500 text-white"
            >
              {t('login_button')}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;