# 11. ETC - AI 멀티모달 기능 핵심 요약

> **멀티모달(Multimodal)** = AI가 텍스트뿐 아니라 이미지, 음성 등 여러 형태의 데이터를 다루는 것

---

## 목차

| 번호 | 주제 | 한 줄 요약 |
|------|------|-----------|
| 1 | [Vision (이미지 읽기)](#1-vision--이미지를-보고-설명하기) | AI에게 사진을 보여주고 설명을 들음 |
| 2 | [Image 생성](#2-image-generation--텍스트로-이미지-만들기) | 텍스트 설명으로 이미지를 만들어냄 |
| 3 | [Whisper (STT)](#3-whisper--음성을-텍스트로-변환) | 말소리 → 텍스트로 변환 |
| 4 | [TTS](#4-tts--텍스트를-음성으로-변환) | 텍스트 → 말소리로 변환 |

---

## 1. Vision — 이미지를 보고 설명하기

> 📷 "AI에게 사진을 보여주면 무엇이 있는지 설명해줘!"

### 핵심 개념

AI가 이미지를 **입력**으로 받아서 텍스트로 **설명**해주는 기능이에요.  
마치 시각 장애인을 위한 "눈" 역할을 하는 것과 같아요.

### 이미지를 넘기는 두 가지 방법

```
방법 1) URL 방식  →  인터넷에 있는 이미지 주소를 그냥 전달
방법 2) Base64   →  내 컴퓨터에 있는 파일을 직접 암호화해서 전달
```

### 방법 1: URL로 이미지 전달 (`1.intro.py`)

```python
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        'role': 'user',
        'content': [
            {'type': 'text', 'text': '이 이미지를 한국어로 설명해줘'},
            {'type': 'image_url', 'image_url': {'url': image_url}}  # ← 핵심
        ]
    }]
)
```

> 일반 채팅과 거의 동일한데, `content`에 텍스트 외에 이미지 URL도 같이 넣는 게 전부예요!

### 방법 2: 로컬 파일(Base64) 전달 (`2.more.py`)

```python
# 1단계: 이미지 파일을 Base64 문자열로 변환
def encode_image(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

# 2단계: 변환된 문자열을 data URL 형식으로 전달
{'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{b64}'}}
```

> **Base64란?** 이미지 파일(바이너리)을 텍스트 문자열로 바꾸는 인코딩 방식이에요.  
> 파일을 직접 텍스트로 "포장"해서 보내는 것과 같아요.

### 이미지 종류별 MIME 타입

| 파일 형식 | `data:` URL 앞에 붙이는 값 |
|-----------|--------------------------|
| `.jpg` / `.jpeg` | `data:image/jpeg;base64,` |
| `.png` | `data:image/png;base64,` |
| `.webp` | `data:image/webp;base64,` |

### 활용 예시

```python
questions = [
    '이미지에 있는 한글 글자를 다 읽어줘.',    # OCR
    '해당 이미지에 사용된 주요 색상을 알려줘',  # 색상 분석
    '이 주식 차트를 보고 기술적 분석을 해줘.',  # 차트 분석
]
```

> Vision 기능으로 할 수 있는 것들: OCR(글자 인식), 색상 분석, 차트 분석, 이미지 설명 등

---

## 2. Image Generation — 텍스트로 이미지 만들기

> 🎨 "말로 설명하면 AI가 그림을 그려줘!"

### 핵심 개념

텍스트 프롬프트를 입력하면 AI가 이미지를 **생성**해주는 기능이에요.  
마치 아주 빠른 그래픽 디자이너에게 주문하는 것과 같아요.

### 기본 사용법 (`1.intro.py`)

```python
result = client.images.generate(
    model="gpt-image-1.5",   # 사용할 모델
    prompt="원하는 이미지 설명",
    size='1024x1024',        # 이미지 크기
    quality='high'           # 품질: low / medium / high / auto
)

# 결과를 Base64로 받아서 파일로 저장
b64 = result.data[0].b64_json
with open('output.png', 'wb') as f:
    f.write(base64.b64decode(b64))
```

### 모델 비교

| 모델 | 특징 |
|------|------|
| `dall-e-2` | 구버전, 기본 품질 |
| `gpt-image-1.5` | 투명 배경 지원 ✅, 최대 1536px |
| `gpt-image-2` | 4K(4096px) 지원, 16:9 가능, 더 많은 언어 지원, 투명 배경 ❌ |

### 지원 이미지 크기

```
1024x1024  →  정사각형 (기본)
1024x1536  →  세로 (모바일 느낌)
1536x1024  →  가로 (와이드 느낌)
```

### 좋은 프롬프트 작성 팁

```
❌ 나쁜 예: "돌고래가 날개 달고 갈매기 잡아먹음" (너무 복잡·이상한 묘사)
✅ 좋은 예: "해변 아이콘 팩 4x4, 16개, 64x64, 수채화 스타일"
```

> 프롬프트가 구체적이고 현실적일수록 원하는 결과가 나와요!

---

## 3. Whisper — 음성을 텍스트로 변환

> 🎙️ "말하면 AI가 받아적어줘!" = STT (Speech-To-Text)

### 핵심 개념

오디오 파일을 입력하면 텍스트로 변환해주는 기능이에요.  
회의 녹음, 강의 자막, 음성 메모 정리 등에 사용해요.

### 기본 사용법 (`1.intro.py`)

```python
def transcribe_audio(file):
    with open(file, "rb") as af:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=af,
            response_format="text",  # 반환 형식: text / json / srt 등
            language="ko"            # 언어 힌트 (생략하면 자동 감지)
        )
    return transcript
```

### 파라미터 설명

| 파라미터 | 설명 | 예시 |
|----------|------|------|
| `model` | 사용할 Whisper 모델 | `"whisper-1"` |
| `response_format` | 출력 형식 | `text`, `json`, `srt`, `vtt` |
| `language` | 음성 언어 힌트 | `"ko"`, `"en"`, `"ja"` |

> **`language` 설정 팁**: 언어를 미리 알고 있으면 명시해주세요. 인식 속도와 정확도가 올라가요!

### 지원 파일 형식

```
mp3, mp4, mpeg, mpga, m4a, wav, webm
```

---

## 4. TTS — 텍스트를 음성으로 변환

> 🔊 "글자를 읽어줘!" = TTS (Text-To-Speech)

### 핵심 개념

텍스트를 입력하면 사람처럼 자연스러운 음성으로 변환해주는 기능이에요.  
Whisper와 반대 방향이에요: `텍스트 → 음성`.

### 기본 사용법 (`1.intro.py`)

```python
response = client.audio.speech.create(
    model='tts-1',      # 모델 선택
    voice='alloy',      # 목소리 선택
    input=text          # 변환할 텍스트
)

response.write_to_file('output.mp3')  # mp3 파일로 저장
```

### 모델 비교

| 모델 | 특징 |
|------|------|
| `tts-1` | 빠름, 표준 품질 |
| `tts-1-hd` | 느림, 고품질 (더 자연스러운 음성) |

### 지원 목소리 (voice)

| 목소리 | 느낌 |
|--------|------|
| `alloy` | 중성적, 안정적 |
| `echo` | 남성, 낮은 톤 |
| `fable` | 영국식, 온화함 |
| `onyx` | 깊고 묵직한 남성 |
| `nova` | 여성, 밝고 활기찬 |
| `shimmer` | 여성, 부드럽고 조용한 |

---

## 전체 흐름 한눈에 보기

```
                  ┌─────────────────────────────┐
                  │        OpenAI API           │
                  └──────────────┬──────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    📷 Vision               🎨 Image              🔊 Audio
    (이미지 읽기)            (이미지 생성)          (음성 처리)
          │                      │              ┌───────┴───────┐
   이미지 → 텍스트          텍스트 → 이미지   🎙️ STT        📢 TTS
                                            (음성→텍스트)  (텍스트→음성)
                                              Whisper
```

---

## 공통 설정 (모든 예제에서 동일)

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()       # .env 파일에서 API 키 불러오기
client = OpenAI()   # 이후 client.XXX 형태로 사용
```

> `.env` 파일에 `OPENAI_API_KEY=sk-...` 형태로 키를 저장해두면 코드에 직접 노출되지 않아요!

---

## 요약 비교표

| 기능 | 입력 | 출력 | API 경로 | 주요 모델 |
|------|------|------|----------|-----------|
| Vision | 이미지 + 텍스트 | 텍스트 | `chat.completions` | `gpt-4o-mini` |
| Image Gen | 텍스트(프롬프트) | 이미지 파일 | `images.generate` | `gpt-image-1.5` |
| Whisper(STT) | 오디오 파일 | 텍스트 | `audio.transcriptions` | `whisper-1` |
| TTS | 텍스트 | 오디오 파일 | `audio.speech` | `tts-1` |
