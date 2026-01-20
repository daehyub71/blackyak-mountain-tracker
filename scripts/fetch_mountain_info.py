#!/usr/bin/env python3
"""
산림청 산정보 API를 사용하여 블랙야크 100대 명산 정보를 수집하는 스크립트

API 엔드포인트: http://openapi.forest.go.kr/openapi/service/trailInfoService/getforeststoryservice

Usage:
    python fetch_mountain_info.py

필요:
    - .env 파일에 DATA_GO_KR_API_KEY 설정
    - pip install requests python-dotenv
"""

import os
import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
import pandas as pd
from dotenv import load_dotenv
import time
import urllib.parse

# .env 파일 로드
load_dotenv()

API_KEY = os.getenv('DATA_GO_KR_API_KEY')
# 공공데이터포털 API 게이트웨이 사용
BASE_URL = 'http://apis.data.go.kr/1400000/service/cultureInfoService2/forestStoryService'
# 대체 URL (산림청 직접)
ALT_URL = 'http://openapi.forest.go.kr/openapi/service/trailInfoService/getforeststoryservice'


def fetch_mountain_info(mountain_name: str) -> Optional[dict]:
    """산림청 API에서 산 정보 조회"""
    if not API_KEY or API_KEY == 'your_api_key':
        print("❌ DATA_GO_KR_API_KEY가 설정되지 않았습니다.")
        print("   1. https://www.data.go.kr/data/15058682/openapi.do 에서 활용신청")
        print("   2. scripts/.env 파일에 API 키 설정")
        return None

    params = {
        'serviceKey': API_KEY,
        'mntnNm': mountain_name,
        'numOfRows': 10,
        'pageNo': 1,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()

        # XML 파싱
        root = ET.fromstring(response.content)

        # 에러 체크
        result_code = root.find('.//resultCode')
        if result_code is not None and result_code.text != '00':
            result_msg = root.find('.//resultMsg')
            print(f"  API 에러: {result_msg.text if result_msg is not None else 'Unknown'}")
            return None

        # 데이터 추출
        items = root.findall('.//item')
        if not items:
            return None

        # 첫 번째 결과 사용
        item = items[0]

        def get_text(elem_name: str) -> str:
            elem = item.find(elem_name)
            return elem.text.strip() if elem is not None and elem.text else ''

        return {
            'mntn_id': get_text('mntnid'),
            'mntn_nm': get_text('mntnnm'),
            'mntn_height': get_text('mntninfohght'),
            'mntn_location': get_text('mntninfopoflc'),
            'mntn_summary': get_text('mntninfodscrt'),          # 산 개관/설명
            'tourism_info': get_text('crcmrsghtnginfodscrt'),   # 주변 관광정보
            'image_url': get_text('mntnattchimageseq'),         # 이미지
        }

    except requests.exceptions.RequestException as e:
        print(f"  요청 실패: {e}")
        return None
    except ET.ParseError as e:
        print(f"  XML 파싱 실패: {e}")
        return None


def generate_from_csv_only():
    """CSV 데이터만 사용하여 산 정보 JSON 생성 (API 미사용)"""
    script_dir = Path(__file__).parent
    blackyak_csv = script_dir.parent / 'data' / 'raw' / 'blackyak_100.csv'
    output_dir = script_dir.parent / 'frontend' / 'public' / 'mountain_info'

    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)

    # 블랙야크 100대 명산 로드
    df = pd.read_csv(blackyak_csv)

    print("🏔️ CSV에서 산 정보 생성 중...")
    print("-" * 50)

    results = []

    for _, row in df.iterrows():
        mountain_name = row['name']
        search_name = mountain_name.split('(')[0] if '(' in mountain_name else mountain_name

        info = {
            'blackyak_id': int(row['id']),
            'blackyak_name': mountain_name,
            'mntn_nm': search_name,
            'mntn_height': str(int(row['altitude'])) + 'm' if pd.notna(row.get('altitude')) else '',
            'mntn_location': row.get('address', ''),
            'mntn_summary': '',  # API에서 가져올 정보
            'tourism_info': '',  # API에서 가져올 정보
            'image_url': row.get('image_url', ''),
            'certification_point': row.get('certification_point', ''),
            'altitude': int(row['altitude']) if pd.notna(row.get('altitude')) else None,
            'region': row.get('region', ''),
            'address': row.get('address', ''),
            'latitude': float(row['latitude']) if pd.notna(row.get('latitude')) else None,
            'longitude': float(row['longitude']) if pd.notna(row.get('longitude')) else None,
        }

        results.append(info)
        print(f"  ✅ {mountain_name}")

    # 전체 데이터 저장
    output_file = output_dir / 'index.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 개별 산 파일 저장 (blackyak_id 기준)
    for info in results:
        individual_file = output_dir / f"{info['blackyak_id']}.json"
        with open(individual_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

    print("-" * 50)
    print(f"\n✅ 생성 완료: {len(df)}개 산")
    print(f"📁 출력 디렉토리: {output_dir}")


def main():
    """메인 함수 - CSV 데이터로 기본 생성 (API는 선택사항)"""
    # CSV 기반으로 기본 데이터 생성
    generate_from_csv_only()


if __name__ == '__main__':
    main()
