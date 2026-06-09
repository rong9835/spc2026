# MCP (Model Context Protocol) 핵심 요약

> **MCP란?**  
> AI(Claude 등)가 외부 도구(함수)를 사용할 수 있게 해주는 **연결 규약**이다.  
> 비유: AI가 "계산기", "달력", "검색" 같은 도구 상자를 빌려 쓸 수 있는 규칙.

---

## 핵심 개념 한눈에 보기

```
[ 클라이언트 (Client) ]  ←→  [ 서버 (Server) ]
     요청하는 쪽                  도구를 가진 쪽
   "add(3, 5) 실행해줘"      "결과: 8 반환할게"
```

| 역할 | 설명 | 비유 |
|------|------|------|
| **Server** | 도구(함수)를 제공하는 쪽 | 식당 주방 (요리 제공) |
| **Client** | 도구를 호출하는 쪽 | 손님 (주문하는 사람) |
| **Tool** | 서버가 등록한 함수 | 메뉴판의 음식 항목 |
| **Handshake** | 클라이언트-서버 연결 초기화 | 식당 입장 후 자리 잡기 |

---

## 실습 파일 구성

```
1.intro_docs.py         ← MCP 버전 확인 & 공식 문서 출력
2.mcp_server.py         ← 기본 서버 (hello 도구)
3.mcp_client.py         ← 기본 클라이언트 (stdio 방식)
4.debug_server.py       ← 디버그 로그 포함 서버
5.debug_client.py       ← 디버그 프록시 통해 연결
6.mcp_server_moretools.py ← 여러 도구가 있는 서버
7.mcp_client_more.py    ← 여러 도구 호출
8.mcp_http_server.py    ← HTTP 방식 서버
9.mcp_http_client.py    ← HTTP 방식 클라이언트
debug_proxy.py          ← 메시지 감청 도구 (디버깅용)
```

---

## STEP 1 — 기본 서버 만들기 (`2.mcp_server.py`)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HelloWorld")   # 서버 이름 지정

@mcp.tool()                   # ← 이 데코레이터로 "도구" 등록
def hello(name: str) -> str:
    return f"Hello, {name}!"

mcp.run()                     # 서버 실행
```

**포인트:**
- `FastMCP` = FastAPI처럼 쉽게 MCP 서버를 만드는 클래스
- `@mcp.tool()` = 이 함수를 클라이언트가 호출할 수 있는 도구로 등록
- 도구 설명(docstring)을 달면 AI가 언제 이 도구를 쓸지 판단하는 데 사용됨

---

## STEP 2 — 기본 클라이언트 만들기 (`3.mcp_client.py`)

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 1. 서버 실행 방법 지정 (어떤 파이썬 파일을 실행할지)
    server_params = StdioServerParameters(
        command="python",
        args=["2.mcp_server.py"]
    )

    # 2. 서버와 연결
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # 3. 핸드셰이크 (악수 = 연결 초기화)
            await session.initialize()

            # 4. 도구 호출
            result = await session.call_tool("hello", {"name": "John"})
            print(result.content[0].text)  # "Hello, John!"

asyncio.run(main())
```

**실행 흐름:**
```
클라이언트 시작
   → 서버 프로세스 자동 실행
   → initialize() 로 핸드셰이크
   → call_tool() 로 함수 호출
   → 결과 받아서 출력
```

---

## STEP 3 — 여러 도구 등록 (`6.mcp_server_moretools.py`)

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """ 두 정수 a 와 b를 더한다 """
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """ 두 정수 a와 b를 곱한다 """
    return a * b

@mcp.tool()
def word_count(text: str) -> int:
    """ 주어진 문장에서 단어 갯수를 센다 """
    return len(text.split())
```

**도구 목록 조회 (`7.mcp_client_more.py`):**
```python
# 서버에 "어떤 도구 있어?" 물어보기
tools = (await session.list_tools()).tools
print([t.name for t in tools])  # ['add', 'multiply', 'word_count']

