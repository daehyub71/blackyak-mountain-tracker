import { create } from 'zustand';
import type { MountainFilters, DifficultyLevel } from '../types';

interface FilterState {
  filters: MountainFilters;
  page: number;
  setSearch: (search: string) => void;
  setRegion: (region: string | null) => void;
  setDifficulty: (difficulty: DifficultyLevel | null) => void;
  setTimeCategory: (timeCategory: string | null) => void;
  setPage: (page: number) => void;
  resetFilters: () => void;
}

const initialFilters: MountainFilters = {
  search: '',
  region: null,
  difficulty: null,
  timeCategory: null,
};

export const useFilterStore = create<FilterState>((set) => ({
  filters: initialFilters,
  page: 1,

  setSearch: (search) =>
    set((state) => ({
      filters: { ...state.filters, search },
      page: 1,
    })),

  setRegion: (region) =>
    set((state) => ({
      filters: { ...state.filters, region },
      page: 1,
    })),

  setDifficulty: (difficulty) =>
    set((state) => ({
      filters: { ...state.filters, difficulty },
      page: 1,
    })),

  setTimeCategory: (timeCategory) =>
    set((state) => ({
      filters: { ...state.filters, timeCategory },
      page: 1,
    })),

  setPage: (page) => set({ page }),

  resetFilters: () =>
    set({
      filters: initialFilters,
      page: 1,
    }),
}));
