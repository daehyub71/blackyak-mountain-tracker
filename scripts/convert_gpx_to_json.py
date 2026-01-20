#!/usr/bin/env python3
"""
GPX 파일을 프론트엔드용 JSON으로 변환하는 스크립트
- 매핑된 블랙야크 100대 명산의 GPX 파일을 읽어서 GeoJSON 형식으로 변환
- frontend/public/trails 디렉토리에 저장

Usage:
    python convert_gpx_to_json.py
"""

import os
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
import pandas as pd


# 매핑 정보 (blackyak_mnt_code_mapping.md 기반)
MOUNTAIN_MNT_CODE_MAPPING = {
    '가리왕산': 427700101,
    '가지산': 317100101,
    '감악산(원주)': 421303001,
    '감악산(파주)': 414800101,
    '계방산': 427206801,
    '관악산': 116200201,
    '광덕산': 441300301,
    '구병산(보은)': 437200401,
    '구봉산(진안)': 457200201,
    '금수산': 438002601,
    '금오산(구미)': 471900101,
    '남산(경주)': 478200601,
    '내연산': 471100801,
    '달마산': 468200701,
    '대둔산': 447103401,
    '대야산': 472800901,
    '덕룡산': 468100501,
    '덕항산': 421900601,
    '도락산': 438002801,
    '도봉산': 482501001,
    '두타산': 422301901,
    '마니산(강화도)': 287100601,
    '마이산(진안)': 457200901,
    '명지산': 418201401,
    '모악산': 451103301,
    '민주지산': 437401401,
    '방장산': 457900601,
    '방태산': 428102201,
    '백덕산': 427505801,
    '백운산(광양)': 457301401,
    '백운산(동강)': 427708601,
    '북한산': 114100801,
    '불갑산(영광)': 468600801,
    '비슬산': 277101501,
    '삼악산': 421102701,
    '소요산': 412500201,
    '수락산': 113500201,
    '신불산': 317102401,
    '연인산': 418202901,
    '오봉산(춘천)': 421103801,
    '오서산(보령)': 441801701,
    '용문산(양평)': 418303101,
    '용화산': 421302101,
    '운악산': 416502601,
    '운장산': 457202301,
    '유명산': 418303301,
    '응봉산(울진)': 422305301,
    '재약산': 482704101,
    '조령산': 437602101,
    '주왕산': 477502301,
    '주흘산': 472803901,
    '천관산': 468001701,
    '천마산': 413602201,
    '천태산': 437403501,
    '청량산': 481502601,
    '청화산': 437603301,
    '칠갑산(청양)': 447902001,
    '칠보산(괴산)': 437603901,
    '태화산': 427504901,
    '팔봉산': 421106201,
    '팔영산': 468400801,
    '화악산': 418200501,
    '화왕산(창녕)': 484802001,
    '황매산': 488500301,
    '황석산': 488802001,
    '황악산': 437400201,
    '황장산': 437200501,
    '희양산': 437603201,
}


def parse_gpx_from_zip(zip_path: str) -> dict:
    """ZIP 파일에서 GPX 파일을 파싱하여 GeoJSON 형식으로 반환"""
    result = {
        'track_points': [],
        'track_elevations': [],  # 고도 데이터 추가
        'waypoints': [],
        'name': '',
        'bounds': None,
        'center': None,
        'total_distance_km': 0.0,
        'summit': None,  # 정상 (최고 고도 지점)
    }

    if not os.path.exists(zip_path):
        return result

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for info in zf.infolist():
                # 파일명 인코딩 처리
                try:
                    name = info.filename.encode('cp437').decode('euc-kr')
                except:
                    name = info.filename

                if name.lower().endswith('.gpx'):
                    content = zf.read(info.filename)
                    parse_gpx_content(content, result)
    except Exception as e:
        print(f"  Error parsing {zip_path}: {e}")

    # 중심점과 경계 계산
    if result['track_points']:
        calculate_bounds_and_center(result)
        calculate_distance(result)

    return result


def parse_gpx_content(content: bytes, result: dict) -> None:
    """GPX XML 내용 파싱"""
    try:
        root = ET.fromstring(content)
    except:
        return

    # XML 네임스페이스 처리
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

    # 트랙 이름
    trk_name = root.find('.//gpx:trk/gpx:name', ns)
    if trk_name is not None and trk_name.text:
        result['name'] = trk_name.text

    # 트랙 포인트 파싱 (등산로 경로)
    prev_lat, prev_lon = None, None
    max_elevation = -9999
    summit_point = None

    for trkpt in root.findall('.//gpx:trkpt', ns):
        lat = float(trkpt.get('lat', 0))
        lon = float(trkpt.get('lon', 0))
        ele_elem = trkpt.find('gpx:ele', ns)
        try:
            ele = float(ele_elem.text) if ele_elem is not None and ele_elem.text.strip() else 0
        except:
            ele = 0

        # 중복 좌표 제거
        if prev_lat != lat or prev_lon != lon:
            result['track_points'].append([lon, lat])  # GeoJSON은 [lon, lat] 순서
            result['track_elevations'].append(ele)
            prev_lat, prev_lon = lat, lon

            # 최고 고도 지점 (정상) 찾기
            if ele > max_elevation:
                max_elevation = ele
                summit_point = {'coordinates': [lon, lat], 'elevation': ele}

    # 정상 저장
    if summit_point and max_elevation > 0:
        result['summit'] = summit_point

    # 웨이포인트 파싱 (주요 지점)
    for wpt in root.findall('.//gpx:wpt', ns):
        lat = float(wpt.get('lat', 0))
        lon = float(wpt.get('lon', 0))
        ele_elem = wpt.find('gpx:ele', ns)
        try:
            ele = float(ele_elem.text) if ele_elem is not None and ele_elem.text.strip() else 0
        except:
            ele = 0
        name_elem = wpt.find('gpx:name', ns)
        name = name_elem.text if name_elem is not None else ""

        result['waypoints'].append({
            'coordinates': [lon, lat],
            'name': name,
            'elevation': ele
        })


