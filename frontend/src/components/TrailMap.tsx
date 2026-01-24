import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import type { TrailData, TrailIndex, NationalParkTrailData } from '../types/mountain';

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

// 코스별 색상 팔레트
const TRAIL_COLORS = [
  '#3b82f6', // blue
  '#ef4444', // red
  '#22c55e', // green
  '#f59e0b', // amber
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#f97316', // orange
  '#84cc16', // lime
  '#6366f1', // indigo
];

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
  blackyakId?: number;
  certificationPoint?: string;  // 인증 장소 (예: "대청봉", "백운대")
}

type DataSource = 'national_park' | 'forest_service' | null;

// 인증 장소 키워드 추출 (예: "지리산 천왕봉" -> ["천왕봉", "천왕"], "서석대 정상석/ 인왕봉 정상석" -> ["서석대", "인왕봉", "인왕"])
function extractCertKeywords(certPoint: string | undefined): string[] {
  if (!certPoint) return [];

  // 공통 불용어 제거
  const stopWords = ['정상석', '/', '인증'];
  let cleaned = certPoint;
  for (const word of stopWords) {
    cleaned = cleaned.replace(new RegExp(word, 'g'), ' ');
  }

  // 키워드 추출 (2글자 이상)
  const baseKeywords = cleaned.split(/[\s,/]+/)
    .map(w => w.trim())
    .filter(w => w.length >= 2);

  // 키워드 확장: "봉", "산", "대" 제거 버전 추가 (예: 천황봉 -> 천황, 노인봉 -> 노인)
  const expandedKeywords = new Set<string>();
  for (const kw of baseKeywords) {
    expandedKeywords.add(kw);
    // 봉, 산, 대로 끝나면 제거한 버전도 추가
    if (kw.length >= 3 && /[봉산대]$/.test(kw)) {
      const shortened = kw.slice(0, -1);
      if (shortened.length >= 2) {
        expandedKeywords.add(shortened);
      }
    }
  }

  const keywords = Array.from(expandedKeywords);

  // "정상" 키워드도 추가 (백록담 등 코스명에 없는 경우 대비)
  if (!keywords.includes('정상')) {
    keywords.push('정상');
  }

  return keywords;
}

// 코스가 인증 장소를 포함하는지 확인
function matchesCertPoint(courseName: string, detail: string, keywords: string[]): boolean {
  if (keywords.length === 0) return true;  // 키워드 없으면 모두 포함

  const text = `${courseName} ${detail}`.toLowerCase();
  return keywords.some(kw => text.includes(kw.toLowerCase()));
}

