#!/usr/bin/env python3
"""
국립공원공단 탐방로 공간데이터 API를 사용하여 등산로 정보를 수집하는 스크립트

Usage:
    python fetch_national_park_trails.py
"""

import json
import requests
import os
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
import time

load_dotenv()

API_KEY = os.getenv('DATA_GO_KR_API_KEY')
API_URL = 'https://api.odcloud.kr/api/15003467/v1/uddi:33b2e50e-6039-4649-a9da-8d5b89180b78_201709281349'

# 블랙야크 100대 명산 중 국립공원 산 목록 (공원사무소코드 매핑)
# 2024-01 API 데이터 기준 좌표 분석으로 검증된 매핑
NATIONAL_PARK_MOUNTAINS = {
    '지리산': {'park_codes': [101], 'blackyak_id': 75},           # 51개 코스
    '설악산': {'park_codes': [401], 'blackyak_id': 49},           # 18개 코스
    '북한산': {'park_codes': [1501], 'blackyak_id': 44},          # 96개 코스
    '계룡산': {'park_codes': [201, 1101], 'blackyak_id': 8},      # 24개 코스
    '속리산': {'park_codes': [501], 'blackyak_id': 52},           # 21개 코스
    '내장산': {'park_codes': [601], 'blackyak_id': 20},           # 17개 코스
    '덕유산': {'park_codes': [801], 'blackyak_id': 25},           # 13개 코스
    '주왕산': {'park_codes': [1001], 'blackyak_id': 73},          # 15개 코스
    '치악산': {'park_codes': [1301], 'blackyak_id': 85},          # 11개 코스
    '월악산': {'park_codes': [1401], 'blackyak_id': 65},          # 14개 코스
    '소백산': {'park_codes': [1601], 'blackyak_id': 50},          # 18개 코스
    '오대산': {'park_codes': [901], 'blackyak_id': 56},           # 9개 코스
    '가야산': {'park_codes': [701], 'blackyak_id': 3},            # 8개 코스
    '무등산': {'park_codes': [2101], 'blackyak_id': 36},          # 1개 코스
    '월출산': {'park_codes': [1701], 'blackyak_id': 66},          # 8개 코스
    '한라산': {'park_codes': [2001], 'blackyak_id': 93},          # 9개 코스
    # 태백산은 국립공원이 아닌 도립공원이라 API에 없음
}


def fetch_all_trail_data():
    """API에서 모든 탐방로 데이터 가져오기"""
    all_data = []
    page = 1
    per_page = 1000

    print("🏔️ 국립공원 탐방로 데이터 수집 중...")

    while True:
        params = {
            'serviceKey': API_KEY,
            'page': page,
            'perPage': per_page,
        }

        try:
            response = requests.get(API_URL, params=params, timeout=60)
            data = response.json()

            items = data.get('data', [])
            if not items:
                break

            all_data.extend(items)
            total = data.get('totalCount', 0)

            print(f"  페이지 {page}: {len(all_data)}/{total} 수집 완료", end='\r')

            if len(all_data) >= total:
                break

            page += 1
            time.sleep(0.1)  # API 부하 방지

        except Exception as e:
            print(f"\n  에러 발생: {e}")
            break

    print(f"\n✅ 총 {len(all_data)}개 좌표 포인트 수집 완료")
    return all_data


def group_by_course(data):
    """코스별로 데이터 그룹화"""
    courses = defaultdict(list)

    for item in data:
        course_name = item.get('탐방코스(한글)', '')
        if course_name:
            courses[course_name].append({
                'lat': float(item.get('위도', 0)),
                'lon': float(item.get('경도', 0)),
                'seq': item.get('일련번호', 0),
                'park_code': item.get('공원사무소코드', 0),
                'detail': item.get('상세구간', ''),
                'difficulty': item.get('난이도', ''),
                'distance': item.get('GIS 상 거리(m)', '0'),
            })

    return courses


def convert_to_geojson(course_name, points):
    """코스 포인트를 GeoJSON 형식으로 변환"""
    # 일련번호로 정렬
    sorted_points = sorted(points, key=lambda x: x['seq'])

    # 좌표 배열 생성 [lon, lat]
    coordinates = [[p['lon'], p['lat']] for p in sorted_points if p['lat'] and p['lon']]

    if not coordinates:
        return None

    # 총 거리 계산 (미터)
    total_distance = sum(float(p.get('distance', 0) or 0) for p in sorted_points)

    return {
        'type': 'Feature',
        'properties': {
            'name': course_name,
            'detail': sorted_points[0].get('detail', '') if sorted_points else '',
            'difficulty': sorted_points[0].get('difficulty', '') if sorted_points else '',
            'distance_m': total_distance,
            'point_count': len(coordinates),
        },
        'geometry': {
            'type': 'LineString',
            'coordinates': coordinates,
        }
    }


def save_trail_json(mountain_name, blackyak_id, courses, output_dir):
    """산별 등산로 JSON 저장"""
    features = []

    for course_name, points in courses.items():
        feature = convert_to_geojson(course_name, points)
        if feature:
            features.append(feature)

    if not features:
        return None

    # 첫 번째 코스의 좌표로 중심점 계산
    all_coords = []
    for f in features:
        all_coords.extend(f['geometry']['coordinates'])

    if all_coords:
        center_lon = sum(c[0] for c in all_coords) / len(all_coords)
        center_lat = sum(c[1] for c in all_coords) / len(all_coords)
    else:
        center_lon, center_lat = 0, 0

    trail_data = {
        'mountain_name': mountain_name,
        'blackyak_id': blackyak_id,
        'source': 'national_park_api',
        'trail_count': len(features),
        'center': [center_lon, center_lat],
        'features': features,
    }

    # 저장
    filename = f'np_{blackyak_id}.json'
    filepath = output_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(trail_data, f, ensure_ascii=False, indent=2)

    return filepath


def main():
    """메인 함수"""
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / 'frontend' / 'public' / 'trails'
    output_dir.mkdir(parents=True, exist_ok=True)

    # 모든 데이터 수집
    all_data = fetch_all_trail_data()

    if not all_data:
        print("❌ 데이터를 가져오지 못했습니다.")
        return

    # 코스별 그룹화
    courses = group_by_course(all_data)
    print(f"\n📊 총 {len(courses)}개 코스 발견")

    # 공원사무소코드별로 코스 분류 (정확한 코드 매칭)
    park_courses = defaultdict(dict)
    for course_name, points in courses.items():
        if points:
            park_code = points[0].get('park_code', 0)
            park_courses[park_code][course_name] = points

    # 국립공원 산별로 저장
    print("\n🗂️ 산별 등산로 저장 중...")
    saved_count = 0

    for mountain_name, info in NATIONAL_PARK_MOUNTAINS.items():
        mountain_courses = {}

        for park_code in info['park_codes']:
            if park_code in park_courses:
                mountain_courses.update(park_courses[park_code])

        if mountain_courses:
            filepath = save_trail_json(
                mountain_name,
                info['blackyak_id'],
                mountain_courses,
                output_dir
            )
            if filepath:
                print(f"  ✅ {mountain_name}: {len(mountain_courses)}개 코스 저장")
                saved_count += 1
        else:
            print(f"  ⚠️ {mountain_name}: 코스 없음")

    print(f"\n✅ 완료: {saved_count}개 산의 등산로 저장됨")
    print(f"📁 출력 디렉토리: {output_dir}")


if __name__ == '__main__':
    main()