def calculate_bounds_and_center(result: dict) -> None:
    """경계와 중심점 계산"""
    if not result['track_points']:
        return

    lons = [p[0] for p in result['track_points']]
    lats = [p[1] for p in result['track_points']]

    result['bounds'] = {
        'southwest': [min(lons), min(lats)],
        'northeast': [max(lons), max(lats)]
    }
    result['center'] = [
        (min(lons) + max(lons)) / 2,
        (min(lats) + max(lats)) / 2
    ]


def calculate_distance(result: dict) -> None:
    """총 거리 계산 (하버사인 공식)"""
    from math import radians, sin, cos, sqrt, atan2

    def haversine(lon1, lat1, lon2, lat2):
        R = 6371  # 지구 반경 (km)
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    total = 0
    points = result['track_points']
    for i in range(1, len(points)):
        total += haversine(points[i-1][0], points[i-1][1], points[i][0], points[i][1])

    result['total_distance_km'] = round(total, 2)


def main():
    """메인 함수"""
    # 경로 설정
    script_dir = Path(__file__).parent
    raw_mountain_dir = script_dir.parent / 'data' / 'raw' / 'mountain'
    output_dir = script_dir.parent / 'frontend' / 'public' / 'trails'
    blackyak_csv = script_dir.parent / 'data' / 'raw' / 'blackyak_100.csv'

    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)

    # 블랙야크 100대 명산 정보 로드
    blackyak_df = pd.read_csv(blackyak_csv)

    print("🗺️ GPX를 JSON으로 변환 중...")
    print("-" * 50)

    # 매핑 인덱스 생성 (산 이름 -> 블랙야크 정보)
    name_to_info = {}
    for _, row in blackyak_df.iterrows():
        name_to_info[row['name']] = {
            'id': row['id'],
            'latitude': row.get('latitude'),
            'longitude': row.get('longitude'),
            'altitude': row.get('altitude'),
        }

    converted_count = 0
    trail_index = []  # 변환된 트레일 목록

    for mountain_name, mnt_code in MOUNTAIN_MNT_CODE_MAPPING.items():
        gpx_zip_path = raw_mountain_dir / f"{mnt_code}_gpx.zip"

        if not gpx_zip_path.exists():
            print(f"  ⚠️ {mountain_name}: GPX 파일 없음 ({mnt_code})")
            continue

        # GPX 파싱
        trail_data = parse_gpx_from_zip(str(gpx_zip_path))

        if not trail_data['track_points']:
            print(f"  ⚠️ {mountain_name}: 트랙 포인트 없음")
            continue

        # 블랙야크 정보 찾기 (ID, 정상 좌표, 고도)
        blackyak_info = name_to_info.get(mountain_name)
        if not blackyak_info:
            # 괄호 없는 이름으로도 시도
            clean_name = mountain_name.split('(')[0] if '(' in mountain_name else mountain_name
            for name, info in name_to_info.items():
                if clean_name in name:
                    blackyak_info = info
                    break

        blackyak_id = blackyak_info['id'] if blackyak_info else None

        # 정상 데이터 설정 (CSV의 좌표 및 고도 사용)
        summit_data = None
        if blackyak_info:
            lat = blackyak_info.get('latitude')
            lon = blackyak_info.get('longitude')
            alt = blackyak_info.get('altitude')
            if lat and lon and pd.notna(lat) and pd.notna(lon):
                summit_data = {
                    'coordinates': [float(lon), float(lat)],  # GeoJSON [lon, lat]
                    'elevation': int(alt) if alt and pd.notna(alt) else 0
                }

        # JSON 파일로 저장 (산코드 기반)
        output_file = output_dir / f"{mnt_code}.json"

        output_data = {
            'mountain_name': mountain_name,
            'mnt_code': mnt_code,
            'blackyak_id': blackyak_id,
            'track': trail_data['track_points'],
            'waypoints': trail_data['waypoints'],
            'center': trail_data['center'],
            'bounds': trail_data['bounds'],
            'total_distance_km': trail_data['total_distance_km'],
            'point_count': len(trail_data['track_points']),
            'waypoint_count': len(trail_data['waypoints']),
            'summit': summit_data,  # CSV 기반 정상 좌표
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False)

        trail_index.append({
            'mountain_name': mountain_name,
            'mnt_code': mnt_code,
            'blackyak_id': blackyak_id,
            'distance_km': trail_data['total_distance_km'],
        })

        converted_count += 1
        print(f"  ✅ {mountain_name}: {len(trail_data['track_points'])} 포인트, {trail_data['total_distance_km']}km")

    # 인덱스 파일 저장
    index_file = output_dir / 'index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(trail_index, f, ensure_ascii=False, indent=2)

    print("-" * 50)
    print(f"\n✅ 변환 완료: {converted_count}개 산")
    print(f"📁 출력 디렉토리: {output_dir}")


if __name__ == '__main__':
    main()
