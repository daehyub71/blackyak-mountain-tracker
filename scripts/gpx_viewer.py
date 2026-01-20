#!/usr/bin/env python3
"""
GPX 등산로 시각화 프로그램
- GPX 파일을 읽어서 지도에 등산로와 주요 지점을 표시합니다.
- Folium을 사용하여 인터랙티브 HTML 지도를 생성합니다.

Usage:
    python gpx_viewer.py <gpx_zip_path>
    python gpx_viewer.py /Users/sunchulkim/Downloads/427700101_gpx.zip

Options:
    -e, --elevation    외부 API로 고도 데이터를 조회하여 정상 표시
                       (GPX 파일에 고도 데이터가 없을 때 사용)

Examples:
    python gpx_viewer.py /path/to/gpx.zip --elevation
"""

import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# 필요한 패키지 설치 확인
try:
    import folium
    from folium import plugins
except ImportError:
    print("folium 패키지가 필요합니다. 설치 중...")
    os.system("pip install folium")
    import folium
    from folium import plugins


@dataclass
class TrackPoint:
    """트랙 포인트 (등산로 경로)"""
    lat: float
    lon: float
    ele: float = 0


@dataclass
class WayPoint:
    """웨이포인트 (주요 지점)"""
    lat: float
    lon: float
    ele: float = 0
    name: str = ""
    desc: str = ""


