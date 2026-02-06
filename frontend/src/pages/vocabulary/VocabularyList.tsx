import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
    Plus,
    Search,
    Edit,
    Trash2,
    Filter,
    Loader2,
    BookOpen,
    Upload // Add Upload icon
} from 'lucide-react';
import { useVocabularies, useDeleteVocabulary } from '../../hooks/useVocabulary';
import SmartPagination from '../../components/common/SmartPagination';

const VocabularyList: React.FC = () => {
    const [filters, setFilters] = useState({
        page: 1,
        page_size: 10,
        search: '',
        status: undefined as 'LEARNED' | 'LEARNING' | 'DUE' | undefined,
    });

    const { data, isLoading, isError, refetch } = useVocabularies(filters);
    const deleteMutation = useDeleteVocabulary();

    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFilters(prev => ({ ...prev, search: e.target.value, page: 1 }));
    };


    const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const value = e.target.value as any;
        setFilters(prev => ({ ...prev, status: value === '' ? undefined : value, page: 1 }));
    };

    const handlePageChange = (newPage: number) => {
        setFilters(prev => ({ ...prev, page: newPage }));
    };

    const handleDelete = async (id: number) => {
        if (window.confirm('Bạn có chắc chắn muốn xóa từ vựng này không?')) {
            try {
                await deleteMutation.mutateAsync(id);
            } catch (error) {
                alert('Có lỗi xảy ra khi xóa từ vựng');
            }
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Danh sách từ vựng</h1>
                    <p className="text-gray-600 mt-1">Quản lý và theo dõi tiến độ học tập của bạn</p>
                </div>
                <div className="flex gap-2">
                    <Link
                        to="/vocabulary/import"
                        className="inline-flex items-center px-4 py-2 bg-emerald-600 text-white font-semibold rounded-lg hover:bg-emerald-700 transition-colors"
                    >
                        <Upload className="w-5 h-5 mr-2" />
                        Import
                    </Link>
                    <Link
                        to="/vocabulary/new"
                        className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                        <Plus className="w-5 h-5 mr-2" />
                        Thêm từ mới
                    </Link>
                </div>
            </div>

            {/* Filters */}
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                            type="text"
                            placeholder="Tìm kiếm từ hoặc nghĩa..."
                            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                            value={filters.search}
                            onChange={handleSearchChange}
                        />
                    </div>
                    <div>
                        <select
                            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all appearance-none"
                            value={filters.status || ''}
                            onChange={handleStatusChange}
                        >
                            <option value="">Tất cả trạng thái</option>
                            <option value="LEARNING">Đang học</option>
                            <option value="LEARNED">Đã thuộc</option>
                            <option value="DUE">Cần ôn tập</option>
                        </select>
                    </div>
                    <div className="flex items-center justify-end">
                        <button
                            onClick={() => refetch()}
                            className="p-2 text-gray-500 hover:text-indigo-600 transition-colors"
                            title="Làm mới"
                        >
                            <Filter className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Content */}
            {isLoading ? (
                <div className="flex flex-col items-center justify-center py-20">
                    <Loader2 className="w-10 h-10 text-indigo-600 animate-spin mb-4" />
                    <p className="text-gray-500">Đang tải danh sách từ vựng...</p>
                </div>
            ) : isError ? (
                <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg text-center">
                    Có lỗi xảy ra khi tải dữ liệu. Vui lòng thử lại sau.
                </div>
            ) : data?.items.length === 0 ? (
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
                    <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Không tìm thấy từ vựng nào</h3>
                    <p className="text-gray-500 mb-6">Bắt đầu hành trình học tập bằng cách thêm những từ vựng đầu tiên!</p>
                    <Link
                        to="/vocabulary/new"
                        className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                        <Plus className="w-5 h-5 mr-2" />
                        Thêm từ vựng đầu tiên
                    </Link>
                </div>
            ) : (
                <>
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-gray-50 border-b border-gray-100">
                                    <tr>
                                        <th className="px-6 py-4 text-sm font-semibold text-gray-600">Từ vựng</th>
                                        <th className="px-6 py-4 text-sm font-semibold text-gray-600">Định nghĩa</th>
                                        <th className="px-6 py-4 text-sm font-semibold text-gray-600 text-right">Thao tác</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                    {data?.items.map((item) => (
                                        <tr key={item.id} className="hover:bg-gray-50 transition-colors group">
                                            <td className="px-6 py-4">
                                                <div className="font-bold text-gray-900 text-lg">{item.word}</div>
                                                {/* Display first example sentence if exists */}
                                                {item.meanings?.[0]?.example_sentence && (
                                                    <div className="text-sm text-gray-500 italic mt-1 line-clamp-1">
                                                        "{item.meanings[0].example_sentence}"
                                                    </div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 text-gray-600">
                                                {/* Display first definition */}
                                                {item.meanings?.[0]?.definition}
                                                {item.meanings?.length > 1 && (
                                                    <span className="text-xs text-gray-400 ml-2">
                                                        (+{item.meanings.length - 1} khác)
                                                    </span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <div className="flex items-center justify-end space-x-2">
                                                    <Link
                                                        to={`/vocabulary/${item.id}/edit`}
                                                        className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                                                        title="Chỉnh sửa"
                                                    >
                                                        <Edit className="w-5 h-5" />
                                                    </Link>
                                                    <button
                                                        onClick={() => handleDelete(item.id)}
                                                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                                                        title="Xóa"
                                                    >
                                                        <Trash2 className="w-5 h-5" />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Pagination and Footer Controls */}
                    {data && (
                        <div className="flex flex-col md:flex-row items-center justify-between mt-6 gap-4 border-t border-gray-100 pt-6">
                            <div className="flex items-center text-sm text-gray-600 gap-2 order-2 md:order-1">
                                <span>Hiển thị</span>
                                <select
                                    value={filters.page_size}
                                    onChange={(e) => setFilters(prev => ({ ...prev, page_size: Number(e.target.value), page: 1 }))}
                                    className="border border-gray-200 rounded px-2 py-1 focus:ring-2 focus:ring-indigo-500 outline-none bg-white font-medium text-gray-900"
                                >
                                    <option value={10}>10</option>
                                    <option value={20}>20</option>
                                    <option value={50}>50</option>
                                    <option value={100}>100</option>
                                </select>
                                <span>/ trang</span>
                                <span className="hidden sm:inline px-2 text-gray-300">|</span>
                                <span className="hidden sm:inline">
                                    Tổng <span className="font-medium text-gray-900">{data.total}</span> từ vựng
                                </span>
                            </div>

                            <div className="order-1 md:order-2">
                                <SmartPagination
                                    currentPage={filters.page}
                                    totalPages={data.total_pages}
                                    onPageChange={handlePageChange}
                                />
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default VocabularyList;
