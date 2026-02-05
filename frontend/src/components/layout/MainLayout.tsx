import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LogOut, LayoutDashboard, Settings, User } from 'lucide-react';

const MainLayout: React.FC = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col">
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <Link to="/" className="text-2xl font-bold text-blue-600">
                        AI Vocab
                    </Link>
                    <div className="flex items-center space-x-4">
                        <span className="text-gray-700 font-medium">{user?.username || 'Guest'}</span>
                        <button
                            onClick={handleLogout}
                            className="p-2 text-gray-500 hover:text-red-600 transition-colors"
                            title="Logout"
                        >
                            <LogOut size={20} />
                        </button>
                    </div>
                </div>
            </header>

            <div className="flex flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
                {/* Sidebar */}
                <aside className="w-64 hidden md:block">
                    <nav className="space-y-1">
                        <Link
                            to="/"
                            className="flex items-center px-4 py-2 text-sm font-medium text-gray-900 bg-white rounded-md shadow-sm"
                        >
                            <LayoutDashboard className="mr-3 h-5 w-5 text-gray-400" />
                            Tổng quan
                        </Link>
                        <Link
                            to="/profile"
                            className="flex items-center px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                        >
                            <User className="mr-3 h-5 w-5 text-gray-400" />
                            Tài khoản
                        </Link>
                        <Link
                            to="/settings"
                            className="flex items-center px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
                        >
                            <Settings className="mr-3 h-5 w-5 text-gray-400" />
                            Cài đặt
                        </Link>
                    </nav>
                </aside>

                {/* Main Content */}
                <main className="flex-1">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default MainLayout;
