#!/usr/bin/env python3
import json
import sys
import subprocess
import threading
import os

def log_message(msg):
    """로그를 stderr과 별도 파일에 동시 출력"""
    print(msg, file=sys.stderr)
    # 로그 파일에도 저장
    with open("debug_proxy.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
        f.flush()

def main():
    if len(sys.argv) < 2:
        log_message("[PROXY] 사용법: python debug_proxy.py <서버파일>")
        return
    
    server_file = sys.argv[1]
    
    # 로그 파일 초기화
    with open("debug_proxy.log", "w", encoding="utf-8") as f:
        f.write("=== MCP Proxy Debug Log ===\n")
    
    # 서버 시작
    log_message(f"[PROXY] 서버 시작: {server_file}")
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    
    server = subprocess.Popen(
        ["python", server_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',  # 인코딩 에러 시 ?로 대체
        bufsize=1,
        env=env
    )
    
    # 서버 stderr 로깅
    def log_server_stderr():
        while True:
            try:
                line = server.stderr.readline()
                if not line:
                    break
                log_message(f"[SERVER_OUTPUT] {line.strip()}")
            except:
                break
    
    stderr_thread = threading.Thread(target=log_server_stderr, daemon=True)
    stderr_thread.start()
    
    log_message("[PROXY] 메시지 중계 시작")
    
    def read_from_server():
        """서버 출력을 읽어서 클라이언트로 전달"""
        while True:
            try:
                line = server.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if line:
                    # 서버 -> 클라이언트 로그
                    try:
                        msg = json.loads(line)
                        log_message(f"\n[S->C] {json.dumps(msg, indent=2)}")
                    except:
                        log_message(f"[S->C] {line}")
                    
                    # 클라이언트로 출력
                    print(line, flush=True)
            except Exception as e:
                log_message(f"[PROXY] 서버 읽기 에러: {e}")
                break
    
    # 서버 읽기를 별도 스레드에서 처리
    server_thread = threading.Thread(target=read_from_server, daemon=True)
    server_thread.start()
    
    try:
        # 클라이언트 입력 처리
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if line:
                # 클라이언트 -> 서버 로그
                try:
                    msg = json.loads(line)
                    log_message(f"\n[C->S] {json.dumps(msg, indent=2)}")
                except:
                    log_message(f"[C->S] {line}")
                
                # 서버로 전달
                server.stdin.write(line + '\n')
                server.stdin.flush()
    
    except Exception as e:
        log_message(f"[PROXY] 에러: {e}")
    finally:
        server.terminate()
        log_message("[PROXY] 종료")

if __name__ == "__main__":
    main()
