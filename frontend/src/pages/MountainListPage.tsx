import { useInfiniteMountains } from '../hooks/useMountains';
import { useFilterStore } from '../stores/filterStore';
import { MountainCard } from '../components/mountain/MountainCard';
import { MountainFilters } from '../components/mountain/MountainFilters';
import { SearchBar } from '../components/common/SearchBar';

export function MountainListPage() {
  const { filters, setSearch, setRegion } = useFilterStore();

  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteMountains(filters, 12);

  // Flatten all pages into a single array
  const mountains = data?.pages.flatMap((page) => page.data) ?? [];
  const totalCount = data?.pages[0]?.count ?? 0;

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="bg-gradient-to-b from-emerald-50/50 to-white pt-12 pb-8">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
            블랙야크 100대 명산
          </h1>
          <p className="mt-3 text-gray-500 text-sm md:text-base">
            대한민국을 대표하는 100대 명산을 탐험하세요
          </p>
          <p className="text-gray-400 text-xs mt-1">
            등산 코스, 인증샷 명소, GPX 파일까지 한번에!
          </p>

          {/* Search Bar */}
          <div className="mt-8 max-w-xl mx-auto">
            <SearchBar
              value={filters.search ?? ''}
              onChange={setSearch}
              placeholder="예: 가리산, 관악산, 지리산, 북한산..."
            />
          </div>

          {/* Filter Pills */}
          <div className="mt-4">
            <MountainFilters
              selectedRegion={filters.region ?? null}
              onRegionChange={setRegion}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Results Count */}
        {data && (
          <div className="mb-6 flex items-center gap-2 text-sm text-gray-600">
            <span className="text-lg">⛰️</span>
            <span className="font-medium">{totalCount} 개의 산 탐색 중</span>
            {filters.search && (
              <span className="text-gray-400">· 검색: "{filters.search}"</span>
            )}
            {filters.region && (
              <span className="text-gray-400">· {filters.region}</span>
            )}
          </div>
        )}

        {/* Loading State (Initial) */}
        {isLoading && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(12)].map((_, i) => (
              <div key={i} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="aspect-square bg-gray-100 animate-pulse" />
                <div className="p-4 space-y-3">
                  <div className="h-5 bg-gray-100 rounded animate-pulse" />
                  <div className="h-4 bg-gray-100 rounded w-2/3 animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="text-center py-16">
            <div className="text-red-500 text-lg">데이터를 불러오는데 실패했습니다</div>
            <p className="mt-2 text-gray-500">{error.message}</p>
          </div>
        )}

        {/* Mountain Grid */}
        {mountains.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {mountains.map((mountain) => (
              <MountainCard key={mountain.id} mountain={mountain} />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && mountains.length === 0 && (
          <div className="text-center py-16">
            <span className="text-6xl">🔍</span>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              검색 결과가 없습니다
            </h3>
            <p className="mt-2 text-gray-500">
              다른 검색어나 필터를 시도해보세요
            </p>
          </div>
        )}

        {/* Load More */}
        {mountains.length > 0 && (
          <div className="mt-12 text-center">
            {hasNextPage ? (
              <button
                onClick={() => fetchNextPage()}
                disabled={isFetchingNextPage}
                className="inline-flex items-center gap-2 px-6 py-3 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-full hover:bg-gray-50 hover:border-gray-300 transition-all disabled:opacity-50"
              >
                {isFetchingNextPage ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    불러오는 중...
                  </>
                ) : (
                  <>
                    더 많은 산 보기
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </>
                )}
              </button>
            ) : (
              <p className="text-sm text-gray-400">모든 산을 확인했습니다</p>
            )}
            <div className="mt-4 text-xs text-gray-400">
              {mountains.length} / {totalCount} 개 표시 중
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
