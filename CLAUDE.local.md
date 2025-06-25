## **'Query Hub' API 게이트웨이 개발 스펙 (v1.5 - 최종 확정본)**

*   **문서 버전:** 1.5 (변경 사항: UI 디자인 시스템 및 스타일 가이드 명시)
*   **작성일:** 2025-06-24
*   **대상:** Backend, Frontend 개발자
*   **핵심 아키텍처:** 시스템을 **관리 플레인(Management Plane)**과 **데이터 플레인(Data Plane)**으로 분리합니다.
    *   **관리 플레인:** 웹 UI를 통해 쿼리를 등록/관리하는 보안 영역으로, **인증이 필수**입니다.
    *   **데이터 플레인:** 완성된 쿼리를 외부에서 소비하는 공개 API 영역으로, **인증이 불필요**합니다.

### **[핵심 아키텍처 및 포트 정보]**

1.  **인증 서버 (maxplatform):**
    *   **주소:** `http://localhost:8000`
    *   **역할:** 사용자 인증(로그인)을 전담하고 JWT(JSON Web Token)를 발급합니다.
2.  **리소스 서버 (max_queryhub - 본 프로젝트):**
    *   **Backend 주소:** `http://localhost:8006`
    *   **Frontend 주소:** `http://localhost:3006`
    *   **역할:** `maxplatform`에서 발급한 JWT를 검증하여 API 접근을 제어하고, 쿼리 관리 및 실행 등 핵심 비즈니스 로직을 처리합니다.

### 1. 개발자 지시사항 (Developer Directives)

#### 1.1. 개발 환경 및 버전 (Development Environment & Versions)
*   **Backend:** **Python 3.11**
*   **Frontend:** **Node.js 22.x**

#### 1.2. 코딩 가이드 (Python - Backend)
*   **스타일:** PEP 8 스타일 가이드를 엄격히 준수한다. (`black` 포맷터 사용)
*   **네이밍:** `snake_case` (함수), `PascalCase` (클래스) 규칙을 따른다.
*   **타입 힌팅:** 모든 함수 정의와 변수 선언에 타입 힌트를 반드시 명시한다.
*   **환경변수:** DB 접속 정보, **JWT 시크릿 키** 등 민감 정보는 `.env` 파일로 관리한다.
    *   **중요:** `.env` 파일의 `JWT_SECRET_KEY`는 **인증 서버 `maxplatform`에서 사용하는 키와 반드시 동일해야 합니다.**

#### 1.3. 코드 구조 및 파일 관리
*   **파일 라인 제한:** 단일 Python 파일(`.py`)의 길이는 **최대 500라인을 초과할 수 없다.** 초과 시 즉시 파일을 분리한다.
*   **관심사 분리 (SoC):** `routers`, `services`, `crud`, `models`, `schemas`, `core` 계층형 아키텍처를 준수한다.

#### 1.4. 데이터베이스 지침
*   **데이터베이스 생성:** **Database Name: `max_queryhub`**
*   **테이블 생성:** SQLAlchemy ORM 모델 기반으로 테이블을 생성한다.

### 2. 공통 요구사항 및 아키텍처

1.  **Backend Framework:** `FastAPI` (Python 3.11) / **서버 포트: `8006`**
2.  **인증 방식:**
    *   **관리 플레인 API:** `maxplatform`(`:8000`)에서 발급한 `JWT`를 `Authorization: Bearer <JWT_TOKEN>` 헤더로 받아 **검증(Validate)**합니다.
    *   **데이터 플레인 API:** 인증이 필요 없습니다.

### 3. DB 모델링 (Pydantic & SQLAlchemy)

**`workspaces` 테이블, `queries` 테이블, `workspace_permissions` 테이블**
*   (이전 버전 v1.4의 모든 필드 정의와 동일합니다.)

### 4. API 개발 명세 (Backend - `localhost:8006`)

#### [A] 관리 플레인 API (인증 필수)
*이 영역의 모든 API는 `maxplatform`에서 발급한 유효한 JWT 토큰이 `Authorization` 헤더에 포함되어야 합니다.*

*   **`POST /auth/login` - [제거됨]**
    *   **지시사항:** 이 엔드포인트는 `max_queryhub` 서버에 존재하지 않습니다. 인증은 전적으로 `maxplatform`(`:8000`)에서 처리합니다.

