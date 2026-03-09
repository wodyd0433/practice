## 함수 설계 방법

---

### 1. 큰 그림부터 그린다

코드 짜기 전에 **말로 먼저** 정리합니다.

```
"서울 출발지에서 목적지까지의 OD 데이터를 수집해서 CSV로 저장한다"

→ 이걸 하려면 뭐가 필요하지?

1. API 키 로드
2. 세션 생성
3. 행정구역 코드 가져오기
4. OD 데이터 수집
5. CSV 저장
```

---

### 2. 명사와 동사로 구분한다

```
명사 (데이터)  →  클래스 또는 변수
동사 (행동)    →  함수

"API 키를 로드한다"          → load_env()
"세션을 만든다"              → make_session()
"행정구역 코드를 가져온다"    → fetch_area_codes()
"OD 데이터를 수집한다"       → collect_quarter_od()
"구 단위로 집계한다"         → build_gu_aggregate()
"전체를 실행한다"            → run_collection()
```

---

### 3. 함수 하나 = 역할 하나

```python
# ❌ 나쁜 설계 - 한 함수가 너무 많은 일
def do_everything():
    apikey = os.getenv(...)
    session = requests.Session()
    area_codes = requests.get(...)
    for area in area_codes:
        data = requests.get(...)
        # ... 200줄
    pd.DataFrame(rows).to_csv(...)
    json.dump(meta)

# ✅ 좋은 설계 - 역할별로 분리
def load_env()            # API 키 로드만
def make_session()        # 세션 생성만
def fetch_area_codes()    # 행정구역 코드만
def collect_quarter_od()  # OD 수집만
def run_collection()      # 위 함수들을 조립
```

---

### 4. 입력 → 처리 → 출력 순서로 생각

```
함수를 설계할 때 항상 이 3가지를 먼저 정합니다.

fetch_area_codes(session, apikey)  →  pd.DataFrame
       ↑ 입력                          ↑ 출력
           처리: API 호출 후 테이블로 변환

collect_quarter_od(session, apikey, origins, ...)  →  tuple[pd.DataFrame, dict]
       ↑ 입력                                           ↑ 출력
           처리: 출발지마다 API 호출 후 데이터 수집
```

---

### 5. 위에서 아래로 계층을 나눈다

```
run_collection()          ← 최상위: 전체 흐름 조립
 │
 ├── load_env()           ← 중간: 개별 작업
 ├── make_session()
 ├── fetch_area_codes()
 │     └── call_api()    ← 하위: 가장 작은 단위
 │
 └── collect_quarter_od()
       └── call_api()
```

```
위로 갈수록  →  큰 흐름, 조립
아래로 갈수록 →  작은 단위, 재사용
```

---

### 6. 실제 설계 순서

```
1단계: 말로 정리
  "뭘 만들어야 하지?"

2단계: 큰 함수 먼저
  run_collection() 껍데기만 작성
  def run_collection():
      pass

3단계: 필요한 하위 함수 도출
  run_collection 을 구현하다 보면
  "여기서 세션이 필요하네" → make_session()
  "여기서 API 호출이 필요하네" → call_api()
  자연스럽게 하위 함수가 보임

4단계: 하위 함수부터 구현
  call_api() 먼저 완성
  fetch_area_codes() 완성
  collect_quarter_od() 완성
  run_collection() 마지막에 조립

5단계: 테스트
  각 함수를 개별적으로 테스트
```

---

### 정리

```
설계 잘 하는 방법

1. 말로 먼저 정리한다
2. 명사(데이터)와 동사(행동)를 구분한다
3. 함수 하나에 역할 하나만 준다
4. 입력 → 처리 → 출력을 먼저 정한다
5. 큰 함수에서 작은 함수로 쪼갠다
6. 하위 함수부터 구현하고 마지막에 조립한다
```

**처음부터 완벽하게 설계할 필요 없습니다.
일단 동작하게 만들고, 중복되거나 너무 길어지면 그때 쪼개도 됩니다.**
