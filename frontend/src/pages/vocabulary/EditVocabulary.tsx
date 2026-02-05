import React from 'react';
import { useParams } from 'react-router-dom';
import VocabularyForm from './VocabularyForm';
import { useVocabulary, useUpdateVocabulary } from '../../hooks/useVocabulary';
import { VocabularyUpdate } from '../../types/vocabulary';
import { Loader2 } from 'lucide-react';

const EditVocabulary: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const vocabId = parseInt(id || '0');

    const { data: vocab, isLoading: isFetching } = useVocabulary(vocabId);
    const { mutateAsync, isPending: isUpdating } = useUpdateVocabulary();

    const handleSubmit = async (data: VocabularyUpdate) => {
        await mutateAsync({ id: vocabId, vocab: data });
    };

    if (isFetching) {
        return (
            <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-10 h-10 text-indigo-600 animate-spin mb-4" />
                <p className="text-gray-500">Đang tải thông tin từ vựng...</p>
            </div>
        );
    }

    if (!vocab) {
        return (
            <div className="container mx-auto px-4 py-20 text-center">
                <h2 className="text-2xl font-bold text-gray-900">Không tìm thấy từ vựng</h2>
                <p className="text-gray-600 mt-2">Từ vựng bạn đang tìm kiếm không tồn tại hoặc đã bị xóa.</p>
            </div>
        );
    }

    return (
        <VocabularyForm
            title={`Chỉnh sửa: ${vocab.word}`}
            initialData={vocab}
            onSubmit={handleSubmit}
            isLoading={isUpdating}
        />
    );
};

export default EditVocabulary;
