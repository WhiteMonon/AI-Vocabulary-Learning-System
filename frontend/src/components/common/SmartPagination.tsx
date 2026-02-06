import React from 'react';
import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react';

interface SmartPaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    siblingCount?: number;
    className?: string;
}

const SmartPagination: React.FC<SmartPaginationProps> = ({
    currentPage,
    totalPages,
    onPageChange,
    siblingCount = 1,
    className = '',
}) => {
    // Generate page numbers to display
    const getPageNumbers = () => {
        const totalNumbers = siblingCount * 2 + 5; // siblingLeft + siblingRight + current + first + last + 2*dots
        const totalBlocks = totalNumbers + 2;

        if (totalPages <= totalBlocks) {
            return Array.from({ length: totalPages }, (_, i) => i + 1);
        }

        const leftSiblingIndex = Math.max(currentPage - siblingCount, 1);
        const rightSiblingIndex = Math.min(currentPage + siblingCount, totalPages);

        const shouldShowLeftDots = leftSiblingIndex > 2;
        const shouldShowRightDots = rightSiblingIndex < totalPages - 2;

        const firstPageIndex = 1;
        const lastPageIndex = totalPages;

        if (!shouldShowLeftDots && shouldShowRightDots) {
            const leftItemCount = 3 + 2 * siblingCount;
            const leftRange = Array.from({ length: leftItemCount }, (_, i) => i + 1);
            return [...leftRange, '...', totalPages];
        }

        if (shouldShowLeftDots && !shouldShowRightDots) {
            const rightItemCount = 3 + 2 * siblingCount;
            const rightRange = Array.from(
                { length: rightItemCount },
                (_, i) => totalPages - rightItemCount + i + 1
            );
            return [firstPageIndex, '...', ...rightRange];
        }

        if (shouldShowLeftDots && shouldShowRightDots) {
            const middleRange = Array.from(
                { length: rightSiblingIndex - leftSiblingIndex + 1 },
                (_, i) => leftSiblingIndex + i
            );
            return [firstPageIndex, '...', ...middleRange, '...', lastPageIndex];
        }

        return [];
    };

    const pages = getPageNumbers();

    if (totalPages <= 1) return null;

    return (
        <div className={`flex items-center justify-center space-x-2 ${className}`}>
            <button
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="p-2 border border-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors focus:ring-2 focus:ring-indigo-500 outline-none"
                aria-label="Previous Page"
            >
                <ChevronLeft className="w-5 h-5" />
            </button>

            <div className="hidden sm:flex items-center space-x-2">
                {pages.map((page, index) => {
                    if (page === '...') {
                        return (
                            <div key={`dots-${index}`} className="w-10 h-10 flex items-center justify-center text-gray-400">
                                <MoreHorizontal className="w-5 h-5" />
                            </div>
                        );
                    }

                    const pageNumber = page as number;
                    const isCurrent = pageNumber === currentPage;

                    return (
                        <button
                            key={pageNumber}
                            onClick={() => onPageChange(pageNumber)}
                            className={`min-w-[40px] h-10 px-3 rounded-lg font-medium transition-all focus:ring-2 focus:ring-offset-1 outline-none ${isCurrent
                                    ? 'bg-indigo-600 text-white shadow-md ring-indigo-500'
                                    : 'border border-gray-200 text-gray-600 hover:bg-gray-50 hover:text-indigo-600 ring-gray-200'
                                }`}
                            aria-current={isCurrent ? 'page' : undefined}
                        >
                            {pageNumber}
                        </button>
                    );
                })}
            </div>

            {/* Mobile View: Simplified */}
            <div className="flex sm:hidden items-center space-x-2 text-sm text-gray-600 font-medium">
                <span>Trang {currentPage} / {totalPages}</span>
            </div>

            <button
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="p-2 border border-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors focus:ring-2 focus:ring-indigo-500 outline-none"
                aria-label="Next Page"
            >
                <ChevronRight className="w-5 h-5" />
            </button>
        </div>
    );
};

export default SmartPagination;
