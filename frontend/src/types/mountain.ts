export interface Mountain {
  id: string;
  name: string;
  name_origin: string | null;
  altitude: number | null;
  region: string;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  category: string[];
  first_char: string | null;
  certification_point: string | null;
  image_url: string | null;
  description: string | null;
  significance: string | null;
  created_at: string;
  updated_at: string;
}

export interface Trail {
  id: string;
  mountain_id: string;
  name: string;
  trail_head: string | null;
  trail_end: string | null;
  distance_km: number | null;
  estimated_time_minutes: number | null;
  difficulty: 'easy' | 'moderate' | 'hard' | 'expert' | null;
  elevation_gain: number | null;
  time_category: string | null;
  is_circular: boolean;
  is_recommended: boolean;
  description: string | null;
  cautions: string | null;
  gpx_file_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface ParkingLot {
  id: string;
  mountain_id: string;
  name: string;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  fee_type: 'free' | 'paid' | 'mixed' | null;
  fee_description: string | null;
  capacity: number | null;
  operating_hours: string | null;
  has_restroom: boolean;
  has_store: boolean;
  nearby_trail_head: string | null;
  created_at: string;
  updated_at: string;
}

export interface Highlight {
  id: string;
  mountain_id: string;
  name: string;
  category: string | null;
  description: string | null;
  latitude: number | null;
  longitude: number | null;
  image_url: string | null;
  created_at: string;
}

export type DifficultyLevel = 'easy' | 'moderate' | 'hard' | 'expert';

// GPX Trail 데이터 (산림청)
export interface TrailData {
  mountain_name: string;
  mnt_code: number;
  blackyak_id: number | null;
  track: [number, number][];  // [lon, lat][]
  waypoints: TrailWaypoint[];
  center: [number, number];   // [lon, lat]
  bounds: {
    southwest: [number, number];
    northeast: [number, number];
  };
  total_distance_km: number;
  point_count: number;
  waypoint_count: number;
  summit: TrailSummit | null;  // 정상 위치
}

export interface TrailSummit {
  coordinates: [number, number];  // [lon, lat]
  elevation: number;  // 해발고도 (m)
}

export interface TrailWaypoint {
  coordinates: [number, number];  // [lon, lat]
  name: string;
  elevation: number;
}

export interface TrailIndex {
  mountain_name: string;
  mnt_code: number;
  blackyak_id: number | null;
  distance_km: number;
}

export interface MountainFilters {
  search?: string;
  region?: string | null;
  difficulty?: DifficultyLevel | null;
  timeCategory?: string | null;
}

export interface MountainWithTrails extends Mountain {
  trails: Trail[];
}

// 산림청 산정보 API 데이터
export interface MountainInfo {
  blackyak_id: number;
  blackyak_name: string;
  mntn_nm: string;
  mntn_height: string;
  mntn_location: string;
  mntn_summary: string;      // 산 개관/설명 (API)
  tourism_info: string;      // 주변 관광정보 (API)
  image_url: string;
  certification_point: string;
  altitude: number | null;
  region: string;
  address: string;
  latitude: number | null;
  longitude: number | null;
}
