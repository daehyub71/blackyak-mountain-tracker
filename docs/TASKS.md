# 블랙야크 100대 명산 트래커 - 상세 Task 리스트

## Task 관리 규칙

- [ ] 미완료
- [x] 완료
- 🔴 P0 (필수)
- 🟡 P1 (중요)
- 🟢 P2 (선택)

---

## Phase 0: 프로젝트 셋업 (완료)

### 0.1 프로젝트 구조
- [x] 프로젝트 폴더 생성 (`blackyak-mountain-tracker`)
- [x] 디렉토리 구조 생성 (backend, frontend, scripts, data, docs)
- [x] CLAUDE.md 작성
- [x] .gitignore 작성
- [x] .env.example 작성

### 0.2 문서화
- [x] DB 스키마 설계 (`docs/db_schema.md`)
- [x] 개발계획서 작성 (`docs/개발계획서.md`)
- [x] 와이어프레임 작성 (ASCII)
- [x] Task 리스트 작성 (`docs/TASKS.md`)
- [x] Supabase 설정 가이드 작성 (`docs/SUPABASE_SETUP.md`)

### 0.3 데이터 수집 스크립트
- [x] `crawl_blackyak_100.py` - 100대 명산 크롤러
- [x] `fetch_public_data_api.py` - 공공데이터 API 클라이언트
- [x] `requirements.txt` 작성

---

## Phase 1: MVP (Week 1-4)

### Week 1: 인프라 및 데이터 기반 ✅

#### 1.1 Supabase 설정 🔴 ✅
- [x] Supabase 프로젝트 생성
- [x] 프로젝트 URL 및 API 키 획득
- [x] `.env` 파일에 Supabase 설정 추가
- [ ] Supabase CLI 설치 (선택)

#### 1.2 데이터베이스 생성 🔴 ✅
- [x] `mountains` 테이블 생성
- [x] `trails` 테이블 생성
- [x] `parking_lots` 테이블 생성
- [x] `highlights` 테이블 생성
- [x] `user_profiles` 테이블 생성
- [x] `user_completions` 테이블 생성
- [x] `user_completion_photos` 테이블 생성
- [x] PostGIS 확장 활성화
- [x] 인덱스 생성
- [x] RLS 정책 설정 (Public Read)
- [x] Triggers 설정 (updated_at, 신규 사용자 프로필 자동 생성)

#### 1.3 초기 데이터 수집 🔴 ✅
- [x] 크롤링 스크립트 venv 설정
- [x] `crawl_blackyak_100.py` 실행 (공식 API 버전)
- [x] 99대 명산 기본 데이터 JSON 생성 (`data/raw/blackyak_100.json`)
  - ⚠️ 공식 API에서 99개만 반환됨 (1개 누락, 추후 수동 입력)
- [ ] 공공데이터포털 API 키 발급
- [ ] `fetch_public_data_api.py` 실행 (산 정보 보강)
- [ ] 국립공원 데이터 파일 다운로드

#### 1.4 데이터 Supabase 업로드 🔴 ✅
- [x] 데이터 업로드 스크립트 작성 (`scripts/upload_to_supabase.py`)
- [x] 99대 명산 기본 정보 업로드
- [x] 인증지 정보 업로드 (certification_point 필드)
- [x] 데이터 검증 쿼리 실행
  - 총 99개 레코드
  - 지역별 분포: 강원도(21), 전라남도(13), 전라북도(11), 충청북도(10), 경상북도(10)...

---

### Week 2: Frontend 기본 구조 ✅

#### 2.1 React 프로젝트 초기화 🔴 ✅
- [x] Vite + React + TypeScript 프로젝트 생성
- [x] 기본 의존성 설치
  - [x] `@supabase/supabase-js`
  - [x] `@tanstack/react-query`
  - [x] `zustand`
  - [x] `react-router-dom`