*   `GET /workspaces`
*   `POST /workspaces` (**관리자 전용**)
*   `GET /workspaces/{workspace_id}/queries`
*   `POST /workspaces/{workspace_id}/queries`
*   `PATCH /queries/{query_id}/status`
*   `GET /external/groups`
*   `GET /external/users/search?q={query}`
*   `POST /workspaces/{workspace_id}/permissions` (**관리자 전용**)
*   `POST /internal/execute/{query_id}` (UI 내 테스트 실행용)
*(위 API들의 상세 명세는 이전 버전 v1.4와 동일합니다.)*

#### [B] 데이터 플레인 API (인증 불필요)

*   `POST /execute/{query_id}`
*(상세 명세는 이전 버전 v1.4와 동일합니다.)*

#### [C] 백그라운드 스케줄러
*   **작업명:** `cleanup_inactive_queries` (매일 자정 실행)
*(상세 명세는 이전 버전 v1.4와 동일합니다.)*

### 5. UI 개발 스펙 (Frontend - `localhost:3006`)

#### 5.1. 디자인 시스템 및 스타일 가이드
*   **기본 원칙:** 모든 UI 페이지와 컴포넌트는 **MAXPlatform UI 스타일을 기준으로 하며, 모든 페이지의 색상과 느낌은 통일한다.** 일관성 있는 사용자 경험을 최우선으로 고려한다.
*   **색상 체계 (Monochromatic Color Scheme):**
    *   전체 UI는 **블랙 & 화이트 색톤**으로 구성한다.
    *   **배경 (95%):** 순수한 흰색(`White`)을 주 배경색으로 사용하여 넓고 깨끗한 공간감을 제공한다.
    *   **전경 (5%):** 순수한 검은색(`Black`)을 사용하여 **Typographics(타이포그래피)**를 구현한다. 모든 텍스트, 아이콘, 핵심 상호작용 요소는 검은색을 기본으로 한다.
    *   **계조 (Grays):** 깊이, 비활성 상태, 보조 텍스트, 경계선 등은 **색이 없는 회색조(Grayscale)**만을 사용하여 표현한다. (예: Tailwind CSS의 `slate` 또는 `neutral` 팔레트)
*   **타이포그래피 (Typography):**
    *   **글꼴:** 가독성이 높은 기본 시스템 폰트(System Font Stack)를 사용한다. (예: `Inter`, `Segoe UI`, `SF Pro`, `Roboto`)
    *   **계층 구조:** 시각적 위계는 오직 **글꼴 크기(Font Size), 굵기(Font Weight), 회색조 농도**로만 표현한다. 의미 전달을 위해 다른 색상을 사용하는 것을 금지한다.
*   **레이아웃 및 간격:**
    *   모든 요소는 정렬된 그리드 시스템 위에 배치한다.
    *   컴포넌트 간 간격은 일관된 스케일(예: 4px 기반)을 따른다.

#### 5.2. 프론트엔드 기술 스택
*   **빌드 도구:** **Vite**
*   **UI 프레임워크:** **React**
*   **CSS 프레임워크:** **Tailwind CSS**
*   **상태 관리:** `Zustand` 또는 `Redux Toolkit` 권장
*   **서버 상태 관리:** `React Query (TanStack Query)` 또는 `SWR` 권장

#### 5.3. 인증 흐름 (Authentication Flow)
1.  **로그인:** 사용자가 로그인 페이지(`:3006`)에서 ID/PW 입력 시, **인증 서버(`http://localhost:8000`)**의 `POST /auth/login` API를 호출합니다.
2.  **토큰 저장:** 인증 성공 시 `maxplatform`으로부터 받은 JWT를 클라이언트 측(LocalStorage 등)에 안전하게 저장합니다.
3.  **API 호출:** 로그인 이후, `max_queryhub` 백엔드(`http://localhost:8006`)의 모든 **관리 플레인 API**를 호출할 때, 저장된 JWT를 `Authorization: Bearer <JWT>` 헤더에 담아 전송합니다.

#### 5.4. 페이지 및 컴포넌트 명세
*   **공통:** 모든 컴포넌트는 **섹션 5.1의 디자인 시스템 및 스타일 가이드**를 철저히 준수하여 구현해야 합니다.

