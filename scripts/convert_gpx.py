#!/usr/bin/env python3
"""
GPX to JSON 변환 스크립트

램블러, 트랭글 등에서 다운로드한 GPX 파일을
블랙야크 100대 명산 트래커 형식의 JSON으로 변환합니다.

Usage:
    python convert_gpx.py --input 가리산.gpx --blackyak-id 1
    python convert_gpx.py --input 가리산.gpx --blackyak-id 1 --name "가리산(홍천)"
    python convert_gpx.py --input ./gpx_files/ --batch  # 폴더 내 모든 GPX 변환
"""

import argparse
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


def parse_gpx(gpx_path: Path) -> dict:
    """GPX 파일 파싱"""
    tree = ET.parse(gpx_path)
    root = tree.getroot()

    # GPX 네임스페이스 처리
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

    # 네임스페이스가 없는 경우도 처리
    if root.tag.startswith('{'):
        ns_uri = root.tag.split('}')[0] + '}'
        ns = {'gpx': ns_uri[1:-1]}
    else:
        ns = {}

    def find_with_ns(element, tag):
        """네임스페이스 유무에 관계없이 태그 찾기"""
        if ns:
            result = element.findall(f'gpx:{tag}', ns)
            if result:
                return result
        return element.findall(tag)

    def find_one_with_ns(element, tag):
        """네임스페이스 유무에 관계없이 단일 태그 찾기"""
        if ns:
            result = element.find(f'gpx:{tag}', ns)
            if result is not None:
                return result
        return element.find(tag)

    track_points = []
    waypoints = []

    # 트랙 포인트 추출 (trk > trkseg > trkpt)
    for trk in find_with_ns(root, 'trk') or [root]:
        for trkseg in find_with_ns(trk, 'trkseg') or [trk]:
            for trkpt in find_with_ns(trkseg, 'trkpt'):
                lat = float(trkpt.get('lat'))
                lon = float(trkpt.get('lon'))

                ele_elem = find_one_with_ns(trkpt, 'ele')
                ele = float(ele_elem.text) if ele_elem is not None and ele_elem.text else 0.0

                track_points.append({
                    'coordinates': [lon, lat],
                    'elevation': ele
                })

    # 웨이포인트 추출 (wpt)
    for wpt in find_with_ns(root, 'wpt'):
        lat = float(wpt.get('lat'))
        lon = float(wpt.get('lon'))

        name_elem = find_one_with_ns(wpt, 'name')
        name = name_elem.text if name_elem is not None and name_elem.text else ''

        ele_elem = find_one_with_ns(wpt, 'ele')
        ele = float(ele_elem.text) if ele_elem is not None and ele_elem.text else 0.0

        waypoints.append({
            'coordinates': [lon, lat],
            'name': name,
            'elevation': ele
        })

    # 경로(rte > rtept)도 확인 (일부 GPX는 track 대신 route 사용)
    if not track_points:
        for rte in find_with_ns(root, 'rte') or []:
            for rtept in find_with_ns(rte, 'rtept'):
                lat = float(rtept.get('lat'))
                lon = float(rtept.get('lon'))

                ele_elem = find_one_with_ns(rtept, 'ele')
                ele = float(ele_elem.text) if ele_elem is not None and ele_elem.text else 0.0

                track_points.append({
                    'coordinates': [lon, lat],
                    'elevation': ele
                })

    return {
        'track_points': track_points,
        'waypoints': waypoints
    }


def haversine_distance(coord1: list, coord2: list) -> float:
    """두 좌표 사이의 거리 계산 (km)"""
    R = 6371  # 지구 반지름 (km)

    lon1, lat1 = coord1
    lon2, lat2 = coord2

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def calculate_total_distance(track_points: list) -> float:
    """트랙 포인트로부터 총 거리 계산 (km)"""
    total = 0.0
    for i in range(1, len(track_points)):
        total += haversine_distance(
            track_points[i-1]['coordinates'],
            track_points[i]['coordinates']
        )
    return total


def calculate_bounds(track_points: list) -> dict:
    """트랙 포인트로부터 경계 계산"""
    if not track_points:
        return None

    lons = [p['coordinates'][0] for p in track_points]
    lats = [p['coordinates'][1] for p in track_points]

    return {
        'southwest': [min(lons), min(lats)],
        'northeast': [max(lons), max(lats)]
    }


def calculate_center(bounds: dict) -> list:
    """경계로부터 중심점 계산"""
    if not bounds:
        return None

    center_lon = (bounds['southwest'][0] + bounds['northeast'][0]) / 2
    center_lat = (bounds['southwest'][1] + bounds['northeast'][1]) / 2

    return [center_lon, center_lat]


def find_summit_from_track(track_points: list) -> dict:
    """트랙 포인트에서 가장 높은 지점을 정상으로 추정"""
    if not track_points:
        return None

    max_elevation = 0
    summit_point = None

    for point in track_points:
        if point['elevation'] > max_elevation:
            max_elevation = point['elevation']
            summit_point = point

    if summit_point and max_elevation > 0:
        return {
            'coordinates': summit_point['coordinates'],
            'elevation': max_elevation
        }

    return None


