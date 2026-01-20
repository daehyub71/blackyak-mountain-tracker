import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import {
  getMountains,
  getMountainById,
  searchMountains,
  getRegions,
  getTrailsByMountainId,
  type GetMountainsParams,
} from '../services/mountainService';
import type { MountainFilters } from '../types';

export function useMountains(params: GetMountainsParams = {}) {
  return useQuery({
    queryKey: ['mountains', params],
    queryFn: () => getMountains(params),
  });
}

export function useInfiniteMountains(filters: MountainFilters = {}, limit = 12) {
  return useInfiniteQuery({
    queryKey: ['mountains', 'infinite', filters],
    queryFn: ({ pageParam = 1 }) => getMountains({ page: pageParam, limit, filters }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.totalPages) {
        return lastPage.page + 1;
      }
      return undefined;
    },
  });
}

export function useMountain(id: string | undefined) {
  return useQuery({
    queryKey: ['mountain', id],
    queryFn: () => getMountainById(id!),
    enabled: !!id,
  });
}

export function useSearchMountains(searchTerm: string) {
  return useQuery({
    queryKey: ['mountains', 'search', searchTerm],
    queryFn: () => searchMountains(searchTerm),
    enabled: searchTerm.length >= 1,
  });
}

export function useRegions() {
  return useQuery({
    queryKey: ['regions'],
    queryFn: getRegions,
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

export function useTrails(mountainId: string | undefined) {
  return useQuery({
    queryKey: ['trails', mountainId],
    queryFn: () => getTrailsByMountainId(mountainId!),
    enabled: !!mountainId,
  });
}
