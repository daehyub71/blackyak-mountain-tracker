#!/usr/bin/env python3
"""
공공데이터포털 API를 통한 산/등산로 정보 수집 스크립트

데이터 소스:
1. 전국산정보표준데이터 (산림청)
   - http://apis.data.go.kr/1400000/service/cultureInfoService2/mntInfoOpenAPI2
   - 산이름, 높이, 위치, 100대명산 여부 등

2. 국토교통부 등산로 (WMS/WFS)
   - https://www.data.go.kr/data/15057232/openapi.do
   - 등산로 공간정보

3. 국립공원공단 파일 데이터
   - 공원 경계, 다목적위치표지판 등

사용법:
    export DATA_GO_KR_API_KEY="your_api_key"
    python fetch_public_data_api.py --type mountains --output ../data/raw/mountains_api.json
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()


class PublicDataAPIClient:
    """공공데이터포털 API 클라이언트"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('DATA_GO_KR_API_KEY')
        if not self.api_key:
            raise ValueError("DATA_GO_KR_API_KEY is required. Get it from https://www.data.go.kr/")

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BlackyakMountainTracker/1.0'
        })

    def fetch_mountain_info(self, mountain_name: str) -> Optional[dict]:
        """
        전국산정보표준데이터 API로 산 정보 조회

        API 문서: https://www.data.go.kr/data/15029183/standard.do
        """
        base_url = "http://apis.data.go.kr/1400000/service/cultureInfoService2/mntInfoOpenAPI2"

        params = {
            'serviceKey': self.api_key,
            'searchWrd': mountain_name,
            'numOfRows': 10,
            'pageNo': 1,
        }

        try:
            response = self.session.get(base_url, params=params, timeout=30)
            response.raise_for_status()

            # XML 응답 파싱
            from xml.etree import ElementTree as ET
            root = ET.fromstring(response.content)

            # 결과 추출
            items = root.findall('.//item')
            if not items:
                return None

            results = []
            for item in items:
                mountain = {
                    'name': self._get_text(item, 'mntnm'),  # 산이름
                    'altitude': self._get_int(item, 'mntheight'),  # 높이
                    'location': self._get_text(item, 'mntlocation'),  # 위치
                    'info': self._get_text(item, 'mntidetails'),  # 상세정보
                    'admin_district': self._get_text(item, 'mntiadminarea'),  # 행정구역
                    'is_top100': self._get_text(item, 'top100yn'),  # 100대명산 여부
                }
                results.append(mountain)

            return results[0] if len(results) == 1 else results

        except Exception as e:
            print(f"Error fetching mountain info for {mountain_name}: {e}")
            return None

    def fetch_all_mountains(self, page_size: int = 100) -> list[dict]:
        """전체 산 목록 조회"""
        base_url = "http://apis.data.go.kr/1400000/service/cultureInfoService2/mntInfoOpenAPI2"

        all_mountains = []
        page = 1

        while True:
            params = {
                'serviceKey': self.api_key,
                'numOfRows': page_size,
                'pageNo': page,
            }

            try:
                response = self.session.get(base_url, params=params, timeout=30)
                response.raise_for_status()

                from xml.etree import ElementTree as ET
                root = ET.fromstring(response.content)

                items = root.findall('.//item')
                if not items:
                    break

                for item in items:
                    mountain = {
                        'name': self._get_text(item, 'mntnm'),
                        'altitude': self._get_int(item, 'mntheight'),
                        'location': self._get_text(item, 'mntlocation'),
                        'info': self._get_text(item, 'mntidetails'),
                        'admin_district': self._get_text(item, 'mntiadminarea'),
                        'is_top100': self._get_text(item, 'top100yn') == 'Y',
                    }
                    all_mountains.append(mountain)

                total_count = int(self._get_text(root.find('.//totalCount'), '.') or 0)
                print(f"Page {page}: fetched {len(items)} mountains (total: {len(all_mountains)}/{total_count})")

                if len(all_mountains) >= total_count:
                    break

                page += 1
                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"Error on page {page}: {e}")
                break

        return all_mountains

    def fetch_trail_info(self) -> dict:
        """
        국토교통부 등산로 API 정보

        WMS/WFS 서비스로 제공되며, 직접 호출보다는 GIS 도구 사용 권장
        API 문서: https://www.data.go.kr/data/15057232/openapi.do
        """
        info = {
            "api_name": "국토교통부_등산로",
            "api_url": "https://www.data.go.kr/data/15057232/openapi.do",
            "service_type": "WMS/WFS (OGC 표준)",
            "available_layers": [
                "등산로",
                "등산로시설",
                "둘레길링크",
                "산책로분기점",
                "자전거길노드",
                "자전거길",
                "자전거보관소"
            ],
            "usage_note": "WMS/WFS 서비스는 QGIS, ArcGIS 등 GIS 도구에서 직접 연동하거나, " +
                         "OWSLib 파이썬 라이브러리를 사용하여 데이터를 가져올 수 있습니다.",
            "example_wfs_url": "https://api.vworld.kr/req/wfs?key={API_KEY}&service=WFS&request=GetFeature&typename=lt_l_frstclimb"
        }
        return info

    @staticmethod
    def _get_text(element, tag: str) -> Optional[str]:
        """XML 엘리먼트에서 텍스트 추출"""
        if element is None:
            return None
        child = element.find(tag) if tag != '.' else element
        return child.text if child is not None else None

    @staticmethod
    def _get_int(element, tag: str) -> Optional[int]:
        """XML 엘리먼트에서 정수 추출"""
        text = PublicDataAPIClient._get_text(element, tag)
        if text:
            try:
                return int(float(text))
            except ValueError:
                return None
        return None


