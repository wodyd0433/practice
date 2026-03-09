## requests.Session() 완전 정리

---

### Q1. `requests.Session()`이란? 빈 껍데기인가?

**A.** 맞습니다. 처음엔 빈 껍데기입니다.

```python
session = requests.Session()  # 아직 아무 서버에도 연결 안 함
                               # 그냥 "설정 보관함" 생성
```

비유하자면:

```
requests.get(url)  →  매번 새 택시를 잡는 것
                      (탑승 → 목적지 → 하차 → 택시 사라짐)

requests.Session() →  전용 기사를 고용하는 것
                      (한 번 계약 → 계속 같은 기사 사용)
```

생성 시점 vs 연결 시점:

```python
# 1단계: 빈 껍데기 생성 (서버 연결 X)
session = requests.Session()

# 2단계: 설정 추가 (서버 연결 X)
session.headers.update({"Authorization": "Bearer TOKEN"})

# 3단계: 여기서 비로소 실제 서버 연결
session.get("https://api.example.com/data")  # ← 이때 TCP 연결 발생
```

---

### Q2. `session`을 쓰는 이유는?

**A.** TCP 연결 재사용, 헤더/쿠키/인증 정보 자동 유지입니다.

**TCP 연결 재사용**

```python
# session 없이 매번 연결
requests.get(url)  # TCP 연결 생성 → 요청 → 응답 → 종료
requests.get(url)  # TCP 연결 생성 → 요청 → 응답 → 종료

# session 사용
session = requests.Session()
session.get(url)   # TCP 연결 생성 → 요청 → 응답
session.get(url)   #  ↑ TCP 연결 재사용 → 요청 → 응답
```

**헤더 자동 유지**

```python
# session 없이 → 매번 헤더를 넣어야 함
requests.get(url, headers={"Authorization": "Bearer TOKEN"})
requests.get(url, headers={"Authorization": "Bearer TOKEN"})

# session 사용 → 한 번만 설정하면 자동 적용
session.headers.update({"Authorization": "Bearer TOKEN"})
session.get(url)  # 헤더 자동 포함
session.get(url)  # 헤더 자동 포함
```

**쿠키 자동 유지**

```python
session.post(url, data={"id": "user", "pw": "1234"})  # 로그인
session.get("https://example.com/mypage")  # 로그인 상태 자동 유지
```

| 항목     | Session 없음          | Session 있음 |
| -------- | --------------------- | ------------ |
| TCP 연결 | 매 요청마다 새로 생성 | 재사용       |
| 헤더     | 매 요청마다 직접 전달 | 자동 유지    |
| 쿠키     | 매 요청마다 직접 전달 | 자동 유지    |
| 인증     | 매 요청마다 직접 전달 | 자동 유지    |
| 성능     | 느림                  | 빠름         |

---

### Q3. `session` 내부에 어떤 변수들이 담기나?

**A.** 실제로 확인해보면:

```python
session = requests.Session()
print(session.__dict__)
# {
#   'headers': {
#       'User-Agent': 'python-requests/2.31.0',
#       'Accept-Encoding': 'gzip, deflate',
#       'Accept': '*/*',
#       'Connection': 'keep-alive'
#   },
#   'auth': None,
#   'proxies': {},
#   'hooks': {'response': []},
#   'params': {},
#   'stream': False,
#   'verify': True,
#   'cert': None,
#   'max_redirects': 30,
#   'trust_env': True,
#   'cookies': <RequestsCookieJar[]>,
#   'adapters': {
#       'https://': <HTTPAdapter>,
#       'http://':  <HTTPAdapter>
#   }
# }
```

**자주 쓰는 것들**

```python
session.headers    # 요청 헤더 (기본값 이미 들어있음)
session.auth       # 인증 정보
session.params     # 공통 쿼리 파라미터
session.cookies    # 쿠키 저장소
session.verify     # SSL 인증서 검증 여부
```

**기본 헤더가 이미 들어있는 이유**

```python
session = requests.Session()
print(session.headers)
# {
#   'User-Agent': 'python-requests/2.31.0',  ← 어떤 클라이언트인지
#   'Accept-Encoding': 'gzip, deflate',       ← 압축 형식
#   'Accept': '*/*',                           ← 모든 응답 형식 허용
#   'Connection': 'keep-alive'                 ← TCP 연결 유지
# }

session.headers.update({"Authorization": "Bearer TOKEN"})
# 기존 헤더 유지 + Authorization 추가됨
```

**adapters가 실제 TCP 연결 담당**

```python
session.adapters = {
    'https://': HTTPAdapter(),  # https 요청 처리
    'http://':  HTTPAdapter()   # http 요청 처리
}
# HTTPAdapter 안에 TCP 연결 풀이 있음
# → 연결을 재사용할 수 있는 이유
```

---

### Q4. `session`에 저장한 값이 응답으로 덮어씌워지나?

**A.** 덮어씌워지지 않습니다. 방향이 반대이기 때문입니다.

