import { supabase } from './supabase';
import type { Mountain, Trail, MountainFilters } from '../types';

export interface GetMountainsParams {
  page?: number;
  limit?: number;
  filters?: MountainFilters;
}

export interface GetMountainsResponse {
  data: Mountain[];
  count: number;
  page: number;
  totalPages: number;
}

export async function getMountains({
  page = 1,
  limit = 12,
  filters,
}: GetMountainsParams = {}): Promise<GetMountainsResponse> {
  let query = supabase
    .from('mountains')
    .select('*', { count: 'exact' });

  // Apply filters
  if (filters?.search) {
    query = query.or(`name.ilike.%${filters.search}%,address.ilike.%${filters.search}%`);
  }

  if (filters?.region) {
    query = query.eq('region', filters.region);
  }

  // Pagination
  const from = (page - 1) * limit;
  const to = from + limit - 1;

  query = query.range(from, to).order('name', { ascending: true });

  const { data, error, count } = await query;

  if (error) {
    throw new Error(`Failed to fetch mountains: ${error.message}`);
  }

  return {
    data: data || [],
    count: count || 0,
    page,
    totalPages: Math.ceil((count || 0) / limit),
  };
}

export async function getMountainById(id: string): Promise<Mountain | null> {
  const { data, error } = await supabase
    .from('mountains')
    .select('*')
    .eq('id', id)
    .single();

  if (error) {
    if (error.code === 'PGRST116') {
      return null; // Not found
    }
    throw new Error(`Failed to fetch mountain: ${error.message}`);
  }

  return data;
}

export async function searchMountains(searchTerm: string): Promise<Mountain[]> {
  const { data, error } = await supabase
    .from('mountains')
    .select('*')
    .or(`name.ilike.%${searchTerm}%,address.ilike.%${searchTerm}%,certification_point.ilike.%${searchTerm}%`)
    .order('name', { ascending: true })
    .limit(20);

  if (error) {
    throw new Error(`Failed to search mountains: ${error.message}`);
  }

  return data || [];
}

export async function getRegions(): Promise<string[]> {
  const { data, error } = await supabase
    .from('mountains')
    .select('region')
    .order('region', { ascending: true });

  if (error) {
    throw new Error(`Failed to fetch regions: ${error.message}`);
  }

  const uniqueRegions = [...new Set(data?.map((m) => m.region) || [])];
  return uniqueRegions;
}

export async function getTrailsByMountainId(mountainId: string): Promise<Trail[]> {
  const { data, error } = await supabase
    .from('trails')
    .select('*')
    .eq('mountain_id', mountainId)
    .order('is_recommended', { ascending: false })
    .order('estimated_time_minutes', { ascending: true });

  if (error) {
    throw new Error(`Failed to fetch trails: ${error.message}`);
  }

  return data || [];
}
