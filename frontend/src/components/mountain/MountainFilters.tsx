import { useRegions } from '../../hooks/useMountains';

interface MountainFiltersProps {
  selectedRegion: string | null;
  onRegionChange: (region: string | null) => void;
}

export function MountainFilters({
  selectedRegion,
  onRegionChange,
}: MountainFiltersProps) {
  const { data: regions, isLoading } = useRegions();

  if (isLoading) {
    return (
      <div className="flex justify-center gap-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            className="h-8 w-16 bg-gray-100 rounded-full animate-pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
      <div className="flex justify-center gap-2 pb-2 sm:pb-0 sm:flex-wrap min-w-max sm:min-w-0">
        <button
          onClick={() => onRegionChange(null)}
          className={`px-4 py-2 rounded-full text-sm transition-all whitespace-nowrap ${
            selectedRegion === null
              ? 'bg-slate-900 text-white font-medium'
              : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300'
          }`}
        >
          전체
        </button>
        {regions?.map((region) => (
          <button
            key={region}
            onClick={() => onRegionChange(region)}
            className={`px-4 py-2 rounded-full text-sm transition-all whitespace-nowrap ${
              selectedRegion === region
                ? 'bg-slate-900 text-white font-medium'
                : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300'
            }`}
          >
            {region.replace(/특별자치|광역|특별/g, '')}
          </button>
        ))}
      </div>
    </div>
  );
}