class GPXParser:
    """GPX 파일 파서"""

    def __init__(self):
        self.track_points: list[TrackPoint] = []
        self.waypoints: list[WayPoint] = []
        self.name: str = ""

    def parse_file(self, gpx_content: bytes) -> None:
        """GPX XML 파싱"""
        root = ET.fromstring(gpx_content)

        # XML 네임스페이스 처리
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

        # 트랙 이름
        trk_name = root.find('.//gpx:trk/gpx:name', ns)
        if trk_name is not None and trk_name.text:
            self.name = trk_name.text

        # 트랙 포인트 파싱 (등산로 경로)
        for trkpt in root.findall('.//gpx:trkpt', ns):
            lat = float(trkpt.get('lat', 0))
            lon = float(trkpt.get('lon', 0))
            ele_elem = trkpt.find('gpx:ele', ns)
            ele = float(ele_elem.text) if ele_elem is not None and ele_elem.text.strip() else 0

            # 중복 좌표 제거 (연속으로 같은 좌표가 3번씩 반복됨)
            if not self.track_points or (self.track_points[-1].lat != lat or self.track_points[-1].lon != lon):
                self.track_points.append(TrackPoint(lat=lat, lon=lon, ele=ele))

        # 웨이포인트 파싱 (주요 지점)
        for wpt in root.findall('.//gpx:wpt', ns):
            lat = float(wpt.get('lat', 0))
            lon = float(wpt.get('lon', 0))
            ele_elem = wpt.find('gpx:ele', ns)
            ele = float(ele_elem.text) if ele_elem is not None and ele_elem.text.strip() else 0
            name_elem = wpt.find('gpx:name', ns)
            name = name_elem.text if name_elem is not None else ""
            desc_elem = wpt.find('gpx:desc', ns)
            desc = desc_elem.text if desc_elem is not None else ""

            self.waypoints.append(WayPoint(lat=lat, lon=lon, ele=ele, name=name, desc=desc))

    def get_center(self) -> tuple[float, float]:
        """지도 중심점 계산"""
        all_points = [(p.lat, p.lon) for p in self.track_points] + [(w.lat, w.lon) for w in self.waypoints]
        if not all_points:
            return (37.5665, 126.9780)  # 기본: 서울

        avg_lat = sum(p[0] for p in all_points) / len(all_points)
        avg_lon = sum(p[1] for p in all_points) / len(all_points)
        return (avg_lat, avg_lon)

    def get_bounds(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """지도 경계 계산 (min, max)"""
        all_points = [(p.lat, p.lon) for p in self.track_points] + [(w.lat, w.lon) for w in self.waypoints]
        if not all_points:
            return ((37.5, 126.9), (37.6, 127.0))

        min_lat = min(p[0] for p in all_points)
        max_lat = max(p[0] for p in all_points)
        min_lon = min(p[1] for p in all_points)
        max_lon = max(p[1] for p in all_points)
        return ((min_lat, min_lon), (max_lat, max_lon))

    def get_summit(self, use_elevation_api: bool = False) -> Optional['TrackPoint']:
        """정상 (최고 고도 지점) 찾기"""
        if not self.track_points:
            return None

        # 고도 데이터가 있는 포인트만 필터링
        points_with_ele = [p for p in self.track_points if p.ele > 0]

        if points_with_ele:
            # 기존 고도 데이터 사용
            return max(points_with_ele, key=lambda p: p.ele)

        # 고도 데이터가 없으면 외부 API 사용 (옵션)
        if use_elevation_api:
            return self._fetch_summit_from_api()

        return None

    def _fetch_summit_from_api(self) -> Optional['TrackPoint']:
        """외부 API로 정상 찾기 (Open-Elevation API 사용)"""
        import requests

        if not self.track_points:
            return None

        # 샘플링: 전체 포인트가 많으면 일부만 조회 (API 부하 감소)
        step = max(1, len(self.track_points) // 100)
        sample_points = self.track_points[::step]

        print(f"\n  🌐 외부 API로 고도 조회 중... ({len(sample_points)} 포인트)")

        try:
            # Open-Elevation API (무료, 제한 있음)
            locations = [{"latitude": p.lat, "longitude": p.lon} for p in sample_points]

            response = requests.post(
                "https://api.open-elevation.com/api/v1/lookup",
                json={"locations": locations},
                timeout=30
            )

            if response.status_code == 200:
                results = response.json().get("results", [])

                if results:
                    # 최고 고도 찾기
                    max_idx = max(range(len(results)), key=lambda i: results[i]["elevation"])
                    max_ele = results[max_idx]["elevation"]

                    summit_point = sample_points[max_idx]
                    return TrackPoint(
                        lat=summit_point.lat,
                        lon=summit_point.lon,
                        ele=max_ele
                    )
        except Exception as e:
            print(f"  ⚠️ 고도 API 조회 실패: {e}")

        return None

    def get_elevation_stats(self) -> dict:
        """고도 통계 계산"""
        if not self.track_points:
            return {}

        elevations = [p.ele for p in self.track_points if p.ele > 0]

        if not elevations:
            return {}

        return {
            'min_elevation': min(elevations),
            'max_elevation': max(elevations),
            'elevation_gain': self._calculate_elevation_gain(),
        }

    def _calculate_elevation_gain(self) -> float:
        """누적 상승 고도 계산"""
        total_gain = 0
        for i in range(1, len(self.track_points)):
            diff = self.track_points[i].ele - self.track_points[i-1].ele
            if diff > 0:
                total_gain += diff
        return round(total_gain, 1)


def extract_gpx_from_zip(zip_path: str) -> dict[str, bytes]:
    """ZIP 파일에서 GPX 파일 추출"""
    gpx_files = {}

    with zipfile.ZipFile(zip_path, 'r') as zf:
        for info in zf.infolist():
            # 파일명 인코딩 처리
            try:
                name = info.filename.encode('cp437').decode('euc-kr')
            except:
                name = info.filename

            if name.lower().endswith('.gpx'):
                content = zf.read(info.filename)
                gpx_files[name] = content
                print(f"  추출: {name}")

    return gpx_files


def create_trail_map(parser: GPXParser, output_path: str, summit: Optional['TrackPoint'] = None) -> str:
    """등산로 지도 생성"""

    # 지도 생성
    center = parser.get_center()
    m = folium.Map(
        location=center,
        zoom_start=13,
        tiles='OpenStreetMap'
    )

    # 다양한 타일 레이어 추가
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Maps'
    ).add_to(m)

    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite'
    ).add_to(m)

    # 등산로 경로 그리기 (Polyline)
    if parser.track_points:
        trail_coords = [(p.lat, p.lon) for p in parser.track_points]

        # 메인 등산로 (주황색)
        folium.PolyLine(
            trail_coords,
            weight=4,
            color='#FF6B35',
            opacity=0.8,
            popup=f'등산로: {parser.name}'
        ).add_to(m)

        # 시작점 마커 (녹색)
        start = trail_coords[0]
        folium.Marker(
            location=start,
            popup='<b>시작점</b>',
            icon=folium.Icon(color='green', icon='play', prefix='fa')
        ).add_to(m)

        # 종점 마커 (빨간색)
        end = trail_coords[-1]
        folium.Marker(
            location=end,
            popup='<b>종점</b>',
            icon=folium.Icon(color='red', icon='flag', prefix='fa')
        ).add_to(m)

    # 정상 마커 (최고 고도 지점) - 노란색 별
    if summit:
        folium.Marker(
            location=(summit.lat, summit.lon),
            popup=f'<b>⛰️ 정상</b><br>고도: {summit.ele:.1f}m<br>위도: {summit.lat:.6f}<br>경도: {summit.lon:.6f}',
            icon=folium.Icon(color='orange', icon='star', prefix='fa'),
            z_index_offset=1000  # 다른 마커보다 위에 표시
        ).add_to(m)

    # 주요 지점 마커
    waypoint_group = folium.FeatureGroup(name='주요 지점')
    for i, wp in enumerate(parser.waypoints, 1):
        folium.CircleMarker(
            location=(wp.lat, wp.lon),
            radius=8,
            color='#2563EB',
            fill=True,
            fill_color='#2563EB',
            fill_opacity=0.7,
            popup=f'<b>지점 {i}</b><br>위도: {wp.lat:.6f}<br>경도: {wp.lon:.6f}'
        ).add_to(waypoint_group)
    waypoint_group.add_to(m)

    # 지도 경계에 맞춤
    bounds = parser.get_bounds()
    m.fit_bounds([bounds[0], bounds[1]])

    # 레이어 컨트롤 추가
    folium.LayerControl().add_to(m)

    # 전체화면 버튼 추가
    plugins.Fullscreen().add_to(m)

    # 마우스 좌표 표시
    plugins.MousePosition().add_to(m)

    # 미니맵 추가
    plugins.MiniMap(toggle_display=True).add_to(m)

    # HTML 저장
    m.save(output_path)
    return output_path


