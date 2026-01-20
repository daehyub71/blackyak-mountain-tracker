#!/usr/bin/env python3
"""
블랙야크 100대 명산 리스트 크롤링 스크립트 (공식 API 버전)

데이터 소스:
- 블랙야크 공식 사이트 API: https://bac.blackyak.com/BAC/ChallengeProgram/getlist.asp?program_id=114

사용법:
    python crawl_blackyak_100.py --output ../data/raw/blackyak_100.json
    python crawl_blackyak_100.py --output ../data/raw/blackyak_100.json --csv
"""

import argparse
import json
import re
from pathlib import Path
from typing import Optional

import requests


def fetch_official_data() -> str:
    """블랙야크 공식 API에서 데이터 가져오기"""
    url = "https://bac.blackyak.com/BAC/ChallengeProgram/getlist.asp?program_id=114"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://bac.blackyak.com/BAC/ChallengeProgram/114'
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def parse_javascript_array(js_text: str) -> list[dict]:
    """JavaScript 배열 형식을 Python 딕셔너리 리스트로 변환"""
    mountains = []

    # JavaScript 객체들을 분리 (},{로 split)
    # 먼저 전체 배열에서 [ ] 제거
    js_text = js_text.strip()
    if js_text.startswith('['):
        js_text = js_text[1:]
    if js_text.endswith(']'):
        js_text = js_text[:-1]

    # 각 객체 파싱
    # 패턴: {first_char: '...', title: '...', ...}
    pattern = r"\{([^}]+)\}"
    matches = re.findall(pattern, js_text)

    for idx, match in enumerate(matches, 1):
        mountain = {'id': idx}

        # first_char 추출
        first_char_match = re.search(r"first_char:\s*'([^']*)'", match)
        if first_char_match:
            mountain['first_char'] = first_char_match.group(1)

        # title 추출 (산 이름)
        title_match = re.search(r"title:\s*'([^']*)'", match)
        if title_match:
            mountain['name'] = title_match.group(1)

        # name 추출 (인증지 이름)
        name_match = re.search(r"(?<!image_url:\s)name:\s*'([^']*)'", match)
        if name_match:
            mountain['certification_point'] = name_match.group(1)

        # address 추출
        address_match = re.search(r"address:\s*'([^']*)'", match)
        if address_match:
            mountain['address'] = address_match.group(1)
            # 주소에서 지역 추출
            address = address_match.group(1)
            region = extract_region(address)
            mountain['region'] = region

        # image_url 추출
        image_match = re.search(r"image_url:\s*'([^']*)'", match)
        if image_match:
            mountain['image_url'] = image_match.group(1)

        # lat 추출
        lat_match = re.search(r"lat\s*:\s*([\d.]+)", match)
        if lat_match:
            mountain['latitude'] = float(lat_match.group(1))

        # lon 추출
        lon_match = re.search(r"lon\s*:\s*([\d.]+)", match)
        if lon_match:
            mountain['longitude'] = float(lon_match.group(1))

        # apex 추출 (고도)
        apex_match = re.search(r"apex\s*:\s*'([^']*)'", match)
        if apex_match:
            # '1,051' 형식에서 숫자만 추출
            altitude_str = apex_match.group(1).replace(',', '')
            try:
                mountain['altitude'] = int(altitude_str)
            except ValueError:
                mountain['altitude'] = None

        mountains.append(mountain)

    return mountains


def extract_region(address: str) -> str:
    """주소에서 광역시/도 추출"""
    region_mapping = {
        '서울': '서울특별시',
        '부산': '부산광역시',
        '대구': '대구광역시',
        '인천': '인천광역시',
        '광주': '광주광역시',
        '대전': '대전광역시',
        '울산': '울산광역시',
        '세종': '세종특별자치시',
        '경기': '경기도',
        '강원': '강원도',
        '충북': '충청북도',
        '충남': '충청남도',
        '전북': '전라북도',
        '전남': '전라남도',
        '경북': '경상북도',
        '경남': '경상남도',
        '제주': '제주특별자치도',
    }

    for short, full in region_mapping.items():
        if address.startswith(short):
            return full

    return address.split()[0] if address else ''


def save_to_json(data: list[dict], output_path: Path):
    """JSON 파일로 저장"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} mountains to {output_path}")


def save_to_csv(data: list[dict], output_path: Path):
    """CSV 파일로 저장"""
    import pandas as pd
    df = pd.DataFrame(data)

    # 컬럼 순서 정리
    columns = ['id', 'name', 'certification_point', 'altitude', 'region', 'address',
               'latitude', 'longitude', 'image_url', 'first_char']
    columns = [c for c in columns if c in df.columns]
    df = df[columns]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Saved {len(data)} mountains to {output_path}")


def print_statistics(mountains: list[dict]):
    """통계 출력"""
    from collections import Counter

    print(f"\n{'='*50}")
    print(f"총 {len(mountains)}개 산")
    print(f"{'='*50}")

    # 지역별 분포
    regions = Counter(m.get('region', '기타') for m in mountains)
    print("\n[지역별 분포]")
    for region, count in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"  {region}: {count}개")

    # 고도 통계
    altitudes = [m['altitude'] for m in mountains if m.get('altitude')]
    if altitudes:
        print(f"\n[고도 통계]")
        print(f"  최고: {max(altitudes)}m")
        print(f"  최저: {min(altitudes)}m")
        print(f"  평균: {sum(altitudes)//len(altitudes)}m")


def main():
    parser = argparse.ArgumentParser(description='블랙야크 100대 명산 크롤링 (공식 API)')
    parser.add_argument('--output', '-o', type=str,
                        default='../data/raw/blackyak_100.json',
                        help='Output file path (JSON)')
    parser.add_argument('--csv', action='store_true',
                        help='Also save as CSV')
    parser.add_argument('--stats', action='store_true',
                        help='Print statistics')
    args = parser.parse_args()

    print("Fetching data from Black Yak official API...")
    print("URL: https://bac.blackyak.com/BAC/ChallengeProgram/114")

    try:
        raw_data = fetch_official_data()
        mountains = parse_javascript_array(raw_data)

        if not mountains:
            print("Error: No data parsed. Check the API response format.")
            return

        output_path = Path(args.output)
        save_to_json(mountains, output_path)

        if args.csv:
            csv_path = output_path.with_suffix('.csv')
            save_to_csv(mountains, csv_path)

        # 통계 출력
        print_statistics(mountains)

        # 샘플 데이터 출력
        print(f"\n[샘플 데이터]")
        print(json.dumps(mountains[0], ensure_ascii=False, indent=2))

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        raise


if __name__ == '__main__':
    main()