# 도구 호출
result = await session.call_tool("add", {"a": 3, "b": 5})
# → "8"
```

---

## STEP 4 — 통신 방식 2가지

### 방식 1: stdio (표준 입출력) — 기본값

```
클라이언트 → [stdin/stdout 파이프] → 서버
```
- 로컬 프로세스끼리 통신
- 서버를 자동으로 실행시켜 줌
- 간단한 테스트에 적합

### 방식 2: HTTP (streamable-http) — 네트워크

```
클라이언트 → [HTTP 요청] → 서버 (포트 8000)
```

**서버 (`8.mcp_http_server.py`):**
```python
mcp.run(transport="streamable-http")  # 이 한 줄로 HTTP 서버로 전환!
# 기본 주소: http://localhost:8000/mcp
```

**클라이언트 (`9.mcp_http_client.py`):**
```python
from mcp.client.streamable_http import streamablehttp_client

URL = "http://localhost:8000/mcp"

async with streamablehttp_client(URL) as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = (await session.list_tools()).tools
```

| 비교 | stdio | HTTP |
|------|-------|------|
| 실행 방법 | 자동 프로세스 실행 | 서버 별도 실행 후 URL 접속 |
| 사용 시나리오 | 로컬 개발, 단순 테스트 | 여러 클라이언트 동시 접속, 원격 서버 |
| 코드 변경 | `mcp.run()` | `mcp.run(transport="streamable-http")` |

---

## STEP 5 — 디버깅

### 방법 1: stderr로 로그 출력 (`4.debug_server.py`)

```python
import sys

@mcp.tool()
def hello(name: str) -> str:
    print(f"[SERVER] hello 호출됨: name={name}", file=sys.stderr)  # 로그
    return f"Hello, {name}!"
```
> `sys.stderr`에 출력하면 MCP 통신(stdout)과 섞이지 않아서 안전함

### 방법 2: 디버그 프록시 (`debug_proxy.py`)

```
클라이언트 → [프록시] → 서버
               ↓
          메시지 전부 파일에 기록 (debug_proxy.log)
```

```python
# 5.debug_client.py
server_params = StdioServerParameters(
    command="python",
    args=["debug_proxy.py", "2.mcp_server.py"]  # 프록시 경유
)
```

로그 파일(`debug_proxy.log`)에서 클라이언트↔서버 사이 오가는 JSON 메시지를 직접 확인 가능.

---

## 전체 흐름 요약

```
┌──────────────────────────────────────────────────────┐
│                    MCP 동작 순서                      │
│                                                      │
│  1. 서버 실행 (도구 등록됨)                           │
│       ↓                                              │
│  2. 클라이언트 → initialize() → 핸드셰이크           │
│       ↓                                              │
│  3. 클라이언트 → list_tools() → 사용 가능한 도구 확인 │
│       ↓                                              │
│  4. 클라이언트 → call_tool("도구명", {인자}) → 실행   │
│       ↓                                              │
│  5. 서버 → 결과 반환 → 클라이언트에서 result 출력    │
└──────────────────────────────────────────────────────┘
```

---

## 설치 & 실행

```bash
# 설치
pip install mcp

# stdio 방식 실행 (클라이언트가 서버를 자동 실행함)
python 3.mcp_client.py

# HTTP 방식 실행 (서버 먼저 실행 후 클라이언트 실행)
python 8.mcp_http_server.py   # 터미널 1
python 9.mcp_http_client.py   # 터미널 2
```

---

## 핵심 API 정리

| 코드 | 설명 |
|------|------|
| `FastMCP("이름")` | MCP 서버 생성 |
| `@mcp.tool()` | 함수를 도구로 등록 |
| `mcp.run()` | stdio 서버 실행 |
| `mcp.run(transport="streamable-http")` | HTTP 서버 실행 |
| `session.initialize()` | 핸드셰이크 (필수, 항상 먼저 호출) |
| `session.list_tools()` | 등록된 도구 목록 조회 |
| `session.call_tool("이름", {인자})` | 도구 실행 |
| `result.content[0].text` | 도구 실행 결과 텍스트 추출 |
