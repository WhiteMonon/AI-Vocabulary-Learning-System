import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getVocabularies,
    getVocabulary,
    createVocabulary,
    updateVocabulary,
    deleteVocabulary
} from '../api/vocabulary';
import {
    VocabularyFilters,
    VocabularyUpdate,
    VocabularyListResponse,
} from '../types/vocabulary';

export const useVocabularies = (filters: VocabularyFilters) => {
    return useQuery({
        queryKey: ['vocabularies', filters],
        queryFn: () => getVocabularies(filters),
    });
};

export const useVocabulary = (id: number | undefined) => {
    return useQuery({
        queryKey: ['vocabulary', id],
        queryFn: () => getVocabulary(id!),
        enabled: !!id,
    });
};

export const useCreateVocabulary = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: createVocabulary,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vocabularies'] });
        },
    });
};

export const useUpdateVocabulary = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, vocab }: { id: number; vocab: VocabularyUpdate }) =>
            updateVocabulary(id, vocab),
        onMutate: async ({ id, vocab }) => {
            await queryClient.cancelQueries({ queryKey: ['vocabularies'] });
            await queryClient.cancelQueries({ queryKey: ['vocabulary', id] });

            const previousVocabularies = queryClient.getQueryData(['vocabularies']);
            const previousVocab = queryClient.getQueryData(['vocabulary', id]);

            // Optimistically update the list
            queryClient.setQueriesData<VocabularyListResponse>(
                { queryKey: ['vocabularies'] },
                (old) => {
                    if (!old) return old;
                    return {
                        ...old,
                        items: old.items.map((item) =>
                            item.id === id ? { ...item, ...vocab } : item
                        ),
                    };
                }
            );

            // Optimistically update the single item
            queryClient.setQueryData(['vocabulary', id], (old: any) => {
                if (!old) return old;
                return { ...old, ...vocab };
            });

            return { previousVocabularies, previousVocab };
        },
        onError: (_err, { id }, context: any) => {
            queryClient.setQueryData(['vocabularies'], context.previousVocabularies);
            queryClient.setQueryData(['vocabulary', id], context.previousVocab);
        },
        onSettled: (_data, _error, { id }) => {
            queryClient.invalidateQueries({ queryKey: ['vocabularies'] });
            queryClient.invalidateQueries({ queryKey: ['vocabulary', id] });
        },
    });
};

export const useDeleteVocabulary = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: deleteVocabulary,
        onMutate: async (id) => {
            await queryClient.cancelQueries({ queryKey: ['vocabularies'] });

            const previousVocabularies = queryClient.getQueryData(['vocabularies']);

            // Optimistically remove from list
            queryClient.setQueriesData<VocabularyListResponse>(
                { queryKey: ['vocabularies'] },
                (old) => {
                    if (!old) return old;
                    return {
                        ...old,
                        items: old.items.filter((item) => item.id !== id),
                        total: old.total - 1,
                    };
                }
            );

            return { previousVocabularies };
        },
        onError: (_err, _id, context: any) => {
            queryClient.setQueryData(['vocabularies'], context.previousVocabularies);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['vocabularies'] });
        },
    });
};