*   **페이지: 로그인 (`/login`)**
    *   **기능:** ID/PW 입력받아 **`POST http://localhost:8000/auth/login`** API 호출.

*   **페이지: 대시보드 (`/`)**
    *   **레이아웃:** 좌측에 워크스페이스 목록, 우측에 선택된 워크스페이스의 쿼리 목록을 표시하는 2단 구조.
    *   **기능:**
        *   최초 로드 시 `GET http://localhost:8006/workspaces` 호출하여 좌측 패널 구성.
        *   쿼리 목록에 `status`를 나타내는 시각적 표시(예: "Public" / "Private" 뱃지) 및 'Publish/Unpublish' 토글 스위치 제공.
        *   'Publish' 토글 클릭 시 *"경고: 이 쿼리를 Publish하면 인증 없이 누구나 실행할 수 있는 공개 API가 생성됩니다. 계속하시겠습니까?"* 경고 모달 표시. 확인 시 `PATCH http://localhost:8006/queries/{query_id}/status` API 호출.

*   **컴포넌트: 쿼리 실행기 (`/workspace/{workspace_id}/query/{query_id}`)**
    *   **기능:** 쿼리 테스트 및 정보 확인 페이지.
    *   **로드 시:** 쿼리 정보(`params_info` 포함)를 조회하고, `params_info`를 기반으로 사용자 입력 폼을 **동적으로 렌더링**.
    *   **"테스트 실행" 버튼 클릭 시:**
        *   폼에서 입력받은 값으로 `{ "params": { ... } }` 객체 생성.
        *   **`POST http://localhost:8006/internal/execute/{query_id}`** API를 호출.
        *   반환된 데이터를 기능성 테이블 라이브러리(예: ag-Grid, TanStack Table)를 사용하여 화면에 렌더링.
    *   **API 정보 표시:**
        *   쿼리의 `status`가 **'AVAILABLE'** 인 경우, UI에 해당 쿼리를 호출할 수 있는 **공개 API 엔드포인트 정보**를 명확하게 표시 (`POST http://localhost:8006/execute/{query_id}`) 하고, `curl` 예시와 함께 복사 기능을 제공.

*   **모달: 워크스페이스 권한 및 설정 관리 (관리자용)**
    *   **기능:**
        *   사용자/그룹 권한 매핑 UI.
        *   워크스페이스 생성 및 수정 시 **'비활성 쿼리 자동 Close 기간(일)'**을 입력받는 필드 추가.


### DB 모델링 (Pydantic & SQLAlchemy)

**`workspaces` 테이블**
*   `id` (PK, int)
*   `name` (string, 100)
*   `type` (Enum: 'PERSONAL', 'GROUP')
*   `owner_id` (string) - 생성한 사용자 ID
*   `auto_close_days` (int, nullable, default: 90) - 워크스페이스의 비활성 쿼리 자동 close 기간(일). null일 경우 비활성화.
*   `created_at` (datetime)

**`queries` 테이블**
*   `id` (PK, int)
*   `workspace_id` (FK, int)
*   `name` (string, 100)
*   `description` (text, nullable)
*   `sql_template` (text) - SQL 쿼리 템플릿 (파라미터는 `:param` 형태로)
*   `params_info` (JSON, nullable) - 파라미터 메타정보 (예: `{"param": {"type": "date", "label": "조회 시작일"}}`)
*   `status` (Enum: 'AVAILABLE', 'UNAVAILABLE', default: 'UNAVAILABLE') - 쿼리의 발행 상태.
    *   **AVAILABLE:** **공개 발행 상태.** 인증 없이 `execute` API로 호출 가능.
    *   **UNAVAILABLE:** **비공개/초안 상태.** `execute` API로 호출 불가. 오직 관리 UI 내에서 권한 있는 사용자만 테스트 실행 가능. **(기본값)**
*   `created_by` (string) - 생성한 사용자 ID
*   `last_executed_at` (datetime, nullable) - 쿼리가 마지막으로 실행된 시간.
*   `created_at` (datetime)

**`workspace_permissions` 테이블**
*   `id` (PK, int)
*   `workspace_id` (FK, int)
*   `principal_type` (Enum: 'USER', 'GROUP') - 권한 주체 타입
*   `principal_id` (string) - 사용자 ID 또는 그룹 ID