export function TrailMap({ mountainName, blackyakId, certificationPoint }: TrailMapProps) {
  const [trailData, setTrailData] = useState<TrailData | null>(null);
  const [npTrailData, setNpTrailData] = useState<NationalParkTrailData | null>(null);
  const [dataSource, setDataSource] = useState<DataSource>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCourses, setSelectedCourses] = useState<Set<number>>(new Set());

  useEffect(() => {
    async function fetchTrailData() {
      setLoading(true);
      setError(null);
      setTrailData(null);
      setNpTrailData(null);
      setDataSource(null);

      try {
        // 1. 먼저 국립공원 데이터 확인 (blackyakId가 있는 경우)
        if (blackyakId) {
          try {
            const npRes = await fetch(`/trails/np_${blackyakId}.json`);
            if (npRes.ok) {
              const npData: NationalParkTrailData = await npRes.json();
              if (npData.features && npData.features.length > 0) {
                setNpTrailData(npData);
                setDataSource('national_park');

                // 인증 장소 키워드로 코스 필터링
                const keywords = extractCertKeywords(certificationPoint);
                const matchingIndices: number[] = [];

                npData.features.forEach((feature, idx) => {
                  const name = feature.properties.name || '';
                  const detail = feature.properties.detail || '';
                  if (matchesCertPoint(name, detail, keywords)) {
                    matchingIndices.push(idx);
                  }
                });

                // 매칭된 코스가 있으면 그것만 선택, 없으면 전체 코스 선택
                if (matchingIndices.length > 0) {
                  setSelectedCourses(new Set(matchingIndices));
                } else {
                  // 인증 장소 매칭 코스가 없으면 전체 코스 선택
                  setSelectedCourses(new Set(npData.features.map((_, i) => i)));
                }

                setLoading(false);
                return;
              }
            }
          } catch {
            // 국립공원 데이터 없음, 다음 소스로 폴백
          }

          // 1.5. GPX 업로드 데이터 확인 (사용자 업로드)
          try {
            const gpxRes = await fetch(`/trails/gpx_${blackyakId}.json`);
            if (gpxRes.ok) {
              const gpxData: TrailData = await gpxRes.json();
              if (gpxData.track && gpxData.track.length > 0) {
                setTrailData(gpxData);
                setDataSource('forest_service');  // 같은 형식 사용
                setLoading(false);
                return;
              }
            }
          } catch {
            // GPX 업로드 데이터 없음, 산림청 데이터로 폴백
          }
        }

        // 2. 산림청 GPX 데이터 확인
        const indexRes = await fetch('/trails/index.json');
        if (!indexRes.ok) throw new Error('인덱스 파일을 불러올 수 없습니다');

        const index: TrailIndex[] = await indexRes.json();

        // 산 이름으로 매칭
        let mountainInfo = index.find(m => m.mountain_name === mountainName);

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

        const trailRes = await fetch(`/trails/${mountainInfo.mnt_code}.json`);
        if (!trailRes.ok) throw new Error('트레일 데이터를 불러올 수 없습니다');

        const data: TrailData = await trailRes.json();
        setTrailData(data);
        setDataSource('forest_service');
      } catch (err) {
        setError(err instanceof Error ? err.message : '데이터를 불러오는데 실패했습니다');
      } finally {
        setLoading(false);
      }
    }

    fetchTrailData();
  }, [mountainName, blackyakId, certificationPoint]);

  const toggleCourse = (index: number) => {
    setSelectedCourses(prev => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const selectAllCourses = () => {
    if (npTrailData) {
      setSelectedCourses(new Set(npTrailData.features.map((_, i) => i)));
    }
  };

  const clearAllCourses = () => {
    setSelectedCourses(new Set());
  };

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

  if (error || (!trailData && !npTrailData)) {
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

  // 국립공원 데이터 렌더링
  if (dataSource === 'national_park' && npTrailData) {
    return <NationalParkMap
      data={npTrailData}
      selectedCourses={selectedCourses}
      toggleCourse={toggleCourse}
      selectAllCourses={selectAllCourses}
      clearAllCourses={clearAllCourses}
      certificationPoint={certificationPoint}
    />;
  }

  // 산림청 데이터 렌더링
  if (dataSource === 'forest_service' && trailData) {
    return <ForestServiceMap data={trailData} />;
  }

  return null;
}

// 국립공원 지도 컴포넌트
function NationalParkMap({
  data,
  selectedCourses,
  toggleCourse,
  selectAllCourses,
  clearAllCourses,
  certificationPoint
}: {
  data: NationalParkTrailData;
  selectedCourses: Set<number>;
  toggleCourse: (index: number) => void;
  selectAllCourses: () => void;
  clearAllCourses: () => void;
  certificationPoint?: string;
}) {
  // 정상 정보
  const summit = data.summit;
  // 인증 장소 키워드 추출
  const certKeywords = extractCertKeywords(certificationPoint);

  // 각 코스가 인증 장소를 포함하는지 확인
  const courseMatches = data.features.map(feature => {
    const name = feature.properties.name || '';
    const detail = feature.properties.detail || '';
    return matchesCertPoint(name, detail, certKeywords);
  });

  const matchingCount = courseMatches.filter(Boolean).length;
  // 선택된 코스들의 bounds 계산
  const selectedFeatures = data.features.filter((_, i) => selectedCourses.has(i));

  let bounds: L.LatLngBoundsExpression;
  if (selectedFeatures.length > 0) {
    const allCoords = selectedFeatures.flatMap(f => f.geometry.coordinates);
    const lats = allCoords.map(c => c[1]);
    const lons = allCoords.map(c => c[0]);
    bounds = [
      [Math.min(...lats), Math.min(...lons)],
      [Math.max(...lats), Math.max(...lons)]
    ];
  } else {
    bounds = [[data.center[1] - 0.05, data.center[0] - 0.05], [data.center[1] + 0.05, data.center[0] + 0.05]];
  }

  // 총 거리 계산
  const totalDistance = selectedFeatures.reduce((sum, f) => sum + (f.properties.distance_m || 0), 0);

  return (
    <div className="space-y-4">
      {/* 지도 정보 헤더 */}
      <div className="bg-white rounded-2xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4 text-sm mb-3">
          <div className="flex items-center gap-2">
            <span className="text-emerald-500 font-medium">🏞️ 국립공원</span>
            <span className="text-gray-700">{data.mountain_name}</span>
          </div>
          {certificationPoint && (
            <div className="flex items-center gap-2">
              <span className="text-yellow-600 font-medium">🏅 인증장소</span>
              <span className="text-gray-700">{certificationPoint}</span>
            </div>
          )}
          <div className="flex items-center gap-2">
            <span className="text-blue-500 font-medium">🥾 코스</span>
            <span className="text-gray-700">
              {matchingCount > 0 ? (
                <>인증코스 {matchingCount}개 / 전체 {data.features.length}개</>
              ) : (
                <>{selectedCourses.size} / {data.features.length}개 선택</>
              )}
            </span>
          </div>
          {totalDistance > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-orange-500 font-medium">📏 총 거리</span>
              <span className="text-gray-700">{(totalDistance / 1000).toFixed(1)} km</span>
            </div>
          )}
          {summit && (
            <div className="flex items-center gap-2">
              <span className="text-yellow-600 font-medium">⛰️ 정상</span>
              <span className="text-gray-700">{summit.elevation.toLocaleString()}m</span>
            </div>
          )}
        </div>

        {/* 코스 선택 UI */}
        <div className="border-t border-gray-100 pt-3">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-medium text-gray-500">
              {matchingCount > 0 ? '인증장소 포함 코스:' : '코스 선택:'}
            </span>
            {matchingCount === 0 && (
              <>
                <button
                  onClick={selectAllCourses}
                  className="text-xs text-blue-500 hover:underline"
                >
                  전체 선택
                </button>
                <span className="text-gray-300">|</span>
                <button
                  onClick={clearAllCourses}
                  className="text-xs text-gray-500 hover:underline"
                >
                  전체 해제
                </button>
              </>
            )}
          </div>
          <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
            {data.features.map((feature, idx) => {
              const isMatch = courseMatches[idx];
              // 인증장소 매칭 코스가 있으면, 매칭되지 않는 코스는 숨김
              if (matchingCount > 0 && !isMatch) return null;

              return (
                <button
                  key={idx}
                  onClick={() => toggleCourse(idx)}
                  className={`text-xs px-2 py-1 rounded-full border transition-colors ${
                    selectedCourses.has(idx)
                      ? 'border-transparent text-white'
                      : isMatch
                        ? 'border-yellow-400 text-yellow-700 bg-yellow-50 hover:bg-yellow-100'
                        : 'border-gray-200 text-gray-600 bg-white hover:bg-gray-50'
                  }`}
                  style={selectedCourses.has(idx) ? { backgroundColor: TRAIL_COLORS[idx % TRAIL_COLORS.length] } : {}}
                >
                  {isMatch && '🏅 '}{feature.properties.name}
                </button>
              );
            })}
          </div>
          {matchingCount > 0 && matchingCount < data.features.length && (
            <p className="text-xs text-gray-400 mt-2">
              * {data.features.length - matchingCount}개의 다른 코스는 인증장소를 포함하지 않아 숨김 처리됨
            </p>
          )}
          {matchingCount === 0 && certificationPoint && (
            <p className="text-xs text-orange-500 mt-2">
              ⚠️ 인증장소({certificationPoint}) 코스를 찾지 못해 전체 코스를 표시합니다
            </p>
          )}
        </div>
      </div>

      {/* 지도 */}
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <MapContainer
          center={[data.center[1], data.center[0]]}
          zoom={12}
          style={{ height: '500px', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {selectedFeatures.length > 0 && <FitBounds bounds={bounds} />}

          {/* 각 코스별 경로 */}
          {data.features.map((feature, idx) => {
            if (!selectedCourses.has(idx)) return null;

            const coords = feature.geometry.coordinates;
            const latLngs: [number, number][] = coords.map(([lon, lat]) => [lat, lon]);
            const color = TRAIL_COLORS[idx % TRAIL_COLORS.length];

            const startPoint = latLngs[0];
            const endPoint = latLngs[latLngs.length - 1];

            return (
              <div key={idx}>
                <Polyline
                  positions={latLngs}
                  pathOptions={{
                    color,
                    weight: 3,
                    opacity: 0.8
                  }}
                />
                {/* 시작점 */}
                <Marker position={startPoint} icon={startIcon}>
                  <Popup>
                    <div className="text-center">
                      <span className="font-semibold text-green-600">출발점</span>
                      <p className="text-xs mt-1">{feature.properties.name}</p>
                    </div>
                  </Popup>
                </Marker>
                {/* 종점 */}
                <Marker position={endPoint} icon={endIcon}>
                  <Popup>
                    <div className="text-center">
                      <span className="font-semibold text-red-600">종점</span>
                      <p className="text-xs mt-1">{feature.properties.name}</p>
                    </div>
                  </Popup>
                </Marker>
              </div>
            );
          })}

          {/* 정상 마커 */}
          {summit && (
            <Marker
              position={[summit.coordinates[1], summit.coordinates[0]]}
              icon={summitIcon}
              zIndexOffset={1000}
            >
              <Popup>
                <div className="text-center">
                  <span className="font-bold text-yellow-600 text-lg">⛰️ 정상</span>
                  <p className="text-sm font-semibold mt-1">{data.mountain_name}</p>
                  <p className="text-sm text-gray-600">{summit.elevation.toLocaleString()}m</p>
                </div>
              </Popup>
            </Marker>
          )}
        </MapContainer>
      </div>

      {/* 선택된 코스 상세 */}
      {selectedFeatures.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 p-4">
          <h4 className="font-medium text-gray-800 mb-3">선택된 코스 정보</h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {data.features.map((feature, idx) => {
              if (!selectedCourses.has(idx)) return null;
              const color = TRAIL_COLORS[idx % TRAIL_COLORS.length];
              return (
                <div key={idx} className="flex items-start gap-3 text-sm p-2 bg-gray-50 rounded-lg">
                  <span
                    className="w-3 h-3 rounded-full mt-1 flex-shrink-0"
                    style={{ backgroundColor: color }}
                  />
                  <div>
                    <p className="font-medium text-gray-800">{feature.properties.name}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{feature.properties.detail}</p>
                    <div className="flex gap-3 mt-1 text-xs text-gray-400">
                      {feature.properties.distance_m > 0 && (
                        <span>거리: {(feature.properties.distance_m / 1000).toFixed(1)}km</span>
                      )}
                      {feature.properties.difficulty && (
                        <span>난이도: {feature.properties.difficulty}</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 범례 */}
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
        <p className="text-xs text-gray-500 font-medium mb-2">범례</p>
        <div className="flex flex-wrap gap-4 text-xs text-gray-600">
          {summit && (
            <span className="flex items-center gap-1">
              <span className="w-4 h-4 rounded-full bg-yellow-500 flex items-center justify-center text-[8px]">⛰️</span> 정상
            </span>
          )}
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-500"></span> 출발점
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-red-500"></span> 종점
          </span>
          <span className="flex items-center gap-1">
            <span className="w-4 h-0.5 bg-blue-500"></span> 탐방로
          </span>
        </div>
        <p className="mt-3 text-xs text-gray-400">
          * {data.source || '국립공원공단 탐방로 공간데이터 API'} 기반
        </p>
      </div>
    </div>
  );
}

// 산림청 지도 컴포넌트 (기존 로직)
function ForestServiceMap({ data }: { data: TrailData }) {
  const trackLatLngs: [number, number][] = data.track.map(([lon, lat]) => [lat, lon]);
  const startPoint = trackLatLngs[0];
  const endPoint = trackLatLngs[trackLatLngs.length - 1];

  const bounds: L.LatLngBoundsExpression = [
    [data.bounds.southwest[1], data.bounds.southwest[0]],
    [data.bounds.northeast[1], data.bounds.northeast[0]]
  ];

  return (
    <div className="space-y-4">
      {/* 지도 정보 헤더 */}
      <div className="bg-white rounded-2xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-emerald-500 font-medium">📏 총 거리</span>
            <span className="text-gray-700">{data.total_distance_km.toFixed(1)} km</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-blue-500 font-medium">📍 트랙 포인트</span>
            <span className="text-gray-700">{data.point_count.toLocaleString()}개</span>
          </div>
          {data.waypoint_count > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-orange-500 font-medium">🚩 주요 지점</span>
              <span className="text-gray-700">{data.waypoint_count}개</span>
            </div>
          )}
          {data.summit && (
            <div className="flex items-center gap-2">
              <span className="text-yellow-600 font-medium">⛰️ 정상</span>
              <span className="text-gray-700">{data.summit.elevation.toLocaleString()}m</span>
            </div>
          )}
        </div>
      </div>

      {/* 지도 */}
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <MapContainer
          center={[data.center[1], data.center[0]]}
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
          {data.summit && (
            <Marker
              position={[data.summit.coordinates[1], data.summit.coordinates[0]]}
              icon={summitIcon}
              zIndexOffset={1000}
            >
              <Popup>
                <div className="text-center">
                  <span className="font-bold text-yellow-600 text-lg">⛰️ 정상</span>
                  <p className="text-sm font-semibold mt-1">{data.mountain_name}</p>
                  <p className="text-sm text-gray-600">{data.summit.elevation.toLocaleString()}m</p>
                </div>
              </Popup>
            </Marker>
          )}

          {/* 웨이포인트 마커 */}
          {data.waypoints.map((wp, idx) => (
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

      {/* 코스 정보 (주요 지점 경로) */}
      {(data.waypoints.length > 0 || data.summit) && (
        <div className="bg-white rounded-2xl border border-gray-100 p-4">
          <h4 className="font-medium text-gray-800 mb-3">코스 정보</h4>
          <div className="p-3 bg-gray-50 rounded-lg">
            {/* 경로 텍스트 */}
            <div className="flex flex-wrap items-center gap-1 text-sm">
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                🟢 출발점
              </span>
              {data.waypoints.map((wp, idx) => {
                // 정상인지 확인 (summit과 같은 위치이거나 이름에 정상/봉 포함)
                const isSummit = data.summit && (
                  (Math.abs(wp.coordinates[0] - data.summit.coordinates[0]) < 0.0001 &&
                   Math.abs(wp.coordinates[1] - data.summit.coordinates[1]) < 0.0001) ||
                  (wp.name && /정상|봉$/.test(wp.name))
                );

                return (
                  <span key={idx} className="inline-flex items-center">
                    <span className="text-gray-400 mx-1">→</span>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                      isSummit
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-blue-100 text-blue-700'
                    }`}>
                      {isSummit ? '⛰️' : '📍'} {wp.name || `지점 ${idx + 1}`}
                      {wp.elevation > 0 && <span className="text-[10px] opacity-75">({wp.elevation}m)</span>}
                    </span>
                  </span>
                );
              })}
              {/* 정상이 waypoints에 없는 경우 별도 표시 */}
              {data.summit && !data.waypoints.some(wp =>
                Math.abs(wp.coordinates[0] - data.summit!.coordinates[0]) < 0.0001 &&
                Math.abs(wp.coordinates[1] - data.summit!.coordinates[1]) < 0.0001
              ) && (
                <span className="inline-flex items-center">
                  <span className="text-gray-400 mx-1">→</span>
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium">
                    ⛰️ 정상 <span className="text-[10px] opacity-75">({data.summit.elevation}m)</span>
                  </span>
                </span>
              )}
              <span className="inline-flex items-center">
                <span className="text-gray-400 mx-1">→</span>
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                  🔴 종점
                </span>
              </span>
            </div>

            {/* 상세 정보 */}
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div>
                  <span className="text-gray-500">총 거리</span>
                  <p className="font-medium text-gray-800">{data.total_distance_km.toFixed(1)} km</p>
                </div>
                {data.summit && (
                  <div>
                    <span className="text-gray-500">정상 고도</span>
                    <p className="font-medium text-gray-800">{data.summit.elevation.toLocaleString()} m</p>
                  </div>
                )}
                <div>
                  <span className="text-gray-500">주요 지점</span>
                  <p className="font-medium text-gray-800">{data.waypoint_count}개</p>
                </div>
                <div>
                  <span className="text-gray-500">트랙 포인트</span>
                  <p className="font-medium text-gray-800">{data.point_count.toLocaleString()}개</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

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
