# 가상자산 퀀트 시뮬레이션 플랫폼 구축 워크플로우 (Workflow)

## 1. 프로젝트 개요 (Overview)
- **목적:** 가상자산 거래소(업비트, 빗썸, 코인원)의 시세를 수집하고, 퀀트 알고리즘 별 수익률(일/주/월간)을 시뮬레이션하여 비교할 수 있는 웹 프로덕트.
- **특징:** 실제 매매가 아닌 **시세 데이터 기반 가상 수익률 시뮬레이션**. 비개발자도 이해하기 쉬운 직관적인 구조와 새로운 거래소/알고리즘을 쉽게 추가할 수 있는 모듈형 아키텍처.
- **기술 스택:** Python, Streamlit, Pandas, Plotly. (로컬 환경에 Node.js가 없어 Python 기반의 최적 프레임워크인 Streamlit 적용)
- **배포 인프라:** Streamlit Community Cloud (무료 호스팅, GitHub 연동 자동 배포).

---

## 2. 시스템 아키텍처 및 폴더 구조 (Architecture)

파이썬 기반으로 비개발자도 구조를 쉽게 파악할 수 있도록 직관적으로 구성합니다.

```text
/quant-sim
  app.py                 # Streamlit 웹 애플리케이션 메인 엔트리포인트
  requirements.txt       # 파이썬 의존성 패키지 목록
  /exchanges             # 거래소별 시세 조회 모듈
    __init__.py
    upbit.py
    bithumb.py
    coinone.py
  /algorithms            # 퀀트 투자 알고리즘 모음
    __init__.py
    base.py              # 알고리즘 공통 인터페이스
    moving_average.py    # 이동평균선 교차 전략 예시
  /simulator             # 시뮬레이션 엔진
    __init__.py
    engine.py            # 데이터를 바탕으로 가상 수익률 계산 및 비교
```

---

## 3. 핵심 모듈 구현 방식 (Implementation Plan)

### A. 거래소 시세 수집 모듈 (`/exchanges`)
- `ccxt` 라이브러리 또는 `requests`를 통해 각 거래소의 REST API(캔들 데이터)를 주기적으로(또는 요청 시) 수신.
- 반환되는 데이터를 `Pandas DataFrame`으로 통일하여 시뮬레이터에 공급.

### B. 퀀트 알고리즘 엔진 (`/algorithms`)
- 기본 데이터(시가, 종가, 고가, 저가, 거래량 등)를 입력받아 매수/매도 시그널 및 수익률을 계산.
- `base.py`에 정의된 `BaseStrategy` 클래스를 상속받아 누구나 새로운 `.py` 파일을 생성해 전략을 쉽게 추가할 수 있는 구조(확장성).

### C. 시뮬레이션 및 데이터 시각화 (`app.py`, `/simulator`)
- 수집된 시세를 바탕으로 퀀트 알고리즘을 적용하여 일간(Daily), 주간(Weekly), 월간(Monthly) 수익률을 도출.
- `Plotly` 차트를 이용해 Streamlit 대시보드에서 직관적으로 성과를 비교.

---

## 4. 진행 및 배포 자동화 단계 (Deployment & Automation)

### 단계 1: 프로젝트 로컬 개발 및 임시 배포 (현재 진행 중)
1. Python/Streamlit 보일러플레이트 및 코어 로직 작성.
2. 작성 완료 직후 SSH 터널링(`localhost.run` 등)을 통해 **즉시 웹에서 확인 가능한 임시 URL** 제공.

### 단계 2: Streamlit Community Cloud를 통한 영구 호스팅 및 자동화
- **이유:** 무료이며, 데이터 앱에 특화된 호스팅 환경을 제공합니다. GitHub에 코드를 푸시하면 **자동 배포(Auto Deployment)**가 이루어집니다.
- **과정:**
  1. 본 프로젝트 폴더를 사용자의 GitHub 레포지토리에 커밋 및 푸시.
  2. [share.streamlit.io](https://share.streamlit.io/)에 로그인 후 `New app` 클릭.
  3. GitHub 레포지토리와 `app.py` 경로만 지정하면 배포 완료. (코드 수정 시 자동 재배포)

### 단계 3: 추후 고도화 옵션
- 거래소 모듈 추가, 퀀트 알고리즘 다변화.
- 사용자가 많아지고 인증(로그인) 기능이 필요해지면 Streamlit Auth 컴포넌트나 Supabase 연동 시도.

---

## 5. 요약 (Summary)
파이썬 생태계 최고의 데이터 웹 프레임워크인 **Streamlit**을 이용하여 빠르고 인터랙티브하게 수익률 비교 대시보드를 구축합니다. 초기 배포는 무료 호스팅인 **Streamlit Community Cloud**를 이용해 CI/CD(자동 배포)를 구현하며, 향후 알고리즘 파일(`.py`)을 폴더에 추가하는 것만으로 기능이 확장되도록 설계되었습니다.