class NationalParkDataFetcher:
    """국립공원공단 데이터 수집기"""

    # 22개 국립공원 목록 (2024년 기준)
    NATIONAL_PARKS = [
        {"name": "지리산", "code": "jirisan", "established": 1967},
        {"name": "경주", "code": "gyeongju", "established": 1968},
        {"name": "계룡산", "code": "gyeryongsan", "established": 1968},
        {"name": "한려해상", "code": "hallyeohaesang", "established": 1968},
        {"name": "설악산", "code": "seoraksan", "established": 1970},
        {"name": "속리산", "code": "songnisan", "established": 1970},
        {"name": "내장산", "code": "naejangsan", "established": 1971},
        {"name": "가야산", "code": "gayasan", "established": 1972},
        {"name": "덕유산", "code": "deogyusan", "established": 1975},
        {"name": "오대산", "code": "odaesan", "established": 1975},
        {"name": "주왕산", "code": "juwangsan", "established": 1976},
        {"name": "태안해안", "code": "taeanhaean", "established": 1978},
        {"name": "다도해해상", "code": "dadohaehaesang", "established": 1981},
        {"name": "북한산", "code": "bukhansan", "established": 1983},
        {"name": "치악산", "code": "chiaksan", "established": 1984},
        {"name": "월악산", "code": "woraksan", "established": 1984},
        {"name": "소백산", "code": "sobaeksan", "established": 1987},
        {"name": "변산반도", "code": "byeonsanbando", "established": 1988},
        {"name": "월출산", "code": "wolchulsan", "established": 1988},
        {"name": "무등산", "code": "mudeungsan", "established": 2013},
        {"name": "태백산", "code": "taebaeksan", "established": 2016},
        {"name": "팔공산", "code": "palgongsan", "established": 2023},
    ]

    def __init__(self):
        self.session = requests.Session()

    def get_national_park_list(self) -> list[dict]:
        """국립공원 목록 반환"""
        return self.NATIONAL_PARKS

    def fetch_park_boundary_file_info(self) -> dict:
        """국립공원 경계 데이터 파일 정보"""
        return {
            "api_name": "국립공원공단_국립공원 공원경계",
            "data_url": "https://www.data.go.kr/data/15017313/fileData.do",
            "file_format": "SHP (Shapefile)",
            "coordinate_system": "EPSG:4326 (WGS 84)",
            "download_note": "직접 다운로드 필요 (로그인 후)",
            "updated": "2024-02-05"
        }

    def fetch_signpost_file_info(self) -> dict:
        """다목적위치표지판 데이터 정보"""
        return {
            "api_name": "국립공원공단_다목적위치표지판 공간데이터",
            "data_url": "https://www.data.go.kr/dcat/metadata/15003463",
            "file_format": "CSV",
            "fields": ["위치번호", "고도(m)", "위도", "경도", "공원명"],
            "download_note": "직접 다운로드 필요"
        }