- [x] Tailwind CSS v4 설정
  - [x] `tailwindcss`, `@tailwindcss/vite` 설치
  - [x] `vite.config.ts`에 플러그인 추가
  - [x] `index.css` 설정 (@import "tailwindcss")

#### 2.2 프로젝트 구조 설정 🔴 ✅
- [x] 폴더 구조 생성 (components, pages, hooks, services, stores, types, utils)
- [x] 라우터 설정 (`App.tsx`)
- [x] 레이아웃 컴포넌트 생성
  - [x] `Header.tsx`
  - [x] `Footer.tsx`
  - [x] `Layout.tsx`

#### 2.3 Supabase 클라이언트 설정 🔴 ✅
- [x] Supabase 클라이언트 초기화 (`services/supabase.ts`)
- [x] 환경변수 설정 (`.env.local`)
- [x] TypeScript 타입 생성
  - [x] `types/mountain.ts` (Mountain, Trail, ParkingLot, Highlight, Filters)

#### 2.4 API 서비스 레이어 🔴 ✅
- [x] `services/mountainService.ts`
  - [x] `getMountains()` - 목록 조회 (페이지네이션, 필터링)
  - [x] `getMountainById()` - 상세 조회
  - [x] `searchMountains()` - 검색
  - [x] `getRegions()` - 지역 목록
  - [x] `getTrailsByMountainId()` - 산별 코스 조회
- [x] React Query 훅 생성
  - [x] `hooks/useMountains.ts` (useMountains, useMountain, useSearchMountains, useRegions, useTrails)
- [x] Zustand 스토어 생성
  - [x] `stores/filterStore.ts` - 필터 상태 관리

---

### Week 3: 핵심 페이지 개발 ✅

#### 3.1 산 목록 페이지 🔴 ✅
- [x] `pages/MountainListPage.tsx` 생성
- [x] 산 카드 컴포넌트 (`components/mountain/MountainCard.tsx`)
- [x] 그리드 레이아웃 구현 (반응형 1-4열)
- [x] 로딩 상태 UI (스켈레톤)
- [x] 에러 상태 UI
- [x] Empty 상태 UI

#### 3.2 검색 및 필터 🔴 ✅
- [x] 검색바 컴포넌트 (`components/common/SearchBar.tsx`) - 디바운스 적용
- [x] 필터 컴포넌트 (`components/mountain/MountainFilters.tsx`)
  - [x] 지역 필터 (시/도)
  - [ ] 난이도 필터 (Phase 2: 등산로 데이터 필요)
  - [ ] 소요시간 필터 (Phase 2: 등산로 데이터 필요)
  - [ ] 국립공원 필터 (Phase 2)
- [ ] URL 쿼리 파라미터 연동 (Phase 2)
- [x] 필터 상태 관리 (Zustand) - `stores/filterStore.ts`

#### 3.3 페이지네이션 🟡 ✅
- [x] 페이지네이션 컴포넌트 (MountainListPage 내장)
- [ ] 무한 스크롤 (선택적 대안)
- [ ] 페이지당 항목 수 설정 (12/24/48)

#### 3.4 산 상세 페이지 🔴 ✅
- [x] `pages/MountainDetailPage.tsx` 생성
- [x] 산 기본 정보 섹션
  - [x] 대표 이미지 (또는 기본 아이콘)
  - [x] 이름, 높이, 위치
  - [ ] 설명/의미 (데이터 입력 필요)
- [x] 인증지 정보 섹션
  - [x] 인증지 카드 (그린 배경)
  - [x] 지도 보기 링크 (Kakao Map)
- [x] 등산로 목록 섹션
  - [x] 코스 카드 (난이도 배지, 거리, 시간)
  - [ ] 시간대별 필터 탭 (Phase 2)

---

### Week 4: GPX 및 부가 기능 ✅

#### 4.1 등산로 상세 🔴
- [ ] 코스 상세 모달/페이지 (Phase 2)
  - [ ] 들머리/날머리
  - [ ] 거리, 시간, 난이도
  - [ ] 고도 프로파일 (선택)
  - [ ] 주의사항

