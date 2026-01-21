import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMountain, useTrails } from '../hooks/useMountains';
import { TrailMap } from '../components/TrailMap';
import type { MountainInfo } from '../types/mountain';

type TabType = 'info' | 'trails' | 'highlights';

export function MountainDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: mountain, isLoading, error } = useMountain(id);
  const { data: trails } = useTrails(id);
  const [activeTab, setActiveTab] = useState<TabType>('info');
  const [mountainInfo, setMountainInfo] = useState<MountainInfo | null>(null);

  // 산림청 산정보 로드
  useEffect(() => {
    if (!mountain?.name) return;

    const mountainName = mountain.name;

    async function loadMountainInfo() {
      try {
        const res = await fetch('/mountain_info/index.json');
        if (!res.ok) return;

        const allInfo: MountainInfo[] = await res.json();
        // 산 이름으로 매칭
        const info = allInfo.find(
          (m) => m.blackyak_name === mountainName || m.mntn_nm === mountainName
        );
        if (info) {
          setMountainInfo(info);
        }
      } catch {
        // 실패해도 기존 데이터로 표시
      }
    }

    loadMountainInfo();
  }, [mountain?.name]);

  if (isLoading) {
    return (
      <div className="min-h-screen">
        <div className="h-72 bg-slate-800 animate-pulse" />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/3" />
            <div className="h-4 bg-gray-200 rounded w-1/2" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !mountain) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <span className="text-6xl">❌</span>
          <h2 className="mt-4 text-xl font-semibold text-gray-900">
            산 정보를 찾을 수 없습니다
          </h2>
          <Link
            to="/"
            className="mt-4 inline-block text-primary hover:text-primary-dark"
          >
            목록으로 돌아가기
          </Link>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'info' as TabType, label: '산 정보' },
    { id: 'trails' as TabType, label: '등산 코스' },
    { id: 'highlights' as TabType, label: '주요 명소' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section - Dark Navy with Image */}
      <div className="relative bg-slate-900 overflow-hidden">
        {/* Background Image */}
        {mountain.image_url && (
          <div className="absolute inset-0">
            <img
              src={mountain.image_url}
              alt={mountain.name}
              className="w-full h-full object-cover opacity-40"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/80 to-slate-900/60" />
          </div>
        )}

        {/* Breadcrumb */}
        <div className="relative max-w-4xl mx-auto px-4 pt-4">
          <nav className="text-sm">
            <Link to="/" className="text-gray-400 hover:text-white transition-colors">
              산 목록
            </Link>
            <span className="mx-2 text-gray-600">›</span>
            <span className="text-gray-300">{mountain.name}</span>
          </nav>
        </div>

        {/* Hero Content */}
        <div className="relative max-w-4xl mx-auto px-4 py-12 pb-16">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6">
            {/* Left: Mountain Info */}
            <div>
              <span className="inline-block px-3 py-1 text-xs font-bold text-emerald-400 bg-emerald-400/10 border border-emerald-400/30 rounded-full mb-4">
                TOP 100 MOUNTAIN
              </span>
              <h1 className="text-3xl md:text-4xl font-bold text-white">
                {mountain.name}
              </h1>
              <p className="mt-2 text-gray-400">
                {mountain.region} {mountain.address && `· ${mountain.address}`}
              </p>
            </div>

            {/* Right: Elevation */}
            {mountain.altitude && (
              <div className="text-right">
                <p className="text-xs text-gray-500 uppercase tracking-wide">최고 높이</p>
                <p className="text-3xl md:text-4xl font-bold text-emerald-400">
                  {mountain.altitude.toLocaleString()}
                  <span className="text-lg ml-1">m</span>
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200 sticky top-14 z-40">
        <div className="max-w-4xl mx-auto px-4">
          <nav className="flex gap-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Tab: 산 정보 */}
        {activeTab === 'info' && (
          <div className="space-y-6">
            {/* 기본 정보 */}
            <div className="bg-white rounded-2xl p-6 border border-gray-100">
              <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
                <span className="w-2 h-2 bg-primary rounded-full"></span>
                기본 정보
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-start gap-3">
                  <span className="text-xl">⛰️</span>
                  <div>
                    <p className="text-xs text-gray-500">해발고도</p>
                    <p className="font-semibold text-gray-900">
                      {mountainInfo?.altitude || mountain.altitude
                        ? `${(mountainInfo?.altitude || mountain.altitude)?.toLocaleString()}m`
                        : '-'}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-xl">📍</span>
                  <div>
                    <p className="text-xs text-gray-500">소재지</p>
                    <p className="font-semibold text-gray-900">
                      {mountainInfo?.address || mountain.address || mountain.region}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-xl">🏅</span>
                  <div>
                    <p className="text-xs text-gray-500">인증 장소</p>
                    <p className="font-semibold text-gray-900">
                      {mountainInfo?.certification_point || mountain.certification_point || '정상'}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <span className="text-xl">🗺️</span>
                  <div>
                    <p className="text-xs text-gray-500">지역</p>
                    <p className="font-semibold text-gray-900">
                      {mountainInfo?.region || mountain.region}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* 산 소개 (위키피디아) */}
            {mountainInfo?.mntn_summary && (
              <div className="bg-white rounded-2xl p-6 border border-gray-100">
                <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
                  <span className="w-2 h-2 bg-primary rounded-full"></span>
                  산 소개
                </h2>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {mountainInfo.mntn_summary}
                </p>
                <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                  <span className="text-xs text-gray-400">
                    출처: <a
                      href={`https://ko.wikipedia.org/wiki/${encodeURIComponent(mountain.name.split('(')[0].trim().replace(/ /g, '_'))}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 hover:underline"
                    >
                      위키피디아
                    </a>
                  </span>
                  <a
                    href={`https://ko.wikipedia.org/wiki/${encodeURIComponent(mountain.name.split('(')[0].trim().replace(/ /g, '_'))}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-500 hover:underline flex items-center gap-1"
                  >
                    더 보기 →
                  </a>
                </div>
              </div>
            )}

            {/* 주변 관광정보 (산림청 API 데이터) */}
            {mountainInfo?.tourism_info && (
              <div className="bg-white rounded-2xl p-6 border border-gray-100">
                <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
                  <span className="w-2 h-2 bg-primary rounded-full"></span>
                  주변 관광정보
                </h2>
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {mountainInfo.tourism_info}
                </p>
              </div>
            )}

            {/* 상세 정보 */}
            <div className="bg-white rounded-2xl p-6 border border-gray-100">
              <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
                <span className="w-2 h-2 bg-primary rounded-full"></span>
                인증 정보
              </h2>
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-gray-700">
                  <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>블랙야크 100대 명산</span>
                </div>
                {mountain.certification_point && (
                  <div className="flex items-center gap-3 text-gray-700">
                    <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>인증 방법: {mountain.certification_point}</span>
                  </div>
                )}
                <div className="flex items-center gap-3 text-gray-700">
                  <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>산림청 선정 100대 명산</span>
                </div>
              </div>
            </div>

            {/* 관련 서비스 링크 */}
            <div className="bg-white rounded-2xl p-6 border border-gray-100">
              <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
                <span className="w-2 h-2 bg-primary rounded-full"></span>
                관련 서비스
              </h2>
              <div className="flex flex-wrap gap-3">
                {mountain.latitude && mountain.longitude && (
                  <>
                    <a
                      href={`https://map.naver.com/p/search/${encodeURIComponent(mountain.name)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2.5 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 transition-colors text-sm"
                    >
                      <span>🗺️</span>
                      네이버지도
                    </a>
                    <a
                      href={`https://map.kakao.com/link/map/${mountain.name},${mountain.latitude},${mountain.longitude}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2.5 bg-yellow-400 text-yellow-900 rounded-lg font-medium hover:bg-yellow-500 transition-colors text-sm"
                    >
                      <span>📍</span>
                      카카오맵
                    </a>
                  </>
                )}
              </div>
              <p className="mt-4 text-xs text-gray-500">
                * 상세 등산로 GPX는 램블러, 트랭글에서 "{mountain.name_origin || mountain.name}" 검색 후 다운로드하세요.
              </p>
            </div>
          </div>
        )}

        {/* Tab: 등산 코스 */}
        {activeTab === 'trails' && (
          <div className="space-y-6">
            {/* 등산로 지도 */}
            <div>
              <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
                <span className="w-2 h-2 bg-primary rounded-full"></span>
                등산로 지도
              </h2>
              <TrailMap
                mountainName={mountain.name}
                blackyakId={mountainInfo?.blackyak_id}
                certificationPoint={mountainInfo?.certification_point || mountain.certification_point || undefined}
              />
            </div>

            {/* 등산 코스 목록 */}
            {trails && trails.length > 0 && (
              <div>
                <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
                  <span className="w-2 h-2 bg-primary rounded-full"></span>
                  등산 코스
                </h2>
                <div className="space-y-4">
                  {trails.map((trail) => (
                    <div
                      key={trail.id}
                      className="bg-white rounded-2xl p-6 border border-gray-100"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                            {trail.name}
                            {trail.is_recommended && (
                              <span className="text-xs bg-primary text-white px-2 py-0.5 rounded-full">
                                추천
                              </span>
                            )}
                          </h3>
                          <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-600">
                            {trail.distance_km && (
                              <span className="flex items-center gap-1">
                                <span className="text-gray-400">📏</span>
                                {trail.distance_km}km
                              </span>
                            )}
                            {trail.estimated_time_minutes && (
                              <span className="flex items-center gap-1">
                                <span className="text-gray-400">⏱️</span>
                                {Math.floor(trail.estimated_time_minutes / 60)}시간 {trail.estimated_time_minutes % 60}분
                              </span>
                            )}
                            {trail.difficulty && (
                              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                trail.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                                trail.difficulty === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                                trail.difficulty === 'hard' ? 'bg-orange-100 text-orange-700' :
                                'bg-red-100 text-red-700'
                              }`}>
                                {trail.difficulty === 'easy' ? '쉬움' :
                                 trail.difficulty === 'moderate' ? '보통' :
                                 trail.difficulty === 'hard' ? '어려움' : '전문가'}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      {trail.description && (
                        <p className="mt-4 text-sm text-gray-600 leading-relaxed">{trail.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab: 주요 명소 */}
        {activeTab === 'highlights' && (
          <div className="bg-white rounded-2xl p-12 border border-gray-100 text-center">
            <span className="text-5xl">📸</span>
            <p className="mt-4 text-gray-600">등록된 명소 정보가 없습니다</p>
            <p className="mt-2 text-sm text-gray-400">
              곧 인증샷 명소, 경치 좋은 포인트 정보가 추가됩니다
            </p>
          </div>
        )}
      </div>

      {/* Call-to-Action Banner */}
      <div className="bg-slate-900 mt-8">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h3 className="text-xl font-bold text-white">
                이 산의 완등 기록을 남겨보세요!
              </h3>
              <p className="mt-1 text-gray-400 text-sm">
                회원가입 후 나만의 등산 지도와 기록을 관리할 수 있습니다.
              </p>
            </div>
            <button className="px-6 py-3 bg-white text-slate-900 rounded-lg font-semibold hover:bg-gray-100 transition-colors whitespace-nowrap">
              기록하기 시작
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
