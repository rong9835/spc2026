# Claude Desktop + MCP 서버 만들기

> **MCP(Model Context Protocol)**를 사용해서 Claude Desktop에 나만의 기능(도구)을 추가하는 방법을 배웁니다.

---

## MCP가 뭔가요?

```
📱 Claude Desktop  ←→  🔌 MCP 서버  ←→  🌐 인터넷/파일/DB 등
```

MCP는 **Claude가 외부 기능을 사용할 수 있게 연결해주는 규격(약속)**입니다.

예를 들어, Claude에게 "구글에서 검색해줘" 또는 "내 파일 열어줘"처럼 원래는 못하는 일을 시키려면 → MCP 서버를 만들어서 연결하면 됩니다.

> 비유: MCP = 스마트폰의 **앱 스토어**. Claude라는 폰에 새로운 앱(기능)을 설치하는 것.

---

## 핵심 개념

| 용어 | 쉬운 설명 |
|------|-----------|
| **MCP 서버** | Claude에게 특정 기능을 제공하는 Python 프로그램 |
| **Tool (도구)** | `@mcp.tool()` 로 만드는 함수 하나하나 = Claude가 쓸 수 있는 기능 |
| **FastMCP** | MCP 서버를 쉽게 만드는 Python 라이브러리 |
| **stdio** | Claude Desktop과 서버가 통신하는 방식 (터미널 입출력) |

---

## 파일 구조

```
4.claude_desktop/
├── hello_server.py       # 기초 예제: 인사말 도구
└── diag_net_server.py    # 심화 예제: 네트워크 진단 도구
```

---

## 예제 1: hello_server.py (기초)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello")          # 서버 이름 지정

@mcp.tool()
async def hello(name: str) -> str:
    """ 간단한 인사말을 돌려줍니다. """
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

### 동작 방식

```
사용자: "chorong에게 인사해줘"
   ↓
Claude: hello("chorong") 도구 호출
   ↓
서버: "Hello, chorong!" 반환
   ↓
Claude: "Hello, chorong! 라고 인사합니다"
```

### 핵심 패턴

```python
@mcp.tool()          # ← 이 장식자(decorator)가 함수를 Claude 도구로 등록
async def 함수이름(파라미터: 타입) -> 반환타입:
    """ 이 설명이 Claude에게 도구의 역할을 알려줍니다 """
    return 결과
```

> 주의: 설명(docstring)을 잘 써야 Claude가 언제 이 도구를 써야 할지 알 수 있어요!

---

## 예제 2: diag_net_server.py (심화)

네트워크 진단 기능 2가지를 제공하는 서버입니다.

```python
mcp = FastMCP("simple-net-diag-server")
```

### 도구 1: `fetch_page` — 웹 페이지 가져오기

```python
@mcp.tool()
async def fetch_page(host: str, port: int = 80, path: str = "/", max_bytes: int = 100_000) -> dict:
```

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `host` | 필수 | 접속할 도메인 또는 IP (예: `google.com`) |
| `port` | `80` | 포트 번호 (HTTP=80, HTTPS=443) |
| `path` | `"/"` | URL 경로 (예: `/about`) |
| `max_bytes` | `100,000` | 최대 100KB까지만 가져옴 |

**반환 예시 (성공)**
```json
{
  "ok": true,
  "url": "http://example.com:80/",
  "status": 200,
  "content_type": "text/html",
  "body": "<!DOCTYPE html>..."
}
```

**반환 예시 (실패)**
```json
{
  "ok": false,
  "error": "HTTP 404",
  "reason": "Not Found"
}
```

---

### 도구 2: `ping_host` — ping 테스트

```python
@mcp.tool()
async def ping_host(host: str, count: int = 3, timeout_sec: int = 3) -> str:
```

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `host` | 필수 | ping할 대상 (예: `8.8.8.8`) |
| `count` | `3` | ping 횟수 (1~5) |
| `timeout_sec` | `3` | 응답 대기 시간 초 (1~5) |

**OS별 자동 처리**
```python
if platform.system() == "Windows":
    cmd = ['ping', '-n', count, ...]   # 윈도우
else:
    cmd = ['ping', '-c', count, ...]   # Mac/Linux
```

> 내부적으로 운영체제의 ping 명령어를 실행하고 결과를 텍스트로 돌려줍니다.

---

## 오류 처리 패턴

`fetch_page`에서 배우는 좋은 습관:

```python
try:
    # 정상 동작
    return {"ok": True, ...}

except HTTPError as e:          # HTTP 오류 (404, 500 등)
    return {"ok": False, "error": f"HTTP {e.code}"}

except URLError as e:           # 네트워크 연결 오류
    return {"ok": False, "error": "URL Error"}

except Exception as e:          # 그 외 모든 오류
    return {"ok": False, "error": type(e).__name__}
```

오류 발생해도 프로그램이 죽지 않고 **오류 내용을 담아 반환**합니다.

---

## Claude Desktop에 연결하는 방법

### 1. 설정 파일 열기

| OS | 경로 |
|----|------|
| Mac | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

### 2. 서버 등록

```json
{
  "mcpServers": {
    "hello": {
      "command": "python",
      "args": ["/절대경로/hello_server.py"]
    },
    "net-diag": {
      "command": "python",
      "args": ["/절대경로/diag_net_server.py"]
    }
  }
}
```

### 3. Claude Desktop 재시작

재시작 후 채팅창에 🔌 아이콘이 보이면 연결 성공!

---

## 나만의 MCP 서버 만드는 템플릿

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("내서버이름")

@mcp.tool()
async def 내도구(입력: str) -> str:
    """
    Claude에게 이 도구가 무엇을 하는지 설명합니다.
    Claude는 이 설명을 보고 도구 사용 여부를 결정합니다.
    """
    결과 = 입력을_처리하는_코드(입력)
    return 결과

if __name__ == "__main__":
    mcp.run(transport="stdio")   # Claude Desktop은 stdio 방식
```

---

## 요약 정리

```
✅ MCP = Claude에게 새 기능을 추가하는 방법
✅ @mcp.tool() = 함수를 Claude 도구로 등록하는 장식자
✅ FastMCP = MCP 서버를 쉽게 만드는 라이브러리
✅ docstring = Claude에게 도구 사용법을 알려주는 설명
✅ transport="stdio" = Claude Desktop 연결 방식
```