#### 4.2 GPX 다운로드 🔴 ✅
- [x] GPX 생성 유틸리티 (`utils/gpxGenerator.ts`)
- [x] 다운로드 버튼 컴포넌트 (MountainDetailPage)
- [x] GPX 파일 저장 로직 (Blob + download)
- [ ] 트랭글/램블러 호환 테스트 (수동 확인 필요)

#### 4.3 주차장 정보 🟡
- [ ] 주차장 섹션 컴포넌트 (Phase 2)
- [ ] Kakao Map 길찾기 연동
- [ ] 주차장 데이터 입력 (최소 20개 산)

#### 4.4 추천 장소 🟢
- [ ] 추천 장소 섹션 컴포넌트 (Phase 2)
- [ ] 추천 장소 데이터 입력 (최소 20개 산)

#### 4.5 반응형 UI 🔴 ✅
- [x] 모바일 레이아웃 최적화
- [x] 태블릿 레이아웃 (Tailwind 반응형)
- [x] 햄버거 메뉴 (모바일) - Header.tsx
- [x] 터치 친화적 UI (버튼 사이즈, 간격)
- [x] 지역 필터 가로 스크롤 (모바일)
- [x] Sticky 헤더

#### 4.6 배포 🔴 ✅
- [x] Vercel 프로젝트 연결
- [x] 환경변수 설정 (VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY)
- [x] 프로덕션 빌드 테스트
- [x] 배포 URL: https://frontend-nqzndi99h-daehyub71s-projects.vercel.app
- [ ] 커스텀 도메인 설정 (선택)

---

## Phase 2: 개인화 (Week 5-7)

### Week 5: 인증 시스템

#### 5.1 Supabase Auth 설정 🔴
- [ ] Auth 공급자 설정 (Supabase Dashboard)
  - [ ] 이메일/비밀번호
  - [ ] Google OAuth (선택)
  - [ ] Kakao OAuth (선택)
- [ ] `user_profiles` 테이블 RLS 설정
- [ ] Auth 트리거 설정 (프로필 자동 생성)

#### 5.2 인증 UI 🔴
- [ ] 로그인 페이지 (`pages/LoginPage.tsx`)
- [ ] 회원가입 페이지 (`pages/SignUpPage.tsx`)
- [ ] 비밀번호 재설정 페이지
- [ ] 인증 상태 관리 (`stores/authStore.ts`)
- [ ] Protected Route 컴포넌트

#### 5.3 사용자 프로필 🟡
- [ ] 프로필 페이지 (`pages/ProfilePage.tsx`)
- [ ] 프로필 수정 기능
- [ ] 아바타 업로드 (Supabase Storage)

---

### Week 6: 완등 기록

#### 6.1 데이터베이스 🔴
- [ ] `user_completions` 테이블 RLS 설정
- [ ] `user_completion_photos` 테이블 RLS 설정

#### 6.2 완등 기록 CRUD 🔴
- [ ] `services/completionService.ts`
  - [ ] `addCompletion()` - 기록 추가
  - [ ] `getCompletions()` - 기록 조회
  - [ ] `updateCompletion()` - 기록 수정
  - [ ] `deleteCompletion()` - 기록 삭제
- [ ] React Query 훅
  - [ ] `hooks/useCompletions.ts`
  - [ ] `hooks/useAddCompletion.ts`

#### 6.3 완등 기록 UI 🔴
- [ ] 완등 추가 모달/페이지
  - [ ] 산 선택 (자동완성)
  - [ ] 날짜 선택
  - [ ] 코스 선택 (선택)
  - [ ] 메모 입력
  - [ ] 날씨 선택
  - [ ] 블랙야크 인증 여부
- [ ] 인증샷 업로드
  - [ ] 이미지 선택/촬영
  - [ ] Supabase Storage 업로드
  - [ ] 썸네일 생성
- [ ] 기록 목록 표시
- [ ] 기록 수정/삭제

