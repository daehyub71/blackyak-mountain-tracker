#!/usr/bin/env python3
"""
블랙야크 100대 명산 데이터를 Supabase에 업로드하는 스크립트

사용법:
    # .env 파일 설정 후
    python upload_to_supabase.py

    # 테스트 모드 (실제 업로드 안함)
    python upload_to_supabase.py --dry-run

    # 특정 파일 지정
    python upload_to_supabase.py --input ../data/raw/blackyak_100.json
"""

import argparse
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def get_supabase_client() -> Client:
    """Supabase 클라이언트 생성"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Service Role Key 사용 (RLS 우회)

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY 환경변수가 필요합니다.\n"
            ".env 파일을 확인하세요."
        )

    return create_client(url, key)


def load_mountains_data(input_path: Path) -> list[dict]:
    """JSON 파일에서 산 데이터 로드"""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def transform_mountain_data(raw: dict) -> dict:
    """크롤링 데이터를 Supabase 스키마에 맞게 변환"""
    # 산 이름에서 원래 이름 추출 (괄호 제거)
    name = raw.get('name', '')
    name_origin = re.sub(r'\([^)]*\)', '', name).strip()

    return {
        'name': name,
        'name_origin': name_origin,
        'altitude': raw.get('altitude'),
        'region': raw.get('region', ''),
        'address': raw.get('address', ''),
        'latitude': raw.get('latitude'),
        'longitude': raw.get('longitude'),
        'category': ['blackyak_100'],
        'first_char': raw.get('first_char', ''),
        'certification_point': raw.get('certification_point', ''),
        'image_url': raw.get('image_url', ''),
    }


def upload_mountains(client: Client, mountains: list[dict], dry_run: bool = False) -> int:
    """산 데이터 업로드"""
    transformed = [transform_mountain_data(m) for m in mountains]

    if dry_run:
        print(f"\n[DRY RUN] 업로드할 데이터 {len(transformed)}개:")
        print(json.dumps(transformed[0], ensure_ascii=False, indent=2))
        print("...")
        return len(transformed)

    # Upsert (name 기준으로 중복 시 업데이트)
    # 먼저 기존 데이터 확인
    existing = client.table('mountains').select('name').execute()
    existing_names = {m['name'] for m in existing.data}

    new_mountains = [m for m in transformed if m['name'] not in existing_names]
    update_mountains = [m for m in transformed if m['name'] in existing_names]

    # 새 데이터 삽입
    if new_mountains:
        result = client.table('mountains').insert(new_mountains).execute()
        print(f"새로 추가: {len(result.data)}개")

    # 기존 데이터 업데이트
    if update_mountains:
        for m in update_mountains:
            client.table('mountains').update(m).eq('name', m['name']).execute()
        print(f"업데이트: {len(update_mountains)}개")

    return len(transformed)


def verify_upload(client: Client):
    """업로드 결과 검증"""
    result = client.table('mountains').select('*', count='exact').execute()

    print(f"\n{'='*50}")
    print(f"[검증] mountains 테이블 레코드 수: {result.count}개")

    if result.data:
        # 지역별 통계
        from collections import Counter
        regions = Counter(m['region'] for m in result.data)
        print("\n[지역별 분포]")
        for region, count in sorted(regions.items(), key=lambda x: -x[1])[:5]:
            print(f"  {region}: {count}개")

        # 샘플 데이터
        print(f"\n[샘플 데이터]")
        sample = result.data[0]
        print(f"  이름: {sample['name']}")
        print(f"  인증지: {sample['certification_point']}")
        print(f"  위치: ({sample['latitude']}, {sample['longitude']})")


def main():
    parser = argparse.ArgumentParser(description='Supabase 데이터 업로드')
    parser.add_argument('--input', '-i', type=str,
                        default='../data/raw/blackyak_100.json',
                        help='Input JSON file path')
    parser.add_argument('--dry-run', action='store_true',
                        help='실제 업로드 없이 테스트')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: 파일을 찾을 수 없습니다: {input_path}")
        return

    print("="*50)
    print("블랙야크 100대 명산 Supabase 업로드")
    print("="*50)

    # 데이터 로드
    print(f"\n[1] 데이터 로드: {input_path}")
    mountains = load_mountains_data(input_path)
    print(f"    로드된 산: {len(mountains)}개")

    if args.dry_run:
        print("\n[DRY RUN 모드] 실제 업로드하지 않습니다.")
        upload_mountains(None, mountains, dry_run=True)
        return

    # Supabase 연결
    print(f"\n[2] Supabase 연결")
    try:
        client = get_supabase_client()
        print("    연결 성공!")
    except ValueError as e:
        print(f"    Error: {e}")
        return

    # 업로드
    print(f"\n[3] 데이터 업로드")
    count = upload_mountains(client, mountains)
    print(f"    처리 완료: {count}개")

    # 검증
    print(f"\n[4] 업로드 검증")
    verify_upload(client)

    print(f"\n{'='*50}")
    print("완료!")


if __name__ == '__main__':
    main()
