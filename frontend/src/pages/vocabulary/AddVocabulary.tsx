import React from 'react';
import VocabularyForm from './VocabularyForm';
import { useCreateVocabulary } from '../../hooks/useVocabulary';
import { VocabularyCreate } from '../../types/vocabulary';

const AddVocabulary: React.FC = () => {
    const { mutateAsync, isPending } = useCreateVocabulary();

    const handleSubmit = async (data: VocabularyCreate) => {
        await mutateAsync(data);
    };

    return (
        <VocabularyForm
            title="Thêm từ vựng mới"
            onSubmit={handleSubmit}
            isLoading={isPending}
        />
    );
};

export default AddVocabulary;