#### 6.4 산 상세 페이지 연동 🔴
- [ ] "완등 기록하기" 버튼 추가
- [ ] 이미 완등한 산 표시 (배지/아이콘)
- [ ] 내 완등 기록 표시 (로그인 시)

---

### Week 7: 진행률 대시보드

#### 7.1 대시보드 페이지 🔴
- [ ] `pages/DashboardPage.tsx` 생성
- [ ] 전체 진행률 카드
  - [ ] 프로그레스 바 (42/100)
  - [ ] 완등 개수
  - [ ] 마지막 완등 정보

#### 7.2 통계 시각화 🟡
- [ ] 지역별 완등 현황 차트
- [ ] 월별 등산 횟수 차트
- [ ] 난이도별 분포 (선택)
- [ ] 차트 라이브러리 선택 (Recharts/Chart.js)

#### 7.3 완등 기록 테이블 🔴
- [ ] 최근 완등 목록
- [ ] 정렬 (날짜순)
- [ ] 필터 (연도별)
- [ ] 상세 보기 링크

#### 7.4 미완등 산 목록 🟡
- [ ] 아직 완등하지 않은 산 목록
- [ ] 추천 순서 (거리순, 난이도순)

---

## Phase 3: 부가 기능 (Week 8-10)

### 8.1 날씨 정보 🟡
- [ ] 기상청 API 연동 조사
- [ ] 날씨 서비스 구현 (`services/weatherService.ts`)
- [ ] 산 상세 페이지에 날씨 위젯 추가
- [ ] 주간 예보 표시

### 8.2 Kakao Map 연동 🟡
- [ ] Kakao Map SDK 설정
- [ ] 산 위치 마커 표시
- [ ] 등산로 경로 표시 (GPX 기반)
- [ ] 인증지/주차장 마커

### 8.3 대중교통 정보 🟢
- [ ] 버스 노선 정보 수집 (수동)
- [ ] 대중교통 섹션 UI
- [ ] 네이버/카카오 지도 대중교통 링크

### 8.4 SEO 최적화 🟡
- [ ] 메타 태그 설정 (`react-helmet-async`)
- [ ] Open Graph 태그
- [ ] 사이트맵 생성
- [ ] robots.txt

---

## Phase 4: 커뮤니티 (Week 11+)

### 9.1 등산 후기 🟢
- [ ] `reviews` 테이블 설계
- [ ] 후기 작성 UI
- [ ] 후기 목록 표시
- [ ] 평점 시스템

### 9.2 상태 제보 🟢
- [ ] `trail_conditions` 테이블 설계
- [ ] 제보 UI (등산로 상태, 주차장 만차 등)
- [ ] 최근 제보 표시

### 9.3 사진 갤러리 🟢
- [ ] 산별 사진 갤러리
- [ ] 사용자 업로드 사진 표시
- [ ] 라이트박스 뷰어

---

## 데이터 입력 작업 (병행)

### 우선순위 1 (10개 산) - Week 2-3
- [ ] 북한산 - 등산로 3개, 주차장 3개, 인증지
- [ ] 설악산 - 등산로 5개, 주차장 4개, 인증지
- [ ] 지리산 - 등산로 5개, 주차장 5개, 인증지
- [ ] 팔공산 - 등산로 3개, 주차장 2개, 인증지
- [ ] 한라산 - 등산로 5개, 주차장 5개, 인증지
- [ ] 덕유산 - 등산로 3개, 주차장 2개, 인증지
- [ ] 소백산 - 등산로 3개, 주차장 2개, 인증지
- [ ] 오대산 - 등산로 3개, 주차장 2개, 인증지
- [ ] 치악산 - 등산로 3개, 주차장 2개, 인증지
- [ ] 가야산 - 등산로 3개, 주차장 2개, 인증지

### 우선순위 2 (30개 산) - Week 4-5
- [ ] 나머지 국립공원 산 (12개)
- [ ] 수도권 인기 산 (18개)

