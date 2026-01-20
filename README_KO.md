# 블랙야크 100대 명산 트래커

**블랙야크 100대 명산 챌린지**를 도전하는 등산객들을 위한 종합 정보 플랫폼입니다.

![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?logo=tailwindcss)
![Vite](https://img.shields.io/badge/Vite-7.3-646CFF?logo=vite)

## 주요 기능

- **100대 명산 리스트** - 지역별, 고도별 필터링으로 전체 명산 탐색
- **산 상세 정보** - 해발고도, 소재지, 인증 장소, 산 소개 확인
- **등산로 지도** - 62개 산의 등산로를 인터랙티브 지도로 표시 (Leaflet 기반)
- **정상 마커** - 금색 마커로 정상 위치와 해발고도 표시
- **위키피디아 연동** - 한국어 위키피디아에서 산 소개 정보 제공 (87/99개 산)
- **반응형 디자인** - 야외 사용에 최적화된 모바일 퍼스트 UI

## 데모

**라이브 데모**: [https://frontend-iyx82grvb-daehyub71s-projects.vercel.app](https://frontend-iyx82grvb-daehyub71s-projects.vercel.app)

## 기술 스택

### 프론트엔드
- **프레임워크**: React 18 + Vite
- **언어**: TypeScript
- **스타일링**: Tailwind CSS
- **지도**: React-Leaflet + OpenStreetMap
- **상태 관리**: Zustand + TanStack Query
- **라우팅**: React Router v6

### 데이터 소스
- **산 데이터**: 블랙야크 공식 100대 명산 리스트
- **등산로 데이터**: 산림청 등산로 공간정보 (GPX)
- **산 소개**: 한국어 위키피디아 REST API
- **지도 타일**: OpenStreetMap

## 프로젝트 구조

```
blackyak-mountain-tracker/
├── frontend/                # React 프론트엔드
│   ├── src/
│   │   ├── components/      # UI 컴포넌트
│   │   ├── pages/           # 페이지 컴포넌트
│   │   ├── hooks/           # 커스텀 훅
│   │   ├── services/        # API 서비스
│   │   └── types/           # TypeScript 타입
│   └── public/
│       ├── mountain_info/   # 산 정보 JSON (99개)
│       └── trails/          # 등산로 JSON (62개)
├── scripts/                 # 데이터 수집 스크립트
│   ├── crawl_blackyak_100.py
│   ├── convert_gpx_to_json.py
│   └── fetch_wiki_mountain_info.py
├── data/                    # 원본 및 가공 데이터
│   └── raw/
│       └── blackyak_100.csv
└── docs/                    # 문서
```

## 시작하기

### 필수 조건
- Node.js 18+
- npm 또는 yarn

### 설치

```bash
# 저장소 클론
git clone https://github.com/daehyub71/blackyak-mountain-tracker.git
cd blackyak-mountain-tracker

# 프론트엔드 의존성 설치
cd frontend
npm install

# 개발 서버 실행
npm run dev
```

브라우저에서 [http://localhost:5173](http://localhost:5173)을 엽니다.

### 프로덕션 빌드

```bash
cd frontend
npm run build
```

## 데이터 수집 (선택사항)

데이터를 재생성하려면:

```bash
cd scripts
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 위키피디아에서 산 소개 가져오기
python fetch_wiki_mountain_info.py

# GPX 등산로를 JSON으로 변환
python convert_gpx_to_json.py
```

## 배포

Vercel 배포가 설정되어 있습니다:

```bash
cd frontend
vercel --prod
```

## 스크린샷

### 산 리스트
지역별, 고도별 필터로 100대 명산을 탐색합니다.

### 산 상세 정보
등산로 지도, 정상 마커, 산 소개 등 상세 정보를 확인합니다.

### 등산로 지도
출발점, 종점, 정상 마커가 표시된 인터랙티브 지도입니다.

## 로드맵

- [ ] 사용자 인증 (Supabase)
- [ ] 개인 진행률 트래킹
- [ ] 완등 인증샷 업로드
- [ ] 날씨 정보 연동
- [ ] 커뮤니티 기능

## 라이선스

MIT License

## 감사의 글

- [블랙야크](https://www.blackyak.com/) - 100대 명산 챌린지
- [산림청](https://www.forest.go.kr/) - 등산로 공간정보
- [한국어 위키피디아](https://ko.wikipedia.org/) - 산 소개 정보
- [OpenStreetMap](https://www.openstreetmap.org/) - 지도 타일
