import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import type { TrailData, TrailIndex } from '../types/mountain';

// 마커 아이콘 설정 (Leaflet 기본 아이콘 문제 해결)
const startIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const endIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const waypointIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [20, 33],
  iconAnchor: [10, 33],
  popupAnchor: [1, -28],
  shadowSize: [33, 33]
});

// 정상 마커 아이콘 (금색/주황색)
const summitIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [30, 49],
  iconAnchor: [15, 49],
  popupAnchor: [1, -40],
  shadowSize: [49, 49]
});

// 지도 범위를 자동으로 맞추는 컴포넌트
function FitBounds({ bounds }: { bounds: L.LatLngBoundsExpression }) {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(bounds, { padding: [20, 20] });
  }, [map, bounds]);
  return null;
}

interface TrailMapProps {
  mountainName: string;
}

export function TrailMap({ mountainName }: TrailMapProps) {
  const [trailData, setTrailData] = useState<TrailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchTrailData() {
      setLoading(true);
      setError(null);

      try {
        // 인덱스에서 산 이름으로 mnt_code 찾기
        const indexRes = await fetch('/trails/index.json');
        if (!indexRes.ok) throw new Error('인덱스 파일을 불러올 수 없습니다');

        const index: TrailIndex[] = await indexRes.json();

        // 산 이름으로 매칭 (괄호 있는 이름과 없는 이름 모두 시도)
        let mountainInfo = index.find(m => m.mountain_name === mountainName);

        // 정확한 매칭이 안되면 부분 매칭 시도
        if (!mountainInfo) {
          const baseName = mountainName.split('(')[0];
          mountainInfo = index.find(m =>
            m.mountain_name === baseName ||
            m.mountain_name.startsWith(baseName + '(')
          );
        }

        if (!mountainInfo) {
          setError('등산로 데이터가 없습니다');
          setLoading(false);
          return;
        }

        // mnt_code로 트레일 데이터 가져오기
        const trailRes = await fetch(`/trails/${mountainInfo.mnt_code}.json`);
        if (!trailRes.ok) throw new Error('트레일 데이터를 불러올 수 없습니다');

        const data: TrailData = await trailRes.json();
        setTrailData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : '데이터를 불러오는데 실패했습니다');
      } finally {
        setLoading(false);
      }
    }

    fetchTrailData();
  }, [mountainName]);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div className="h-[400px] flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-gray-500">등산로 지도를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !trailData) {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div className="h-[300px] flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <span className="text-5xl">🗺️</span>
            <p className="mt-4 text-gray-600">{error || '등산로 데이터가 없습니다'}</p>
            <p className="mt-2 text-sm text-gray-400">
              램블러, 트랭글에서 등산 코스 GPX를 다운로드하세요
            </p>
          </div>
        </div>
      </div>
    );
  }

  // GeoJSON 좌표 [lon, lat] → Leaflet 좌표 [lat, lon] 변환
  const trackLatLngs: [number, number][] = trailData.track.map(([lon, lat]) => [lat, lon]);

  // 시작점과 끝점
  const startPoint = trackLatLngs[0];
  const endPoint = trackLatLngs[trackLatLngs.length - 1];

  // bounds 계산
  const bounds: L.LatLngBoundsExpression = [
    [trailData.bounds.southwest[1], trailData.bounds.southwest[0]],  // [lat, lon]
    [trailData.bounds.northeast[1], trailData.bounds.northeast[0]]
  ];

  return (
    <div className="space-y-4">
      {/* 지도 정보 헤더 */}
      <div className="bg-white rounded-2xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-emerald-500 font-medium">📏 총 거리</span>
            <span className="text-gray-700">{trailData.total_distance_km.toFixed(1)} km</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-blue-500 font-medium">📍 트랙 포인트</span>
            <span className="text-gray-700">{trailData.point_count.toLocaleString()}개</span>
          </div>
          {trailData.waypoint_count > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-orange-500 font-medium">🚩 주요 지점</span>
              <span className="text-gray-700">{trailData.waypoint_count}개</span>
            </div>
          )}
          {trailData.summit && (
            <div className="flex items-center gap-2">
              <span className="text-yellow-600 font-medium">⛰️ 정상</span>
              <span className="text-gray-700">{trailData.summit.elevation.toLocaleString()}m</span>
            </div>
          )}
        </div>
      </div>

      {/* 지도 */}
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <MapContainer
          center={[trailData.center[1], trailData.center[0]]}
          zoom={13}
          style={{ height: '450px', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <FitBounds bounds={bounds} />

          {/* 등산로 경로 */}
          <Polyline
            positions={trackLatLngs}
            pathOptions={{
              color: '#3b82f6',
              weight: 3,
              opacity: 0.8
            }}
          />

          {/* 시작점 마커 */}
          <Marker position={startPoint} icon={startIcon}>
            <Popup>
              <div className="text-center">
                <span className="font-semibold text-green-600">출발점</span>
              </div>
            </Popup>
          </Marker>

          {/* 끝점 마커 */}
          <Marker position={endPoint} icon={endIcon}>
            <Popup>
              <div className="text-center">
                <span className="font-semibold text-red-600">종점</span>
              </div>
            </Popup>
          </Marker>

          {/* 정상 마커 */}
          {trailData.summit && (
            <Marker
              position={[trailData.summit.coordinates[1], trailData.summit.coordinates[0]]}
              icon={summitIcon}
              zIndexOffset={1000}
            >
              <Popup>
                <div className="text-center">
                  <span className="font-bold text-yellow-600 text-lg">⛰️ 정상</span>
                  <p className="text-sm font-semibold mt-1">{trailData.mountain_name}</p>
                  <p className="text-sm text-gray-600">{trailData.summit.elevation.toLocaleString()}m</p>
                </div>
              </Popup>
            </Marker>
          )}

          {/* 웨이포인트 마커 */}
          {trailData.waypoints.map((wp, idx) => (
            <Marker
              key={idx}
              position={[wp.coordinates[1], wp.coordinates[0]]}
              icon={waypointIcon}
            >
              <Popup>
                <div className="text-center">
                  <span className="font-semibold">{wp.name || `지점 ${idx + 1}`}</span>
                  {wp.elevation > 0 && (
                    <p className="text-xs text-gray-500">{wp.elevation}m</p>
                  )}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* 범례 */}
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
        <p className="text-xs text-gray-500 font-medium mb-2">범례</p>
        <div className="flex flex-wrap gap-4 text-xs text-gray-600">
          <span className="flex items-center gap-1">
            <span className="w-4 h-4 rounded-full bg-yellow-500 flex items-center justify-center text-[8px]">⛰️</span> 정상
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-500"></span> 출발점
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-red-500"></span> 종점
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-blue-500"></span> 주요 지점
          </span>
          <span className="flex items-center gap-1">
            <span className="w-4 h-0.5 bg-blue-500"></span> 등산로
          </span>
        </div>
        <p className="mt-3 text-xs text-gray-400">
          * 산림청 등산로 공간정보 + 블랙야크 100대 명산 정상 좌표 기반
        </p>
      </div>
    </div>
  );
}