def calculate_stats(parser: GPXParser, use_elevation_api: bool = False) -> dict:
    """등산로 통계 계산"""
    if not parser.track_points:
        return {}

    # 총 거리 계산 (하버사인 공식)
    from math import radians, sin, cos, sqrt, atan2

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # 지구 반경 (km)
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    total_distance = 0
    for i in range(1, len(parser.track_points)):
        p1 = parser.track_points[i-1]
        p2 = parser.track_points[i]
        total_distance += haversine(p1.lat, p1.lon, p2.lat, p2.lon)

    # 고도 통계
    elevation_stats = parser.get_elevation_stats()
    summit = parser.get_summit(use_elevation_api=use_elevation_api)

    return {
        'name': parser.name,
        'total_points': len(parser.track_points),
        'waypoints': len(parser.waypoints),
        'distance_km': round(total_distance, 2),
        'center': parser.get_center(),
        'summit': summit,
        'min_elevation': elevation_stats.get('min_elevation', 0),
        'max_elevation': elevation_stats.get('max_elevation', 0),
        'elevation_gain': elevation_stats.get('elevation_gain', 0),
    }


def main():
    """메인 함수"""

    # 기본 ZIP 파일 경로
    default_zip = '/Users/sunchulkim/Downloads/427700101_gpx.zip'

    # 인자 파싱
    use_elevation_api = '--elevation' in sys.argv or '-e' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('-')]

    if args:
        zip_path = args[0]
    else:
        zip_path = default_zip

    if not os.path.exists(zip_path):
        print(f"파일을 찾을 수 없습니다: {zip_path}")
        sys.exit(1)

    print(f"\n📂 GPX 파일 로드 중: {zip_path}")
    print("-" * 50)

    # GPX 파일 추출
    gpx_files = extract_gpx_from_zip(zip_path)

    if not gpx_files:
        print("GPX 파일이 없습니다.")
        sys.exit(1)

    # GPX 파싱
    parser = GPXParser()
    for name, content in gpx_files.items():
        print(f"\n  파싱 중: {name}")
        parser.parse_file(content)

    # 통계 출력
    stats = calculate_stats(parser, use_elevation_api=use_elevation_api)
    print("\n📊 등산로 정보")
    print("-" * 50)
    print(f"  이름: {stats.get('name', 'Unknown')}")
    print(f"  총 거리: {stats.get('distance_km', 0)} km")
    print(f"  경로 포인트: {stats.get('total_points', 0)} 개")
    print(f"  주요 지점: {stats.get('waypoints', 0)} 개")
    print(f"  중심 좌표: {stats.get('center', (0,0))}")

    # 고도 정보 출력
    summit = stats.get('summit')
    if summit:
        print(f"\n⛰️ 정상 정보")
        print("-" * 50)
        print(f"  정상 고도: {summit.ele:.1f} m")
        print(f"  정상 좌표: ({summit.lat:.6f}, {summit.lon:.6f})")
        # 파일 내 고도 데이터가 있는 경우에만 추가 정보 표시
        if stats.get('max_elevation', 0) > 0:
            print(f"  최저 고도: {stats.get('min_elevation', 0):.1f} m")
            print(f"  누적 상승: {stats.get('elevation_gain', 0):.1f} m")

    # 지도 생성
    output_dir = Path(zip_path).parent
    output_path = output_dir / f"{Path(zip_path).stem}_map.html"

    print(f"\n🗺️ 지도 생성 중...")
    create_trail_map(parser, str(output_path), summit=stats.get('summit'))

    print(f"\n✅ 완료!")
    print(f"  지도 파일: {output_path}")
    print(f"\n  브라우저에서 열기: open \"{output_path}\"")

    # 자동으로 브라우저에서 열기
    import webbrowser
    webbrowser.open(f"file://{output_path}")


if __name__ == '__main__':
    main()
