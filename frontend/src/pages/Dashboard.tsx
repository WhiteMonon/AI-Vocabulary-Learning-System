import React from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, BookOpen, Brain, MessageSquare } from 'lucide-react';

const Dashboard: React.FC = () => {
    return (
        <div className="bg-white p-6 rounded-lg shadow-sm">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Chào mừng đến với AI Vocab!</h1>
            <p className="text-gray-600">
                Bắt đầu học từ vựng mới và luyện tập cùng AI ngay hôm nay.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
                <Link to="/vocabulary/new" className="p-6 border rounded-xl hover:border-indigo-500 hover:shadow-md transition-all group bg-white">
                    <div className="w-12 h-12 bg-indigo-50 rounded-lg flex items-center justify-center mb-4 group-hover:bg-indigo-100 transition-colors">
                        <PlusCircle className="text-indigo-600" size={24} />
                    </div>
                    <h3 className="font-bold text-gray-900 mb-2">Thêm từ mới</h3>
                    <p className="text-sm text-gray-500">Thêm từ vựng mới vào kho kiến thức của bạn.</p>
                </Link>

                <Link to="/vocabulary" className="p-6 border rounded-xl hover:border-blue-500 hover:shadow-md transition-all group bg-white">
                    <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-100 transition-colors">
                        <BookOpen className="text-blue-600" size={24} />
                    </div>
                    <h3 className="font-bold text-gray-900 mb-2">Kho từ vựng</h3>
                    <p className="text-sm text-gray-500">Quản lý và theo dõi danh sách từ đã học.</p>
                </Link>

                <Link to="/vocabulary/review" className="p-6 border rounded-xl hover:border-green-500 hover:shadow-md transition-all group bg-white cursor-pointer">
                    <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center mb-4 group-hover:bg-green-100 transition-colors">
                        <Brain className="text-green-600" size={24} />
                    </div>
                    <h3 className="font-bold text-gray-900 mb-2">Ôn tập (SRS)</h3>
                    <p className="text-sm text-gray-500">Học theo thuật toán lặp lại ngắt quãng (SM-2).</p>
                </Link>

                <Link to="/vocabulary/quiz" className="p-6 border rounded-xl hover:border-orange-500 hover:shadow-md transition-all group bg-white cursor-pointer ring-offset-2 ring-orange-500/20 hover:ring-4">
                    <div className="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center mb-4 group-hover:bg-orange-100 transition-colors">
                        <Brain className="text-orange-600" size={24} />
                    </div>
                    <h3 className="font-bold text-gray-900 mb-2">Quiz AI (Hot)</h3>
                    <p className="text-sm text-gray-500">Trắc nghiệm thông minh với lời giải chi tiết từ AI.</p>
                </Link>

                <Link to="/practice/ai" className="p-6 border rounded-xl hover:border-purple-500 hover:shadow-md transition-all group bg-white cursor-pointer">
                    <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center mb-4 group-hover:bg-purple-100 transition-colors">
                        <MessageSquare className="text-purple-600" size={24} />
                    </div>
                    <h3 className="font-bold text-gray-900 mb-2">AI Practice</h3>
                    <p className="text-sm text-gray-500">Hội thoại cùng AI để ghi nhớ từ vựng lâu hơn.</p>
                </Link>
            </div>
        </div>
    );
};

export default Dashboard;
