import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { importVocabulary } from '../../api/vocabulary';
import { ImportResultResponse } from '../../types/vocabulary';

const ImportVocabulary: React.FC = () => {
    const navigate = useNavigate();
    const [content, setContent] = useState('');
    const [autoFetch, setAutoFetch] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<ImportResultResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleImport = async () => {
        if (!content.trim()) {
            setError('Vui lòng nhập nội dung để import');
            return;
        }

        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await importVocabulary({
                content,
                auto_fetch_meaning: autoFetch
            });
            setResult(response);
            if (response.total_processed > 0) {
                setContent('');
            }
        } catch (err: any) {
            console.error('Import failed:', err);
            setError(err.response?.data?.detail || 'Import thất bại. Vui lòng thử lại.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-8 py-6">
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Upload className="w-6 h-6" />
                        Import Từ Vựng
                    </h1>
                    <p className="text-emerald-50">Thêm nhiều từ vựng cùng lúc từ văn bản</p>
                </div>

                <div className="p-8 space-y-6">
                    {/* Instructions */}
                    <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-blue-800">
                        <h3 className="font-bold flex items-center gap-2 mb-2">
                            <FileText className="w-4 h-4" />
                            Định dạng hỗ trợ:
                        </h3>
                        <ul className="list-disc list-inside space-y-1 ml-1 opacity-90">
                            <li>Mỗi từ một dòng</li>
                            <li>Format: <code>word</code> hoặc <code>word|definition</code> hoặc <code>word|definition|example</code></li>
                            <li>Nếu chỉ nhập <code>word</code>, hệ thống sẽ tự động tìm nghĩa (nếu bật tính năng)</li>
                        </ul>
                    </div>

                    {/* Input Area */}
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Nội dung Import
                        </label>
                        <textarea
                            rows={10}
                            className="w-full px-4 py-3 border border-gray-200 rounded-xl outline-none transition-all focus:ring-2 focus:ring-emerald-100 focus:border-emerald-500 font-mono text-sm"
                            placeholder={"apple\nbanana|quả chuối\ncomputer|máy tính|I use computer everyday"}
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                        />
                    </div>

                    {/* Options */}
                    <div className="flex items-center gap-3">
                        <input
                            type="checkbox"
                            id="autoFetch"
                            className="w-5 h-5 text-emerald-600 rounded focus:ring-emerald-500 border-gray-300"
                            checked={autoFetch}
                            onChange={(e) => setAutoFetch(e.target.checked)}
                        />
                        <label htmlFor="autoFetch" className="text-gray-700 font-medium cursor-pointer select-none">
                            Tự động tìm nghĩa và ví dụ cho từ mới (AI)
                        </label>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="bg-red-50 text-red-600 p-4 rounded-xl flex items-center gap-3 animate-in fade-in slide-in-from-top-2">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            {error}
                        </div>
                    )}

                    {/* Success Result */}
                    {result && (
                        <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-6 animate-in fade-in slide-in-from-top-2">
                            <h3 className="text-lg font-bold text-emerald-800 mb-4 flex items-center gap-2">
                                <CheckCircle className="w-5 h-5" />
                                Kết quả Import
                            </h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                                <div className="bg-white p-3 rounded-lg border border-emerald-100 shadow-sm">
                                    <div className="text-xs text-emerald-600 uppercase font-bold">Đã xử lý</div>
                                    <div className="text-2xl font-bold text-gray-800">{result.total_processed}</div>
                                </div>
                                <div className="bg-white p-3 rounded-lg border border-emerald-100 shadow-sm">
                                    <div className="text-xs text-emerald-600 uppercase font-bold">Từ mới</div>
                                    <div className="text-2xl font-bold text-gray-800">{result.new_words}</div>
                                </div>
                                <div className="bg-white p-3 rounded-lg border border-emerald-100 shadow-sm">
                                    <div className="text-xs text-emerald-600 uppercase font-bold">Ghép nghĩa</div>
                                    <div className="text-2xl font-bold text-gray-800">{result.merged_meanings}</div>
                                </div>
                                <div className="bg-white p-3 rounded-lg border border-emerald-100 shadow-sm">
                                    <div className="text-xs text-emerald-600 uppercase font-bold">AI Tạo</div>
                                    <div className="text-2xl font-bold text-gray-800">{result.auto_generated_count}</div>
                                </div>
                            </div>


                            {result.failed_auto_meaning && result.failed_auto_meaning.length > 0 && (
                                <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-4">
                                    <div className="text-sm font-bold text-amber-800 mb-2 flex items-center gap-2">
                                        <AlertCircle className="w-4 h-4" />
                                        Từ không tìm thấy nghĩa ({result.failed_auto_meaning.length})
                                    </div>
                                    <div className="text-xs text-amber-700 mb-2">
                                        Các từ sau đã được thêm vào danh sách nhưng chưa có nghĩa. Bạn có thể thêm nghĩa thủ công sau.
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {result.failed_auto_meaning.map((word, i) => (
                                            <span key={i} className="bg-amber-100 text-amber-800 text-xs px-2 py-1 rounded-full font-medium">{word}</span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {result.errors.length > 0 && (
                                <div className="mt-4">
                                    <div className="text-sm font-bold text-red-700 mb-1">Lỗi chi tiết:</div>
                                    <ul className="list-disc list-inside text-sm text-red-600 max-h-40 overflow-y-auto">
                                        {result.errors.map((err, i) => (
                                            <li key={i}>{err}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            <div className="mt-6 flex justify-end">
                                <button
                                    onClick={() => navigate('/vocabulary')}
                                    className="text-emerald-700 font-semibold hover:text-emerald-800"
                                >
                                    Xem danh sách từ vựng &rarr;
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center justify-end gap-4 border-t border-gray-100 pt-6">
                        <button
                            onClick={() => navigate('/vocabulary')}
                            className="px-6 py-2.5 text-gray-600 font-medium hover:bg-gray-50 rounded-xl transition-colors"
                        >
                            Quay lại
                        </button>
                        <button
                            onClick={handleImport}
                            disabled={isLoading || !content.trim()}
                            className="px-8 py-2.5 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                            ) : (
                                <Upload className="w-5 h-5 mr-2" />
                            )}
                            Tiến hành Import
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ImportVocabulary;
