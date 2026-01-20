# Supabase 설정 가이드

## 1. Supabase 프로젝트 생성

### 1.1 계정 생성 및 프로젝트 만들기

1. [Supabase](https://supabase.com/) 접속
2. **Start your project** 클릭
3. GitHub 계정으로 로그인
4. **New Project** 클릭
5. 프로젝트 정보 입력:
   - **Organization**: 본인 organization 선택
   - **Name**: `blackyak-mountain-tracker`
   - **Database Password**: 안전한 비밀번호 설정 (저장해두기!)
   - **Region**: `Northeast Asia (Seoul)` 선택
6. **Create new project** 클릭
7. 프로젝트 생성까지 약 2분 소요

### 1.2 API 키 확인

1. 프로젝트 대시보드에서 **Settings** > **API** 이동
2. 다음 값들을 복사해서 저장:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public**: 공개 키 (프론트엔드용)
   - **service_role**: 서비스 롤 키 (백엔드/스크립트용, 비밀!)

---

## 2. 데이터베이스 스키마 생성

### 2.1 SQL Editor에서 실행

1. Supabase 대시보드에서 **SQL Editor** 클릭
2. **New query** 클릭
3. `scripts/supabase_schema.sql` 파일 내용 전체 복사
4. SQL Editor에 붙여넣기
5. **Run** 버튼 클릭
6. "Success. No rows returned" 메시지 확인

### 2.2 테이블 확인

1. **Table Editor** 클릭
2. 다음 테이블들이 생성되었는지 확인:
   - `mountains`
   - `trails`
   - `parking_lots`
   - `highlights`
   - `user_profiles`
   - `user_completions`
   - `user_completion_photos`

---

## 3. 환경변수 설정

### 3.1 스크립트용 .env 파일

```bash
cd /Users/sunchulkim/src/blackyak-mountain-tracker/scripts
cp ../.env.example .env
```

`.env` 파일 수정:

```bash
# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 3.2 프론트엔드용 .env.local (나중에)

```bash
cd /Users/sunchulkim/src/blackyak-mountain-tracker/frontend
```

`.env.local` 파일:

```bash
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_KAKAO_MAP_API_KEY=your_kakao_key
```

---

## 4. 데이터 업로드

### 4.1 의존성 설치

```bash
cd /Users/sunchulkim/src/blackyak-mountain-tracker/scripts
source venv/bin/activate
pip install supabase python-dotenv
```

### 4.2 Dry Run (테스트)

```bash
python upload_to_supabase.py --dry-run
```

예상 출력:
```
[DRY RUN] 업로드할 데이터 99개:
{
  "name": "가리산(홍천)",
  ...
}
```

### 4.3 실제 업로드

```bash
python upload_to_supabase.py
```

예상 출력:
```
==================================================
블랙야크 100대 명산 Supabase 업로드
==================================================

[1] 데이터 로드: ../data/raw/blackyak_100.json
    로드된 산: 99개

[2] Supabase 연결
    연결 성공!

[3] 데이터 업로드
    새로 추가: 99개

[4] 업로드 검증
==================================================
[검증] mountains 테이블 레코드 수: 99개

[지역별 분포]
  강원도: 21개
  전라남도: 13개
  ...

완료!
```

### 4.4 대시보드에서 확인

1. Supabase 대시보드 > **Table Editor** > `mountains`
2. 99개 레코드 확인
3. 데이터 샘플 확인

---

## 5. 문제 해결

### "SUPABASE_URL 환경변수가 필요합니다"

```bash
# .env 파일 확인
cat .env

# 환경변수 로드 확인
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('SUPABASE_URL'))"
```

### "RLS policy violation"

Service Role Key를 사용하고 있는지 확인:
- `SUPABASE_ANON_KEY` ❌
- `SUPABASE_SERVICE_ROLE_KEY` ✅

### "relation does not exist"

SQL 스키마가 실행되지 않았습니다:
1. SQL Editor에서 `supabase_schema.sql` 다시 실행
2. Table Editor에서 테이블 확인

### PostGIS 관련 오류

PostGIS 확장이 설치되어 있지 않을 수 있습니다:
1. SQL Editor에서 실행:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```

---

## 6. 다음 단계

데이터 업로드 완료 후:

1. [ ] Frontend 프로젝트 초기화 (`npm create vite@latest`)
2. [ ] Supabase 클라이언트 설정
3. [ ] 산 목록 페이지 개발

---

## 참고 링크

- [Supabase 공식 문서](https://supabase.com/docs)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript)
- [PostGIS 문서](https://postgis.net/documentation/)
