import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { PlusCircle, BookOpen, Brain, MessageSquare, TrendingUp, Target, Calendar, Award } from 'lucide-react';
import { getVocabularyStats } from '../api/vocabulary';

const Dashboard: React.FC = () => {
    // Lấy thống kê vocabulary
    const { data: stats, isLoading: statsLoading } = useQuery({
        queryKey: ['vocabulary-stats'],
        queryFn: getVocabularyStats,
    });

    // Tính accuracy % (giả định: learned / total * 100)
    const accuracy = stats && stats.total_vocabularies > 0
        ? Math.round((stats.learned / stats.total_vocabularies) * 100)
        : 0;

    return (
        <div className="space-y-8">
            {/* Hero Section */}
            <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 rounded-3xl p-8 text-white shadow-2xl shadow-indigo-200">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold mb-2">Chào mừng trở lại! 👋</h1>
                        <p className="text-indigo-100 text-lg">
                            Tiếp tục hành trình chinh phục từ vựng của bạn hôm nay.
                        </p>
                    </div>
                    <div className="hidden md:block text-6xl">🚀</div>
                </div>

                {/* Quick Stats trong Hero */}
                {!statsLoading && stats && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                        <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-4 text-center">
                            <div className="text-3xl font-bold">{stats.total_vocabularies}</div>
                            <div className="text-indigo-100 text-sm">Tổng từ vựng</div>
                        </div>
                        <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-4 text-center">
                            <div className="text-3xl font-bold text-yellow-300">{stats.due_today}</div>
                            <div className="text-indigo-100 text-sm">Cần ôn hôm nay</div>
                        </div>
                        <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-4 text-center">
                            <div className="text-3xl font-bold text-green-300">{stats.learned}</div>
                            <div className="text-indigo-100 text-sm">Đã thuộc</div>
                        </div>
                        <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-4 text-center">
                            <div className="text-3xl font-bold">{accuracy}%</div>
                            <div className="text-indigo-100 text-sm">Tiến độ</div>
                        </div>
                    </div>
                )}

                {statsLoading && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                        {[...Array(4)].map((_, i) => (
                            <div key={i} className="bg-white/20 backdrop-blur-sm rounded-2xl p-4 text-center animate-pulse">
                                <div className="h-8 bg-white/30 rounded mb-2"></div>
                                <div className="h-4 bg-white/20 rounded w-2/3 mx-auto"></div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Stats Cards Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white rounded-2xl p-6 shadow-lg shadow-gray-100 border border-gray-50 hover:shadow-xl transition-shadow">
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-100">
                            <BookOpen className="text-white" size={28} />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-gray-800">{stats?.total_vocabularies || 0}</div>
                            <div className="text-gray-500 text-sm">Từ đã học</div>
                        </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-50">
                        <div className="flex items-center text-sm text-blue-600">
                            <TrendingUp className="w-4 h-4 mr-1" />
                            <span>Tiếp tục phát triển!</span>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-lg shadow-gray-100 border border-gray-50 hover:shadow-xl transition-shadow">
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-amber-400 rounded-2xl flex items-center justify-center shadow-lg shadow-orange-100">
                            <Calendar className="text-white" size={28} />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-gray-800">{stats?.due_today || 0}</div>
                            <div className="text-gray-500 text-sm">Cần ôn hôm nay</div>
                        </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-50">
                        {stats && stats.due_today > 0 ? (
                            <Link to="/vocabulary/review" className="flex items-center text-sm text-orange-600 hover:text-orange-700">
                                <Target className="w-4 h-4 mr-1" />
                                <span>Ôn tập ngay!</span>
                            </Link>
                        ) : (
                            <span className="flex items-center text-sm text-green-600">
                                <Award className="w-4 h-4 mr-1" />
                                <span>Hoàn thành!</span>
                            </span>
                        )}
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-lg shadow-gray-100 border border-gray-50 hover:shadow-xl transition-shadow">
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-400 rounded-2xl flex items-center justify-center shadow-lg shadow-green-100">
                            <Award className="text-white" size={28} />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-gray-800">{stats?.learned || 0}</div>
                            <div className="text-gray-500 text-sm">Đã thuộc lòng</div>
                        </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-50">
                        <div className="flex items-center text-sm text-green-600">
                            <TrendingUp className="w-4 h-4 mr-1" />
                            <span>Tuyệt vời!</span>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 shadow-lg shadow-gray-100 border border-gray-50 hover:shadow-xl transition-shadow">
                    <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-violet-400 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-100">
                            <Brain className="text-white" size={28} />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-gray-800">{stats?.learning || 0}</div>
                            <div className="text-gray-500 text-sm">Đang học</div>
                        </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-50">
                        <div className="flex items-center text-sm text-purple-600">
                            <Target className="w-4 h-4 mr-1" />
                            <span>Cố gắng lên!</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Progress Bar */}
            {stats && stats.total_vocabularies > 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-lg shadow-gray-100 border border-gray-50">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-gray-800">Tiến độ tổng quan</h3>
                        <span className="text-2xl font-bold text-indigo-600">{accuracy}%</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-4 overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 transition-all duration-1000 ease-out rounded-full"
                            style={{ width: `${accuracy}%` }}
                        />
                    </div>
                    <div className="flex justify-between mt-3 text-sm text-gray-500">
                        <span>Mới bắt đầu</span>
                        <span>Thành thạo</span>
                    </div>
                </div>
            )}

            {/* Quick Actions */}
            <div>
                <h2 className="text-xl font-bold text-gray-800 mb-4">Hành động nhanh</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <Link
                        to="/vocabulary/new"
                        className="group p-6 bg-white border border-gray-100 rounded-2xl hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-50 transition-all"
                    >
                        <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center mb-4 group-hover:bg-indigo-100 group-hover:scale-110 transition-all">
                            <PlusCircle className="text-indigo-600" size={28} />
                        </div>
                        <h3 className="font-bold text-gray-900 mb-2">Thêm từ mới</h3>
                        <p className="text-sm text-gray-500">Mở rộng vốn từ vựng của bạn mỗi ngày.</p>
                    </Link>

                    <Link
                        to="/vocabulary"
                        className="group p-6 bg-white border border-gray-100 rounded-2xl hover:border-blue-200 hover:shadow-xl hover:shadow-blue-50 transition-all"
                    >
                        <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-4 group-hover:bg-blue-100 group-hover:scale-110 transition-all">
                            <BookOpen className="text-blue-600" size={28} />
                        </div>
                        <h3 className="font-bold text-gray-900 mb-2">Kho từ vựng</h3>
                        <p className="text-sm text-gray-500">Quản lý và xem lại danh sách từ đã học.</p>
                    </Link>

                    <Link
                        to="/vocabulary/quiz"
                        className="group p-6 bg-white border border-gray-100 rounded-2xl hover:border-orange-200 hover:shadow-xl hover:shadow-orange-50 transition-all relative overflow-hidden"
                    >
                        <div className="absolute top-2 right-2 px-2 py-1 bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs font-bold rounded-full">
                            HOT
                        </div>
                        <div className="w-14 h-14 bg-orange-50 rounded-2xl flex items-center justify-center mb-4 group-hover:bg-orange-100 group-hover:scale-110 transition-all">
                            <Brain className="text-orange-600" size={28} />
                        </div>
                        <h3 className="font-bold text-gray-900 mb-2">Quiz AI</h3>
                        <p className="text-sm text-gray-500">Trắc nghiệm thông minh với lời giải từ AI.</p>
                    </Link>

                    <Link
                        to="/practice/ai"
                        className="group p-6 bg-white border border-gray-100 rounded-2xl hover:border-purple-200 hover:shadow-xl hover:shadow-purple-50 transition-all"
                    >
                        <div className="w-14 h-14 bg-purple-50 rounded-2xl flex items-center justify-center mb-4 group-hover:bg-purple-100 group-hover:scale-110 transition-all">
                            <MessageSquare className="text-purple-600" size={28} />
                        </div>
                        <h3 className="font-bold text-gray-900 mb-2">AI Practice</h3>
                        <p className="text-sm text-gray-500">Hội thoại cùng AI để ghi nhớ từ vựng.</p>
                    </Link>
                </div>
            </div>

            {/* Review Card - nổi bật nếu có từ cần ôn */}
            {stats && stats.due_today > 0 && (
                <div className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-3xl p-8 text-white shadow-xl shadow-green-100">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-2xl font-bold mb-2">Đến giờ ôn tập rồi! 📚</h3>
                            <p className="text-green-100">
                                Bạn có <span className="font-bold text-yellow-300">{stats.due_today} từ</span> cần ôn tập hôm nay.
                                Đừng bỏ lỡ nhé!
                            </p>
                        </div>
                        <Link
                            to="/vocabulary/review"
                            className="hidden md:flex px-8 py-4 bg-white text-green-600 rounded-2xl font-bold hover:bg-green-50 transition-colors shadow-lg"
                        >
                            Bắt đầu ôn tập
                        </Link>
                    </div>
                    <Link
                        to="/vocabulary/review"
                        className="mt-4 w-full md:hidden flex justify-center px-8 py-4 bg-white text-green-600 rounded-2xl font-bold hover:bg-green-50 transition-colors shadow-lg"
                    >
                        Bắt đầu ôn tập
                    </Link>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