### 우선순위 3 (60개 산) - Week 6+
- [ ] 나머지 100대 명산

### GPX 파일 수집
- [ ] 직접 등산하며 GPX 기록
- [ ] 램블러/트랭글 공유 GPX 수집
- [ ] 산림청 등산로 데이터 변환

---

## 테스트 체크리스트

### 기능 테스트
- [ ] 산 목록 조회
- [ ] 검색 기능
- [ ] 필터 기능
- [ ] 산 상세 조회
- [ ] GPX 다운로드
- [ ] 회원가입/로그인
- [ ] 완등 기록 CRUD
- [ ] 이미지 업로드

### 반응형 테스트
- [ ] iPhone SE (375px)
- [ ] iPhone 14 (390px)
- [ ] iPad (768px)
- [ ] Desktop (1280px+)

### 브라우저 테스트
- [ ] Chrome
- [ ] Safari
- [ ] Firefox
- [ ] Samsung Internet

### 성능 테스트
- [ ] Lighthouse 점수 80+
- [ ] 첫 페이지 로딩 3초 이내
- [ ] 이미지 최적화

---

## 마일스톤

| 마일스톤 | 목표일 | 완료 기준 | 상태 |
|----------|--------|-----------|------|
| M0: 셋업 완료 | Week 0 | 프로젝트 구조, 문서화 | ✅ 완료 |
| M1: DB 구축 | Week 1 | Supabase 설정, 99대 명산 데이터 업로드 | ✅ 완료 |
| M2: MVP UI | Week 3 | 목록/상세 페이지, 검색/필터 | ✅ 완료 |
| M3: MVP 배포 | Week 4 | GPX 다운로드, Vercel 배포 | ✅ 완료 |
| M4: 인증 | Week 5 | 회원가입/로그인 | 🔲 |
| M5: 기록 | Week 6 | 완등 기록, 사진 업로드 | 🔲 |
| M6: 대시보드 | Week 7 | 진행률, 통계 | 🔲 |
| M7: 부가기능 | Week 10 | 날씨, 지도 | 🔲 |
| M8: 커뮤니티 | Week 12+ | 후기, 제보 | 🔲 |

---

## 진행 현황 요약

### 완료된 작업 (2025-01-18 기준)

**Phase 0: 프로젝트 셋업** ✅
- 프로젝트 구조 생성
- 문서화 완료 (CLAUDE.md, db_schema.md, 개발계획서.md, TASKS.md, SUPABASE_SETUP.md)
- 크롤링 스크립트 작성

**Phase 1 Week 1: 인프라 및 데이터 기반** ✅
- Supabase 프로젝트 설정 완료
- 데이터베이스 스키마 생성 (7개 테이블 + RLS + Triggers)
- 블랙야크 공식 API에서 99개 산 데이터 크롤링
- Supabase mountains 테이블에 99개 레코드 업로드 완료

**Phase 1 Week 2-3: Frontend 기본 구조 및 핵심 페이지** ✅
- Vite + React + TypeScript + Tailwind CSS v4 프로젝트 설정
- Supabase 클라이언트, React Query, Zustand 연동
- 산 목록 페이지 (검색, 지역 필터, 페이지네이션)
- 산 상세 페이지 (인증지, 카카오맵 연동, 등산로 목록)

**Phase 1 Week 4: GPX 및 배포** ✅
- GPX 다운로드 기능 (`utils/gpxGenerator.ts`)
- 반응형 UI (모바일 햄버거 메뉴, 지역 필터 스크롤, Sticky 헤더)
- Vercel 프로덕션 배포 완료
- 배포 URL: https://frontend-nqzndi99h-daehyub71s-projects.vercel.app

### 다음 작업 (Phase 2: 개인화)
- [ ] Supabase Auth 설정 (이메일/비밀번호, OAuth)
- [ ] 로그인/회원가입 UI
- [ ] 완등 기록 CRUD
- [ ] 진행률 대시보드