```
session에 저장한 설정  →  요청할 때 서버로 보내는 것
서버의 응답           →  받아서 response에 저장되는 것
```

```python
# session → 내가 서버에 보낼 설정 보관함
session.headers.update({"Authorization": "Bearer TOKEN"})

# response → 서버가 나에게 준 응답 보관함
response = session.get(url)

print(session.headers)    # 내가 보낸 헤더 (변하지 않음)
print(response.headers)   # 서버가 준 헤더 (별개)
print(response.json())    # 서버가 준 데이터 (별개)
```

**예외: 쿠키는 자동으로 업데이트됨**

```python
session.post(url, data={"id": "user", "pw": "1234"})
# 서버가 응답에 쿠키를 담아서 줌
# → session.cookies에 자동 저장 (로그인 상태 유지 목적)
# 덮어씌우는 게 아니라 의도적으로 유지하는 것
```

```
session.headers  →  서버로 나가는 방향 (요청)  →  응답으로 변하지 않음
session.cookies  →  서버로 나가는 방향 (요청)  →  서버 응답 쿠키만 자동 추가
response         →  서버에서 오는 방향 (응답)  →  session과 별개 공간
```

---

### Q5. `headers["Authorization"]`과 `session.auth` 차이는?

**A.** 누가 형식을 만드냐의 차이입니다.

```
session.headers["Authorization"]  →  내가 직접 만들어서 넣는 것
session.auth                      →  requests가 자동으로 만들어주는 것
```

```python
# headers 직접 설정 → 형식까지 직접 지정
session.headers.update({
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9..."
})
# 전송: Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...

# session.auth → requests가 Base64로 자동 변환
session.auth = ("username", "password")
# 전송: Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

| 상황             | 방법                                            |
| ---------------- | ----------------------------------------------- |
| JWT 토큰 인증    | `headers["Authorization"] = "Bearer TOKEN"`   |
| API Key 인증     | `headers["Authorization"] = "Api-Key MY_KEY"` |
| ID/PW Basic 인증 | `session.auth = ("username", "password")`     |

---

### Q6. `session.params.update()`가 동작하지 않는 것 같다

**A.** 맞습니다. `update()` 대신 직접 대입을 사용하세요.

```python
# ❌ 신뢰하기 어려움
session.params.update({"apikey": API_KEY})

# ✅ 직접 대입
session.params = {"apikey": API_KEY}

# ✅ 호출 시 직접 전달 (가장 명확)
call_api(session, "areacode.json", {"apikey": API_KEY})
```

---

### Q7. `with requests.Session()`과 직접 생성의 차이는?

**A.** `with` 블록이 끝나면 자동으로 `close()`가 호출됩니다.

```python
# ❌ with 블록 안에서 생성 후 return
with requests.Session() as session:
    session.headers.update({"User-Agent": "API-practice/1.0"})
return session  # 이미 닫힌 session을 return!

# ✅ 직접 생성 후 return
session = requests.Session()
session.headers.update({"User-Agent": "API-practice/1.0"})
return session  # 열린 상태로 return → 정상 동작
```

**올바른 with문 사용 패턴**

```python
# with 안에서 모든 작업을 끝내는 경우
def fetch_data():
    with requests.Session() as session:
        session.headers.update({"User-Agent": "API-practice/1.0"})
        result = session.get(url)
        return result.json()  # 데이터만 반환

# session을 밖으로 넘겨야 하는 경우
session = requests.Session()  # with 없이 생성
session.headers.update(...)
return session                 # 열린 채로 반환

# 사용하는 쪽에서 닫기
with create_session() as session:
    session.get(url)
# with 블록 끝나면 자동 close
```

```
with 안에서 return  →  ❌ 닫힌 session 반환
직접 생성 후 return →  ✅ 열린 session 반환
session을 return 해야 한다면 with 없이 직접 생성
```

---

### Q8. python-dotenv로 API Key를 로드해서 session에 담는 방법은?

**A.** `.env` 파일에서 로드 후 session에 설정합니다.

```bash
# .env
API_KEY=my-secret-api-key-12345
API_ROOT=https://api.example.com
```

```python
from dotenv import load_dotenv
import os, requests

load_dotenv()
API_KEY  = os.getenv("API_KEY")
API_ROOT = os.getenv("API_ROOT")

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {API_KEY}"})
```

**API Key 전달 방식은 서비스마다 다름**

```python
# 방식 1. Header Bearer 토큰
session.headers.update({"Authorization": f"Bearer {API_KEY}"})
# 요청: Authorization: Bearer my-secret-api-key-12345

# 방식 2. Header 직접
session.headers.update({"X-API-Key": API_KEY})
# 요청: X-API-Key: my-secret-api-key-12345

# 방식 3. 쿼리 파라미터 (지금 코드 방식)
call_api(session, "areacode.json", {"apikey": API_KEY})
# 요청: https://api.example.com/areacode.json?apikey=my-secret-api-key-12345
```

**전체 흐름**

```
.env 파일 → load_dotenv() → os.getenv() → session 설정 → 서버 전송
```
