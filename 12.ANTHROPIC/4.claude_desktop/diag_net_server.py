import asyncio, platform, socket, sys, logging

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("simple-net-diag-server")

logger = logging.getLogger("simple-net-diag-server")

@mcp.tool()
async def fetch_page(
    host: str,
    port: int = 80,
    path: str = "/",
    max_bytes: int = 100_000
) -> dict:
    """
    간단한 페이지 GET(HTTP)을 통해서 가져온 결과를 반환합니다.
    - path 는 기본 '/' 이며 원하는 경로를 추가할수도 있습니다.
    - max_bytes 까지만 가져오며, 기본값은 100kb 입니다.
    """
    from urllib.parse import quote
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError

    url = f"http://{host}:{port}{quote(path)}"
    req = Request(url, headers={"User-Agent": "simple-net-mcp/1.0"})

    try:
        with urlopen(req, timeout=5) as resp:
            data = resp.read(max_bytes)

            return {
                "ok": True,
                "url": url,
                "status": resp.status,
                "content_type": resp.headers.get("Content-Type"),
                "body": data.decode("utf-8", errors="replace"),
            }

    except HTTPError as e:
        return {
            "ok": False,
            "error": f"HTTP {e.code}",
            "reason": str(e),
        }

    except URLError as e:
        return {
            "ok": False,
            "error": "URL Error",
            "reason": str(e.reason),
        }

    except Exception as e:
        return {
            "ok": False,
            "error": type(e).__name__,
            "reason": str(e),
        }


@mcp.tool()
async def ping_host(host: str, count: int=3, timeout_sec: int=3) -> str:
    """ 
    지정한 host 로 ping을 하여 결과를 반환합니다.
     - count: 1~5까지 
     - timeout_sec: 1~5초 (패킷 당 타임아웃)
    """

    host = (host or "").strip()
    if not host:
        raise ValueError("Host 를 입력하세요.")
    
    if platform.system() == "Windows":
        cmd = ['ping', '-n', str(count), '-w', str(timeout_sec * 1000), host]
    else:
        cmd = ['ping', '-c', str(count), '-w', str(timeout_sec), host]

    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, err = await proc.communicate()

    if isinstance(out, bytes):
        text = out.decode("utf-8", "ignore")
        if not text:
            text = err.decode("utf-8", "ignore")

    logger.info(f"[내로그] ping 출력결과: {text}")

    return text

if __name__ == "__main__":
    mcp.run(transport="stdio")
