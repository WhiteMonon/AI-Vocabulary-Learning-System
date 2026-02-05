import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Save, X, Loader2, AlertCircle } from 'lucide-react';
import { VocabularyCreate, VocabularyUpdate, DifficultyLevel, Vocabulary } from '../../types/vocabulary';

interface VocabularyFormProps {
    initialData?: Vocabulary;
    onSubmit: (data: any) => Promise<void>;
    isLoading: boolean;
    title: string;
}

const VocabularyForm: React.FC<VocabularyFormProps> = ({
    initialData,
    onSubmit,
    isLoading,
    title
}) => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState<VocabularyCreate>({
        word: '',
        definition: '',
        example_sentence: '',
        difficulty_level: DifficultyLevel.MEDIUM,
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        if (initialData) {
            setFormData({
                word: initialData.word,
                definition: initialData.definition,
                example_sentence: initialData.example_sentence || '',
                difficulty_level: initialData.difficulty_level,
            });
        }
    }, [initialData]);

    const validate = () => {
        const newErrors: Record<string, string> = {};
        if (!formData.word.trim()) newErrors.word = 'Từ vựng không được để trống';
        if (!formData.definition.trim()) newErrors.definition = 'Định nghĩa không được để trống';
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!validate()) return;

        try {
            await onSubmit(formData);
            navigate('/vocabulary');
        } catch (error) {
            console.error('Submit error:', error);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (errors[name]) {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[name];
                return newErrors;
            });
        }
    };

    return (
        <div className="max-w-2xl mx-auto px-4 py-8">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-600 to-violet-600 px-8 py-6">
                    <h1 className="text-2xl font-bold text-white">{title}</h1>
                    <p className="text-indigo-100">Điền thông tin chi tiết về từ vựng của bạn</p>
                </div>

                <form onSubmit={handleSubmit} className="p-8 space-y-6">
                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Từ vựng <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            name="word"
                            placeholder="Ví dụ: Ephemeral"
                            className={`w-full px-4 py-3 border rounded-xl outline-none transition-all focus:ring-2 ${errors.word
                                    ? 'border-red-300 focus:ring-red-100'
                                    : 'border-gray-200 focus:ring-indigo-100 focus:border-indigo-500'
                                }`}
                            value={formData.word}
                            onChange={handleChange}
                        />
                        {errors.word && (
                            <p className="mt-1 text-sm text-red-600 flex items-center">
                                <AlertCircle className="w-4 h-4 mr-1" />
                                {errors.word}
                            </p>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Định nghĩa <span className="text-red-500">*</span>
                        </label>
                        <textarea
                            name="definition"
                            rows={3}
                            placeholder="Nhập định nghĩa của từ..."
                            className={`w-full px-4 py-3 border rounded-xl outline-none transition-all focus:ring-2 ${errors.definition
                                    ? 'border-red-300 focus:ring-red-100'
                                    : 'border-gray-200 focus:ring-indigo-100 focus:border-indigo-500'
                                }`}
                            value={formData.definition}
                            onChange={handleChange}
                        />
                        {errors.definition && (
                            <p className="mt-1 text-sm text-red-600 flex items-center">
                                <AlertCircle className="w-4 h-4 mr-1" />
                                {errors.definition}
                            </p>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Câu ví dụ
                        </label>
                        <textarea
                            name="example_sentence"
                            rows={2}
                            placeholder="Nhập câu ví dụ để dễ ghi nhớ hơn..."
                            className="w-full px-4 py-3 border border-gray-200 rounded-xl outline-none transition-all focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
                            value={formData.example_sentence}
                            onChange={handleChange}
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Độ khó
                            </label>
                            <select
                                name="difficulty_level"
                                className="w-full px-4 py-3 border border-gray-200 rounded-xl outline-none transition-all focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500 appearance-none bg-white font-medium"
                                value={formData.difficulty_level}
                                onChange={handleChange}
                            >
                                <option value={DifficultyLevel.EASY}>Dễ (Easy)</option>
                                <option value={DifficultyLevel.MEDIUM}>Trung bình (Medium)</option>
                                <option value={DifficultyLevel.HARD}>Khó (Hard)</option>
                            </select>
                        </div>
                    </div>

                    <div className="flex items-center justify-end space-x-4 pt-6 border-t border-gray-100">
                        <button
                            type="button"
                            onClick={() => navigate('/vocabulary')}
                            className="px-6 py-2.5 text-gray-600 font-semibold hover:bg-gray-50 rounded-xl transition-colors flex items-center"
                        >
                            <X className="w-5 h-5 mr-2" />
                            Hủy bỏ
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="px-8 py-2.5 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                            ) : (
                                <Save className="w-5 h-5 mr-2" />
                            )}
                            {initialData ? 'Cập nhật' : 'Lưu từ vựng'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default VocabularyForm;
