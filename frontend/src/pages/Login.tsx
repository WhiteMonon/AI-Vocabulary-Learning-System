import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { loginApi, getMeApi } from '../api/auth';
import { Loader2, AlertCircle } from 'lucide-react';

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            const formData = new FormData();
            formData.append('username', email); // FastAPI uses username field for email in OAuth2
            formData.append('password', password);

            const tokenRes = await loginApi(formData);
            localStorage.setItem('token', tokenRes.access_token);

            const userData = await getMeApi();
            login(tokenRes.access_token, userData);
            navigate('/');
        } catch (err: any) {
            console.error('Login error:', err);
            setError(err.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng kiểm tra lại email/mật khẩu.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-2xl shadow-xl shadow-indigo-100/50 border border-gray-100">
                <div>
                    <div className="mx-auto h-12 w-12 bg-indigo-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-indigo-200">
                        V
                    </div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                        Đăng nhập vào AI Vocab
                    </h2>
                    <p className="mt-2 text-center text-gray-600">
                        Chào mừng bạn quay trở lại!
                    </p>
                </div>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm flex items-center animate-shake">
                        <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0" />
                        {error}
                    </div>
                )}

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">Email</label>
                            <input
                                type="email"
                                required
                                className="appearance-none relative block w-full px-4 py-3 border border-gray-200 placeholder-gray-400 text-gray-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500 transition-all sm:text-sm"
                                placeholder="name@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1 ml-1">Mật khẩu</label>
                            <input
                                type="password"
                                required
                                className="appearance-none relative block w-full px-4 py-3 border border-gray-200 placeholder-gray-400 text-gray-900 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500 transition-all sm:text-sm"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all shadow-lg shadow-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                'Đăng nhập'
                            )}
                        </button>
                    </div>

                    <p className="text-center text-sm text-gray-600">
                        Chưa có tài khoản?{' '}
                        <span className="font-semibold text-indigo-600 hover:text-indigo-500 cursor-pointer">
                            Đăng ký ngay
                        </span>
                    </p>
                </form>
            </div>
        </div>
    );
};

export default Login;
