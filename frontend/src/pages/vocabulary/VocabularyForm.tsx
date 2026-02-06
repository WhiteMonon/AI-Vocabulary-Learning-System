import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Save, X, Loader2, AlertCircle, Plus, Trash2 } from 'lucide-react';
import { VocabularyCreate, Vocabulary } from '../../types/vocabulary';

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
        meanings: [{ definition: '', example_sentence: '' }]
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        if (initialData) {
            setFormData({
                word: initialData.word,
                meanings: initialData.meanings.map(m => ({
                    definition: m.definition,
                    example_sentence: m.example_sentence || ''
                })),
            });
        }
    }, [initialData]);

    const validate = () => {
        const newErrors: Record<string, string> = {};
        if (!formData.word.trim()) newErrors.word = 'Từ vựng không được để trống';

        formData.meanings.forEach((meaning, index) => {
            if (!meaning.definition.trim()) {
                newErrors[`definition_${index}`] = 'Định nghĩa không được để trống';
            }
        });

        if (formData.meanings.length === 0) {
            newErrors.meanings = 'Phải có ít nhất một ý nghĩa';
        }

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

    const handleWordChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
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

    const handleMeaningChange = (index: number, field: 'definition' | 'example_sentence', value: string) => {
        setFormData(prev => {
            const newMeanings = [...prev.meanings];
            newMeanings[index] = { ...newMeanings[index], [field]: value };
            return { ...prev, meanings: newMeanings };
        });

        if (errors[`definition_${index}`] && field === 'definition') {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[`definition_${index}`];
                return newErrors;
            });
        }
    };

    const addMeaning = () => {
        setFormData(prev => ({
            ...prev,
            meanings: [...prev.meanings, { definition: '', example_sentence: '' }]
        }));
    };

    const removeMeaning = (index: number) => {
        if (formData.meanings.length <= 1) return;
        setFormData(prev => ({
            ...prev,
            meanings: prev.meanings.filter((_, i) => i !== index)
        }));
    };

    return (
        <div className="max-w-3xl mx-auto px-4 py-8">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-600 to-violet-600 px-8 py-6">
                    <h1 className="text-2xl font-bold text-white">{title}</h1>
                    <p className="text-indigo-100">Điền thông tin chi tiết về từ vựng của bạn</p>
                </div>

                <form onSubmit={handleSubmit} className="p-8 space-y-8">
                    {/* Basic Info */}
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
                            onChange={handleWordChange}
                        />
                        {errors.word && (
                            <p className="mt-1 text-sm text-red-600 flex items-center">
                                <AlertCircle className="w-4 h-4 mr-1" />
                                {errors.word}
                            </p>
                        )}
                    </div>

                    {/* Meanings */}
                    <div>
                        <div className="flex items-center justify-between mb-4">
                            <label className="block text-sm font-semibold text-gray-700">
                                Ý nghĩa & Ví dụ
                            </label>
                            <button
                                type="button"
                                onClick={addMeaning}
                                className="text-sm px-3 py-1 bg-indigo-50 text-indigo-600 font-medium rounded-lg hover:bg-indigo-100 transition-colors flex items-center"
                            >
                                <Plus className="w-4 h-4 mr-1" />
                                Thêm nghĩa
                            </button>
                        </div>

                        <div className="space-y-6">
                            {formData.meanings?.map((meaning, index) => (
                                <div key={index} className="bg-gray-50 rounded-xl p-5 border border-gray-100 relative group">
                                    {formData.meanings.length > 1 && (
                                        <button
                                            type="button"
                                            onClick={() => removeMeaning(index)}
                                            className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                                            title="Xóa nghĩa này"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    )}

                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-xs font-medium text-gray-500 mb-1">
                                                Định nghĩa {index + 1} <span className="text-red-500">*</span>
                                            </label>
                                            <textarea
                                                rows={2}
                                                placeholder="Nhập định nghĩa..."
                                                className={`w-full px-4 py-2 border rounded-xl outline-none transition-all focus:ring-2 ${errors[`definition_${index}`]
                                                    ? 'border-red-300 focus:ring-red-100'
                                                    : 'border-gray-200 focus:ring-indigo-100 focus:border-indigo-500'
                                                    } bg-white`}
                                                value={meaning.definition}
                                                onChange={(e) => handleMeaningChange(index, 'definition', e.target.value)}
                                            />
                                            {errors[`definition_${index}`] && (
                                                <p className="mt-1 text-xs text-red-600 flex items-center">
                                                    <AlertCircle className="w-3 h-3 mr-1" />
                                                    {errors[`definition_${index}`]}
                                                </p>
                                            )}
                                        </div>
                                        <div>
                                            <label className="block text-xs font-medium text-gray-500 mb-1">
                                                Câu ví dụ (Tùy chọn)
                                            </label>
                                            <input
                                                type="text"
                                                placeholder="Câu ví dụ minh họa..."
                                                className="w-full px-4 py-2 border border-gray-200 rounded-xl outline-none transition-all focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500 bg-white"
                                                value={meaning.example_sentence}
                                                onChange={(e) => handleMeaningChange(index, 'example_sentence', e.target.value)}
                                            />
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        {errors.meanings && (
                            <p className="mt-2 text-sm text-red-600 flex items-center">
                                <AlertCircle className="w-4 h-4 mr-1" />
                                {errors.meanings}
                            </p>
                        )}
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
