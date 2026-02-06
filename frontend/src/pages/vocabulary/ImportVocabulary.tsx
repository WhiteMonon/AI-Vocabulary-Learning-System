import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, AlertCircle, CheckCircle, Loader2, XCircle } from 'lucide-react';
import { ImportResultResponse } from '../../types/vocabulary';

interface ProcessedItem {
    word: string;
    status: 'success' | 'failed' | 'warning';
    message: string;
}

interface ProgressData {
    current: number;
    total: number;
    percent: number;
}

const ImportVocabulary: React.FC = () => {
    const navigate = useNavigate();
    const [content, setContent] = useState('');
    const [autoFetch, setAutoFetch] = useState(true);
    const [isStreaming, setIsStreaming] = useState(false);
    const [result, setResult] = useState<ImportResultResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Streaming states
    const [progress, setProgress] = useState<ProgressData>({ current: 0, total: 0, percent: 0 });
    const [processedItems, setProcessedItems] = useState<ProcessedItem[]>([]);
    const eventSourceRef = useRef<EventSource | null>(null);
    const logContainerRef = useRef<HTMLDivElement | null>(null);
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    const handleImportStream = async () => {
        if (!content.trim()) {
            setError('Vui lòng nhập nội dung để import');
            return;
        }

        setIsStreaming(true);
        setError(null);
        setResult(null);
        setProgress({ current: 0, total: 0, percent: 0 });
        setProcessedItems([]);

        try {
            // Tạo request body
            const requestBody = {
                content,
                auto_fetch_meaning: autoFetch
            };

            // Gọi API với fetch để lấy stream
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/v1/vocabulary/import-stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) {
                throw new Error('No response body');
            }

            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (!line.trim()) continue;

                    const eventMatch = line.match(/^event: (.+)$/m);
                    const dataMatch = line.match(/^data: (.+)$/m);

                    if (eventMatch && dataMatch) {
                        const eventType = eventMatch[1];
                        const eventData = JSON.parse(dataMatch[1]);

                        handleSSEEvent(eventType, eventData);
                    }
                }
            }

        } catch (err: any) {
            console.error('Import stream failed:', err);
            setError(err.message || 'Import thất bại. Vui lòng thử lại.');
        } finally {
            setIsStreaming(false);
        }
    };

    const handleSSEEvent = (eventType: string, data: any) => {
        switch (eventType) {
            case 'progress':
                setProgress(data);
                break;

            case 'item_processed':
                setProcessedItems(prev => [...prev, data]);
                // Auto-scroll to bottom
                setTimeout(() => {
                    if (logContainerRef.current) {
                        logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
                    }
                }, 50);
                break;

            case 'completed':
                setResult(data);
                setContent('');
                break;

            case 'error':
                setError(data.message || 'Có lỗi xảy ra');
                break;
        }
    };

    const handleCancel = () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
        setIsStreaming(false);
        setError('Import đã bị hủy');
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'success':
                return <CheckCircle className="w-4 h-4 text-green-600" />;
            case 'failed':
                return <XCircle className="w-4 h-4 text-red-600" />;
            case 'warning':
                return <AlertCircle className="w-4 h-4 text-amber-600" />;
            default:
                return null;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'success':
                return 'bg-green-50 border-green-200 text-green-800';
            case 'failed':
                return 'bg-red-50 border-red-200 text-red-800';
            case 'warning':
                return 'bg-amber-50 border-amber-200 text-amber-800';
            default:
                return 'bg-gray-50 border-gray-200 text-gray-800';
        }
    };

    const successCount = processedItems.filter(i => i.status === 'success').length;
    const failedCount = processedItems.filter(i => i.status === 'failed').length;
    const warningCount = processedItems.filter(i => i.status === 'warning').length;

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
                            disabled={isStreaming}
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
                            disabled={isStreaming}
                        />
                        <label htmlFor="autoFetch" className="text-gray-700 font-medium cursor-pointer select-none">
                            Tự động tìm nghĩa và ví dụ cho từ mới (AI)
                        </label>
                    </div>

                    {/* Progress Bar */}
                    {isStreaming && (
                        <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100 rounded-xl p-6 animate-in fade-in slide-in-from-top-2">
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <Loader2 className="w-5 h-5 text-emerald-600 animate-spin" />
                                    <span className="font-bold text-emerald-800">Đang xử lý...</span>
                                </div>
                                <span className="text-2xl font-bold text-emerald-600">{progress.percent}%</span>
                            </div>

                            <div className="w-full bg-emerald-100 rounded-full h-3 overflow-hidden mb-3">
                                <div
                                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 transition-all duration-300 ease-out"
                                    style={{ width: `${progress.percent}%` }}
                                />
                            </div>

                            <div className="flex items-center justify-between text-sm text-emerald-700">
                                <span>{progress.current} / {progress.total} từ</span>
                                <div className="flex items-center gap-4">
                                    <span className="flex items-center gap-1">
                                        <CheckCircle className="w-4 h-4 text-green-600" />
                                        {successCount}
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <AlertCircle className="w-4 h-4 text-amber-600" />
                                        {warningCount}
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <XCircle className="w-4 h-4 text-red-600" />
                                        {failedCount}
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Live Log */}
                    {processedItems.length > 0 && (
                        <div className="border border-gray-200 rounded-xl overflow-hidden">
                            <div className="bg-gray-50 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
                                <span className="text-sm font-bold text-gray-700">Chi tiết xử lý</span>
                                <span className="text-xs text-gray-500">{processedItems.length} items</span>
                            </div>
                            <div
                                ref={logContainerRef}
                                className="max-h-64 overflow-y-auto p-4 space-y-2 bg-gray-50"
                            >
                                {processedItems.map((item, index) => (
                                    <div
                                        key={index}
                                        className={`flex items-start gap-3 p-3 rounded-lg border text-sm ${getStatusColor(item.status)}`}
                                    >
                                        {getStatusIcon(item.status)}
                                        <div className="flex-1 min-w-0">
                                            <div className="font-bold truncate">{item.word}</div>
                                            <div className="text-xs opacity-80 truncate">{item.message}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

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
                                Hoàn thành Import!
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
                            disabled={isStreaming}
                        >
                            Quay lại
                        </button>

                        {isStreaming ? (
                            <button
                                onClick={handleCancel}
                                className="px-8 py-2.5 bg-red-600 text-white font-bold rounded-xl hover:bg-red-700 transition-all shadow-lg shadow-red-200 flex items-center"
                            >
                                <XCircle className="w-5 h-5 mr-2" />
                                Hủy Import
                            </button>
                        ) : (
                            <button
                                onClick={handleImportStream}
                                disabled={!content.trim()}
                                className="px-8 py-2.5 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                            >
                                <Upload className="w-5 h-5 mr-2" />
                                Tiến hành Import
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ImportVocabulary;
