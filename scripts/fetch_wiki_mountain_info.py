#!/usr/bin/env python3
"""
위키피디아에서 블랙야크 100대 명산 정보를 수집하는 스크립트

Usage:
    python fetch_wiki_mountain_info.py
"""

import json
import requests
import urllib.parse
from pathlib import Path
import pandas as pd
import time


def fetch_wiki_summary(mountain_name: str) -> str:
    """위키피디아 REST API를 사용하여 산 요약 정보 가져오기"""
    # 괄호 내용 추출 (예: 가리산(홍천) -> 홍천)
    location = ''
    if '(' in mountain_name:
        location = mountain_name.split('(')[1].rstrip(')')
    search_name = mountain_name.split('(')[0].strip()

    # 공백을 포함한 산 이름 처리 (예: "오대산 노인봉" -> "노인봉", "오대산")
    if ' ' in search_name:
        parts = search_name.split()
        search_variations = [search_name.replace(' ', '_'), parts[-1], parts[0]]
    else:
        search_variations = [search_name]

    # 지역명이 있으면 추가
    if location:
        search_variations.insert(0, f"{search_name}_({location})")
        search_variations.append(f"{search_name}_(산)")

    headers = {
        'User-Agent': 'BlackyakMountainTracker/1.0 (https://github.com/blackyak-mountain-tracker)'
    }

    for search_term in search_variations:
        try:
            # Wikipedia REST API 사용
            api_url = f'https://ko.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(search_term)}'
            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                extract = data.get('extract', '')

                # 산 관련 내용인지 확인 (해발, 산, m, 미터 등의 키워드)
                if extract and len(extract) > 50:
                    keywords = ['해발', '산', 'm)', '미터', '봉', '능선', '등산', '국립공원']
                    if any(kw in extract for kw in keywords):
                        return extract[:1000]

            elif response.status_code == 404:
                continue

        except Exception:
            continue

    return ''


def main():
    """메인 함수"""
    script_dir = Path(__file__).parent
    blackyak_csv = script_dir.parent / 'data' / 'raw' / 'blackyak_100.csv'
    output_dir = script_dir.parent / 'frontend' / 'public' / 'mountain_info'

    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)

    # 블랙야크 100대 명산 로드
    df = pd.read_csv(blackyak_csv)

    print("🏔️ 위키피디아에서 산 정보 수집 중...")
    print("-" * 50)

    results = []
    success_count = 0

    for idx, row in df.iterrows():
        mountain_name = row['name']
        search_name = mountain_name.split('(')[0] if '(' in mountain_name else mountain_name

        print(f"  {idx+1}/{len(df)} {mountain_name} 검색 중...", end='', flush=True)

        # 위키피디아에서 요약 가져오기
        wiki_summary = fetch_wiki_summary(mountain_name)

        if wiki_summary:
            print(f" ✅ ({len(wiki_summary)}자)")
            success_count += 1
        else:
            print(" ⚠️ (정보 없음)")

        info = {
            'blackyak_id': int(row['id']),
            'blackyak_name': mountain_name,
            'mntn_nm': search_name,
            'mntn_height': str(int(row['altitude'])) + 'm' if pd.notna(row.get('altitude')) else '',
            'mntn_location': row.get('address', ''),
            'mntn_summary': wiki_summary,  # 위키피디아 요약
            'tourism_info': '',  # 추후 추가 가능
            'image_url': row.get('image_url', ''),
            'certification_point': row.get('certification_point', ''),
            'altitude': int(row['altitude']) if pd.notna(row.get('altitude')) else None,
            'region': row.get('region', ''),
            'address': row.get('address', ''),
            'latitude': float(row['latitude']) if pd.notna(row.get('latitude')) else None,
            'longitude': float(row['longitude']) if pd.notna(row.get('longitude')) else None,
        }

        results.append(info)

        # API 부하 방지
        time.sleep(0.5)

    # 전체 데이터 저장
    output_file = output_dir / 'index.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 개별 산 파일 저장
    for info in results:
        individual_file = output_dir / f"{info['blackyak_id']}.json"
        with open(individual_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

    print("-" * 50)
    print(f"\n✅ 수집 완료: {len(df)}개 산 중 {success_count}개 위키 정보 수집")
    print(f"📁 출력 디렉토리: {output_dir}")


if __name__ == '__main__':
    main()