def save_json(data: any, output_path: Path):
    """JSON 파일로 저장"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='공공데이터포털 API 데이터 수집')
    parser.add_argument('--type', '-t', type=str, required=True,
                        choices=['mountains', 'mountain', 'trails', 'parks', 'all'],
                        help='Data type to fetch')
    parser.add_argument('--output', '-o', type=str,
                        default='../data/raw/',
                        help='Output directory')
    parser.add_argument('--name', '-n', type=str,
                        help='Mountain name (for --type mountain)')
    args = parser.parse_args()

    output_dir = Path(args.output)

    if args.type == 'mountains':
        # 전체 산 목록 조회
        client = PublicDataAPIClient()
        print("Fetching all mountains from 전국산정보표준데이터 API...")
        mountains = client.fetch_all_mountains()
        save_json(mountains, output_dir / 'mountains_api.json')
        print(f"\nFetched {len(mountains)} mountains")

        # 100대 명산만 필터링
        top100 = [m for m in mountains if m.get('is_top100')]
        save_json(top100, output_dir / 'top100_mountains_api.json')
        print(f"100대 명산: {len(top100)} mountains")

    elif args.type == 'mountain':
        # 단일 산 조회
        if not args.name:
            print("Error: --name is required for --type mountain")
            return
        client = PublicDataAPIClient()
        result = client.fetch_mountain_info(args.name)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"No data found for {args.name}")

    elif args.type == 'trails':
        # 등산로 API 정보 출력
        client = PublicDataAPIClient()
        info = client.fetch_trail_info()
        print("\n=== 등산로 API 정보 ===")
        print(json.dumps(info, ensure_ascii=False, indent=2))
        save_json(info, output_dir / 'trail_api_info.json')

    elif args.type == 'parks':
        # 국립공원 정보
        fetcher = NationalParkDataFetcher()
        parks = fetcher.get_national_park_list()
        boundary_info = fetcher.fetch_park_boundary_file_info()
        signpost_info = fetcher.fetch_signpost_file_info()

        data = {
            "national_parks": parks,
            "data_sources": {
                "boundary": boundary_info,
                "signpost": signpost_info
            }
        }
        save_json(data, output_dir / 'national_parks_info.json')
        print(f"\n국립공원 {len(parks)}개 정보 저장")

    elif args.type == 'all':
        # 전체 수집
        print("Collecting all available data...")

        # 1. 산 정보
        try:
            client = PublicDataAPIClient()
            mountains = client.fetch_all_mountains()
            save_json(mountains, output_dir / 'mountains_api.json')
        except ValueError as e:
            print(f"Warning: {e}")

        # 2. 국립공원 정보
        fetcher = NationalParkDataFetcher()
        parks_data = {
            "national_parks": fetcher.get_national_park_list(),
            "data_sources": {
                "boundary": fetcher.fetch_park_boundary_file_info(),
                "signpost": fetcher.fetch_signpost_file_info()
            }
        }
        save_json(parks_data, output_dir / 'national_parks_info.json')

        print("\nData collection complete!")


if __name__ == '__main__':
    main()
