import React from 'react';

const Dashboard: React.FC = () => {
    return (
        <div className="bg-white p-6 rounded-lg shadow-sm">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Chào mừng đến với AI Vocab!</h1>
            <p className="text-gray-600">
                Bắt đầu học từ vựng mới và luyện tập cùng AI ngay hôm nay.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <div className="p-4 border rounded-md hover:border-blue-500 transition-colors cursor-pointer">
                    <h3 className="font-semibold mb-2">Học từ mới</h3>
                    <p className="text-sm text-gray-500">Thêm từ vựng mới vào kho kiến thức của bạn.</p>
                </div>
                <div className="p-4 border rounded-md hover:border-blue-500 transition-colors cursor-pointer">
                    <h3 className="font-semibold mb-2">Luyện tập (SRS)</h3>
                    <p className="text-sm text-gray-500">Ôn tập các từ vựng theo thuật toán SRS.</p>
                </div>
                <div className="p-4 border rounded-md hover:border-blue-500 transition-colors cursor-pointer">
                    <h3 className="font-semibold mb-2">AI Practice</h3>
                    <p className="text-sm text-gray-500">Tạo câu hỏi và hội thoại cùng AI.</p>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
