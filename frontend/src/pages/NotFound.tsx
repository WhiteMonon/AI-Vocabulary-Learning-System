import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
            <div className="text-center">
                <h1 className="text-6xl font-bold text-blue-600">404</h1>
                <p className="text-2xl font-medium text-gray-900 mt-4">Không tìm thấy trang</p>
                <p className="text-gray-600 mt-2">Trang bạn đang tìm kiếm không tồn tại hoặc đã bị di chuyển.</p>
                <Link
                    to="/"
                    className="mt-6 inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
                >
                    Quay lại trang chủ
                </Link>
            </div>
        </div>
    );
};

export default NotFound;
