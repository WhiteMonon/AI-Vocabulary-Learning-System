import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, Filter, ArrowLeft, Clock } from 'lucide-react';

// Định nghĩa kiểu dữ liệu cho kết quả ôn tập
export interface ReviewResultItem {
    id: number;
    word: string;
    definition: string;
    userAnswer: string;
    isCorrect: boolean;
    timeSpent: number;
}

type FilterType = 'all' | 'correct' | 'incorrect';

const ReviewResults: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [filter, setFilter] = useState<FilterType>('all');

    // Lấy kết quả từ state được truyền qua navigation
    const results: ReviewResultItem[] = location.state?.results || [];
    const totalTime: number = location.state?.totalTime || 0;

    // Tính toán thống kê
    const totalQuestions = results.length;
    const correctCount = results.filter(r => r.isCorrect).length;
    const incorrectCount = totalQuestions - correctCount;
    const accuracy = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;

    // Format thời gian
    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return mins > 0 ? `${mins} phút ${secs} giây` : `${secs} giây`;
    };

    // Filter kết quả
    const filteredResults = results.filter(result => {
        if (filter === 'correct') return result.isCorrect;
        if (filter === 'incorrect') return !result.isCorrect;
        return true;
    });

    // Nếu không có kết quả, hiển thị trạng thái trống
    if (results.length === 0) {
        return (
            <div className="max-w-2xl mx-auto py-12 px-4">
                <div className="bg-white rounded-3xl shadow-xl p-10 text-center">
                    <div className="text-6xl mb-6">📝</div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-4">Chưa có kết quả</h2>
                    <p className="text-gray-600 mb-8">
                        Bạn chưa hoàn thành phiên ôn tập nào. Hãy bắt đầu ôn tập để xem kết quả!
                    </p>
                    <button
                        onClick={() => navigate('/vocabulary/review')}
                        className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition-all"
                    >
                        Bắt đầu ôn tập
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto py-8 px-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <button
                    onClick={() => navigate('/')}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                    <ArrowLeft className="w-5 h-5" />
                    <span className="font-medium">Quay lại Dashboard</span>
                </button>
            </div>

            {/* Stats Overview */}
            <div className="bg-white rounded-3xl shadow-xl shadow-indigo-100/50 border border-indigo-50 overflow-hidden mb-8">
                <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-8 text-white">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold mb-2">Kết quả ôn tập</h1>
                            <p className="text-indigo-100">Bạn đã hoàn thành phiên ôn tập xuất sắc!</p>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                            <div className="flex items-center gap-2 bg-white/20 px-4 py-2 rounded-xl">
                                <Clock className="w-5 h-5" />
                                <span className="font-medium">{formatTime(totalTime)}</span>
                            </div>
                            <div className="px-4 py-1 bg-yellow-400 text-yellow-900 rounded-lg font-bold text-sm shadow-sm">
                                Score: {location.state?.score || 0}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6">
                    <div className="bg-gray-50 rounded-2xl p-4 text-center">
                        <div className="text-3xl font-bold text-gray-800">{totalQuestions}</div>
                        <div className="text-sm text-gray-500 mt-1">Tổng số câu</div>
                    </div>
                    <div className="bg-green-50 rounded-2xl p-4 text-center">
                        <div className="text-3xl font-bold text-green-600">{correctCount}</div>
                        <div className="text-sm text-green-600 mt-1">Đúng</div>
                    </div>
                    <div className="bg-red-50 rounded-2xl p-4 text-center">
                        <div className="text-3xl font-bold text-red-600">{incorrectCount}</div>
                        <div className="text-sm text-red-600 mt-1">Sai</div>
                    </div>
                    <div className="bg-indigo-50 rounded-2xl p-4 text-center">
                        <div className="text-3xl font-bold text-indigo-600">{accuracy}%</div>
                        <div className="text-sm text-indigo-600 mt-1">Độ chính xác</div>
                    </div>
                </div>

                {/* Accuracy Bar */}
                <div className="px-6 pb-6">
                    <div className="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-700"
                            style={{ width: `${accuracy}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Weak Words Section (Only if there are incorrect answers) */}
            {incorrectCount > 0 && (
                <div className="mb-8">
                    <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <span className="text-2xl">💪</span> Cần ôn tập thêm
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {results.filter(r => !r.isCorrect).map(r => (
                            <div key={r.id} className="bg-red-50 border border-red-100 p-4 rounded-xl flex justify-between items-center">
                                <div>
                                    <div className="font-bold text-gray-800 text-lg">{r.word}</div>
                                    <div className="text-sm text-gray-600">{r.definition}</div>
                                </div>
                                <button className="text-xs bg-white text-red-600 px-3 py-1 rounded-lg border border-red-200 font-bold uppercase">
                                    Review
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Filter */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 text-gray-600">
                        <Filter className="w-5 h-5" />
                        <span className="font-medium">Chi tiết:</span>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setFilter('all')}
                            className={`px-4 py-2 rounded-xl font-medium transition-all ${filter === 'all'
                                ? 'bg-indigo-600 text-white'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                        >
                            Tất cả
                        </button>
                        <button
                            onClick={() => setFilter('correct')}
                            className={`px-4 py-2 rounded-xl font-medium transition-all ${filter === 'correct'
                                ? 'bg-green-600 text-white'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                        >
                            Đúng
                        </button>
                        <button
                            onClick={() => setFilter('incorrect')}
                            className={`px-4 py-2 rounded-xl font-medium transition-all ${filter === 'incorrect'
                                ? 'bg-red-600 text-white'
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                }`}
                        >
                            Sai
                        </button>
                    </div>
                </div>
            </div>

            {/* Results List */}
            <div className="space-y-4">
                {filteredResults.map((result, index) => (
                    <div
                        key={result.id}
                        className={`bg-white rounded-2xl shadow-sm border p-6 transition-all hover:shadow-md ${result.isCorrect ? 'border-green-100' : 'border-red-100'
                            }`}
                    >
                        <div className="flex items-start justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                    <span className="text-sm font-medium text-gray-400">#{index + 1}</span>
                                    <h3 className="text-xl font-bold text-gray-800">{result.word}</h3>
                                    {result.isCorrect ? (
                                        <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold flex items-center gap-1">
                                            <CheckCircle className="w-3 h-3" />
                                            Đúng
                                        </span>
                                    ) : (
                                        <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold flex items-center gap-1">
                                            <XCircle className="w-3 h-3" />
                                            Sai
                                        </span>
                                    )}
                                </div>
                                <p className="text-gray-600 mb-3">{result.definition}</p>
                                <div className="flex items-center gap-4 text-sm">
                                    <div className="text-gray-500">
                                        <span className="font-medium">Câu trả lời của bạn:</span>{' '}
                                        <span className={result.isCorrect ? 'text-green-600 font-semibold' : 'text-red-600 line-through'}>
                                            {result.userAnswer || '(không trả lời)'}
                                        </span>
                                    </div>
                                    {!result.isCorrect && (
                                        <div className="text-gray-500">
                                            <span className="font-medium">Đáp án đúng:</span>{' '}
                                            <span className="text-green-600 font-semibold">{result.word}</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div className="text-right text-sm text-gray-400">
                                {result.timeSpent}s
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Empty filter state */}
            {filteredResults.length === 0 && (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
                    <div className="text-5xl mb-4">🔍</div>
                    <p className="text-gray-600">Không có kết quả phù hợp với bộ lọc</p>
                </div>
            )}

            {/* Footer Actions */}
            <div className="mt-8 flex justify-center gap-4">
                <button
                    onClick={() => navigate('/vocabulary/review')}
                    className="px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200"
                >
                    Ôn tập tiếp
                </button>
                <button
                    onClick={() => navigate('/')}
                    className="px-8 py-3 bg-gray-100 text-gray-700 rounded-xl font-bold hover:bg-gray-200 transition-all"
                >
                    Về Dashboard
                </button>
            </div>
        </div>
    );
};

export default ReviewResults;