def load_mountain_info(blackyak_id: int, script_dir: Path) -> Optional[dict]:
    """mountain_info JSON에서 산 정보 로드"""
    info_path = script_dir.parent / 'frontend' / 'public' / 'mountain_info' / f'{blackyak_id}.json'

    if info_path.exists():
        with open(info_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    return None


def convert_gpx_to_json(
    gpx_path: Path,
    blackyak_id: int,
    mountain_name: Optional[str] = None,
    output_dir: Optional[Path] = None,
    script_dir: Optional[Path] = None
) -> dict:
    """GPX 파일을 JSON으로 변환"""

    # GPX 파싱
    gpx_data = parse_gpx(gpx_path)
    track_points = gpx_data['track_points']
    waypoints = gpx_data['waypoints']

    if not track_points:
        raise ValueError(f"GPX 파일에 트랙 포인트가 없습니다: {gpx_path}")

    # 산 정보 로드
    if script_dir:
        mountain_info = load_mountain_info(blackyak_id, script_dir)
    else:
        mountain_info = None

    # 산 이름 결정
    if not mountain_name:
        if mountain_info:
            mountain_name = mountain_info.get('blackyak_name', gpx_path.stem)
        else:
            mountain_name = gpx_path.stem

    # 거리, 경계, 중심점 계산
    total_distance = calculate_total_distance(track_points)
    bounds = calculate_bounds(track_points)
    center = calculate_center(bounds)

    # 정상 정보 (mountain_info에서 가져오거나 트랙에서 추정)
    summit = None
    if mountain_info and mountain_info.get('latitude') and mountain_info.get('longitude'):
        summit = {
            'coordinates': [mountain_info['longitude'], mountain_info['latitude']],
            'elevation': mountain_info.get('altitude', 0) or 0
        }
    else:
        summit = find_summit_from_track(track_points)

    # 웨이포인트 정리 (이름이 없는 경우 번호 부여)
    cleaned_waypoints = []
    for i, wp in enumerate(waypoints):
        cleaned_waypoints.append({
            'coordinates': wp['coordinates'],
            'name': wp['name'] if wp['name'] else f'지점 {i+1}',
            'elevation': wp['elevation']
        })

    # JSON 구조 생성
    result = {
        'mountain_name': mountain_name,
        'mnt_code': f'gpx_{blackyak_id}',  # GPX 파일은 mnt_code 대신 gpx_ 접두사
        'blackyak_id': blackyak_id,
        'source': 'gpx_upload',
        'source_file': gpx_path.name,
        'track': [p['coordinates'] for p in track_points],
        'waypoints': cleaned_waypoints,
        'center': center,
        'bounds': bounds,
        'total_distance_km': round(total_distance, 2),
        'point_count': len(track_points),
        'waypoint_count': len(cleaned_waypoints),
        'summit': summit
    }

    # 파일 저장
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f'gpx_{blackyak_id}.json'

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)

        print(f"✅ 변환 완료: {output_path}")
        print(f"   산: {mountain_name}")
        print(f"   트랙 포인트: {len(track_points)}개")
        print(f"   웨이포인트: {len(cleaned_waypoints)}개")
        print(f"   총 거리: {total_distance:.2f}km")
        if summit:
            print(f"   정상: {summit['elevation']}m")

    return result


def update_trail_index(output_dir: Path, trail_data: dict):
    """index.json 업데이트"""
    index_path = output_dir / 'index.json'

    # 기존 인덱스 로드
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = []

    # 기존 항목 찾기
    existing_idx = None
    for i, item in enumerate(index):
        if item.get('blackyak_id') == trail_data['blackyak_id']:
            existing_idx = i
            break

    new_entry = {
        'mountain_name': trail_data['mountain_name'],
        'mnt_code': trail_data['mnt_code'],
        'blackyak_id': trail_data['blackyak_id'],
        'distance_km': trail_data['total_distance_km']
    }

    if existing_idx is not None:
        index[existing_idx] = new_entry
        print(f"   인덱스 업데이트: {trail_data['mountain_name']}")
    else:
        index.append(new_entry)
        print(f"   인덱스 추가: {trail_data['mountain_name']}")

    # 이름순 정렬
    index.sort(key=lambda x: x['mountain_name'])

    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='GPX 파일을 블랙야크 100대 명산 트래커 JSON 형식으로 변환',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 단일 파일 변환
  python convert_gpx.py --input 가리산.gpx --blackyak-id 1

  # 산 이름 직접 지정
  python convert_gpx.py --input 가리산.gpx --blackyak-id 1 --name "가리산(홍천)"

  # 출력 디렉토리 지정
  python convert_gpx.py --input 가리산.gpx --blackyak-id 1 --output ./trails/

GPX 파일 다운로드 방법:
  - 램블러: 앱 > 기록 > 공유 > GPX 내보내기
  - 트랭글: 앱 > 나의 기록 > 공유 > GPX 파일
  - AllTrails: 웹 > 트레일 > Download GPX
        """
    )

    parser.add_argument('--input', '-i', required=True, help='GPX 파일 경로')
    parser.add_argument('--blackyak-id', '-b', type=int, required=True, help='블랙야크 100대 명산 ID (1-100)')
    parser.add_argument('--name', '-n', help='산 이름 (미지정시 자동 감지)')
    parser.add_argument('--output', '-o', help='출력 디렉토리 (기본: frontend/public/trails/)')
    parser.add_argument('--no-index', action='store_true', help='index.json 업데이트 안함')

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    gpx_path = Path(args.input)

    if not gpx_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {gpx_path}")
        return

    # 출력 디렉토리 설정
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = script_dir.parent / 'frontend' / 'public' / 'trails'

    try:
        # GPX 변환
        trail_data = convert_gpx_to_json(
            gpx_path=gpx_path,
            blackyak_id=args.blackyak_id,
            mountain_name=args.name,
            output_dir=output_dir,
            script_dir=script_dir
        )

        # 인덱스 업데이트
        if not args.no_index:
            update_trail_index(output_dir, trail_data)

        print(f"\n🎉 완료! 이제 해당 산 페이지에서 등산로를 볼 수 있습니다.")

    except Exception as e:
        print(f"❌ 변환 실패: {e}")
        raise


if __name__ == '__main__':
    main()
