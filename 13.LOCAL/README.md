# 13. 로컬 AI 모델 실습

> **인터넷 없이 내 컴퓨터에서 AI 모델을 직접 실행하는 방법**을 배우는 챕터입니다.  
> 크게 **Ollama** (대화형 LLM) 와 **HuggingFace** (텍스트/이미지 분석) 두 가지 도구를 사용합니다.

---

## 전체 구성 한눈에 보기

```
로컬 AI 실습
├── Ollama (로컬 LLM 대화)     파일 1~5
├── HuggingFace 기초            파일 6
├── 감성 분석 (영어/다국어)     파일 7~9
├── 제로샷 분류 (BART)          파일 10
├── 직접 학습 - 영어            파일 11~12
├── 직접 학습 - 한국어          파일 13~14
├── NSMC 대용량 학습            파일 15
├── 텍스트 생성 (GPT-2)         파일 16
└── 이미지 생성 (FLUX)          파일 17~18
```

---

## 1. Ollama — 내 컴퓨터에서 ChatGPT처럼 쓰기

> **비유**: Ollama는 AI 모델을 내 컴퓨터에 설치해주는 "앱스토어" 같은 도구입니다.

### 설치 및 기본 사용 (`1.intro.py`)

```python
import ollama

ollama.pull("mistral")          # 모델 다운로드 (처음 한 번만)
response = ollama.chat(model="mistral", messages=[
    {"role": "user", "content": "인공지능에 대해서 설명해줘"}
])
print(response["message"]["content"])
```

| 설치 명령 | `pip install ollama` |
|-----------|----------------------|
| 사용 모델 | `mistral`, `exaone3.5` 등 |

---

### LangChain + Ollama 연결 (`2.langchain.py`)

> **비유**: LangChain은 AI 모델들을 연결하는 "어댑터" 입니다. Ollama든 OpenAI든 같은 방식으로 쓸 수 있게 해줍니다.

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="mistral")
resp = llm.invoke("안녕? 한마디로 너를 소개해줘")
print(resp.content)
```

---

### 프롬프트 템플릿 사용 (`3.langchain2.py`)

> 변수가 있는 질문 틀을 만들어두고 재사용할 수 있습니다.

```python
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    "다음 주제로 블로그 개요를 5가지 만들어줘.\n\n주제: {topic}"
)

chain = prompt | llm | StrOutputParser()
print(chain.invoke({"topic": "로컬 LLM 모델 활용"}))
```

**핵심 패턴**: `프롬프트 | 모델 | 출력파서` — 파이프(|)로 순서대로 연결

---

### 스트리밍 출력 (`4.langchain3_stream.py`)

> 답변이 다 완성될 때까지 기다리지 않고, 글자가 나오는 대로 바로 출력합니다. (ChatGPT처럼)

```python
for chunk in chain.stream({"topic": "로컬 LLM 모델 활용"}):
    print(chunk, end="", flush=True)   # 한 글자씩 바로 출력
```

---

### 외부 Ollama 서버 연결 (`5.external.py`)

> 고성능 서버에 Ollama를 설치하고, 내 노트북에서 원격으로 사용할 수 있습니다.

```python
import requests

OLLAMA_HOST = "http://192.168.0.153:11434"   # 서버 IP
response = requests.post(f"{OLLAMA_HOST}/api/generate", json={
    "model": "exaone3.5",
    "prompt": "파이썬 헬로우 월드 코드를 보여줘.",
    "stream": False
})
```

---

## 2. HuggingFace — 다양한 AI 모델 사용하기

> **비유**: HuggingFace는 전 세계 개발자들이 만든 AI 모델을 무료로 올려두는 "GitHub" 같은 곳입니다.

### 캐시 위치 확인 (`6.huggingface.py`)

```python
from huggingface_hub.constants import HUGGINGFACE_HUB_CACHE
print("HF 캐시 디렉토리:", HUGGINGFACE_HUB_CACHE)
```

> 다운로드한 모델이 저장되는 폴더 위치를 알 수 있습니다.

---

## 3. 감성 분석 — 글의 긍정/부정 판별

### 영어 감성 분석 (`7.hf_sentiment.py`)

```python
from transformers import pipeline

# 모델 이름 규칙: {아키텍처}-{크기}-{전처리}-{학습방식}-{데이터셋}-{언어}
analyzer = pipeline("sentiment-analysis", 
                    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")

result = analyzer("I'm happy")
# 출력: [{'label': 'POSITIVE', 'score': 0.9998}]
```

---

### 다국어 감성 분석 (`8.hf_sentiment2_multilang.py`)

```python
pipe = pipeline("text-classification", 
                model="tabularisai/multilingual-sentiment-analysis")

# 한국어도 분석 가능
result = pipe("배송이 정말 빨랐고 제품 품질도 기대 이상입니다.")
```

---

### BERT로 직접 감성 분석 (`9.hf_sentiment3_multi.py`)

> `pipeline`을 쓰지 않고 **모델과 토크나이저를 직접 다루는 방식**입니다. 더 세밀한 제어가 가능합니다.

```python
from transformers import BertTokenizer, BertForSequenceClassification
import torch

model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

text = "이 영화 정말 재미있었어요!"
inputs = tokenizer(text, return_tensors="pt")   # 텍스트 → 숫자 변환

with torch.no_grad():           # 학습하지 않음 (추론만)
    outputs = model(**inputs)
    predicted_class = outputs.logits.argmax().item()

# 이 모델은 1~5점 (0~4 클래스)
print(f"예측 감정 점수: {predicted_class + 1}")
```

**처리 흐름**: `텍스트` → `토크나이저(숫자 변환)` → `모델` → `logits(점수)` → `argmax(최고값 선택)`

---

## 4. 제로샷 분류 — 학습 없이 카테고리 분류 (`10.hf_bart.py`)

> **비유**: "이 문장이 기술/스포츠/요리 중 어디에 속해?" 처럼, 미리 학습하지 않아도 즉석에서 분류할 수 있습니다.

```python
classifier = pipeline("zero-shot-classification", 
                      model="facebook/bart-large-mnli")

text = "I just upgraded my computer's graphics card"
labels = ["technology", "sports", "cooking", "politics"]

result = classifier(text, candidate_labels=labels)
print(f"최종 분류: {result['labels'][0]}")   # technology
```

> 내부 원리: MNLI(자연어 추론) — 문장과 라벨 사이의 **함의/모순/중립** 관계를 판단합니다.

---

## 5. 나만의 모델 만들기 (파인튜닝, Fine-tuning)

> **비유**: 기존 AI를 내 데이터로 **추가 교육**시키는 것입니다. 영어 선생님(기존 모델)에게 내 회사 용어를 가르치는 것과 같습니다.

### 영어 감성 분류 모델 학습 (`11.my_train.py`)

```
[학습 단계]
1. 내 데이터 준비 (텍스트 + 라벨)
2. 토크나이저로 텍스트를 숫자로 변환
3. 기존 모델 불러오기 (distilbert-base-uncased)
4. Trainer로 학습
5. 내 컴퓨터에 모델 저장
```

```python
# 내 데이터 (1=긍정, 0=부정)
train_data = {
    "text": ["I love this!", "This is terrible!", ...],
    "label": [1, 0, ...]
}

# Trainer가 자동으로 학습 처리
trainer = Trainer(model=model, args=args, 
                  train_dataset=train_ds, eval_dataset=eval_ds)
trainer.train()

model.save_pretrained("./my_local_model")    # 저장
```

### 학습한 모델로 예측 (`12.my_predict.py`)

```python
classifier = pipeline("sentiment-analysis", 
                      model="./my_local_model",     # 내 모델 경로
                      tokenizer="./my_local_model")

result = classifier("I love using my own AI model!")
# {'label': 'POSITIVE', 'score': 0.998}
```

---

### 한국어 감성 분류 모델 학습 (`13.my_kr_train.py`)

> 영어 모델 대신 **KcBERT** (한국어 BERT) 를 사용합니다.

```python
model_name = "beomi/kcbert-base"    # 한국어 특화 모델
```

- 학습 에포크: 20회 (영어 7회보다 더 많이 학습)
- 저장 경로: `./my_local_model_kr`

### 한국어 모델로 예측 (`14.my_predict_kr.py`)

```python
classifier = pipeline("sentiment-analysis", model="./my_local_model_kr", ...)

# 애매한 문장도 테스트
classifier("배송은 느렸지만 제품은 마음에 듭니다.")
```

---

### NSMC 대용량 한국어 학습 (`15.my_nsmc_model.py`)

> **NSMC** = 네이버 영화 리뷰 15만 건 데이터셋  
> 직접 데이터를 만들지 않고 **공개 데이터셋**으로 더 강력하게 학습합니다.

```python
from datasets import load_dataset

ds = load_dataset("nsmc")          # 자동으로 데이터 다운로드
train_ds = ds["train"].select(range(2000))   # 2000개만 사용
eval_ds  = ds["test"].select(range(500))     # 500개로 평가
```

| 항목 | 직접 학습 (13번) | NSMC 학습 (15번) |
|------|----------------|-----------------|
| 데이터 수 | 8개 | 2,000개 |
| 배치 크기 | 2 | 16 |
| 에포크 | 20 | 1 |

---

## 6. 텍스트 생성 — GPT-2 (`16.hf_gpt2.py`)

> 문장의 시작 부분을 주면 AI가 이어서 글을 완성합니다.

```python
text_generator = pipeline("text-generation", model="gpt2")

result = text_generator(
    "Once upon a time, ",
    max_length=50,           # 최대 50 토큰
    truncation=True
)
print(result[0]["generated_text"])
```

---

## 7. 이미지 생성

### HuggingFace API 사용 (`17.hf_image.py`)

> 내 컴퓨터가 아닌 **HuggingFace 서버**에서 이미지를 만들고 결과만 받아옵니다. (API 토큰 필요)

```python
from huggingface_hub import InferenceClient

client = InferenceClient(
    model="black-forest-labs/FLUX.1-dev",
    token=os.getenv('HUGGINGFACEHUB_API_TOKEN')   # .env 파일에서 읽기
)

image = client.text_to_image(
    "A dolphin reading a book under a cherry blossom tree",
    guidance_scale=7.5
)
image.save("output.png")
```

---

### 로컬에서 직접 이미지 생성 (`18.hf_image2.py`)

> 모델을 내 컴퓨터에 다운로드해서 **오프라인으로** 이미지를 생성합니다. (용량 큰 GPU 필요)

```python
from diffusers import FluxPipeline

pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell")
pipe = pipe.to("cpu")   # GPU 없으면 CPU 사용 (느림)

image = pipe(
    "ultra realistic photo of a korean girl, cinematic lighting",
    num_inference_steps=4   # 생성 단계 수 (적을수록 빠르지만 품질↓)
).images[0]

image.save("flux_output.png")
```

---

## 핵심 개념 정리

| 용어 | 쉬운 설명 |
|------|-----------|
| **Ollama** | AI 모델을 내 컴퓨터에 설치·실행하는 도구 |
| **HuggingFace** | AI 모델을 공유하는 플랫폼 (GitHub와 유사) |
| **pipeline** | 모델을 쉽게 쓸 수 있게 감싸주는 포장지 |
| **토크나이저** | 텍스트 → 숫자로 변환하는 번역기 |
| **파인튜닝** | 기존 모델을 내 데이터로 추가 학습 |
| **에포크(epoch)** | 전체 학습 데이터를 몇 번 반복 학습할지 |
| **제로샷** | 별도 학습 없이 즉석에서 분류하는 방식 |
| **logits** | 모델이 출력한 날것의 점수 (argmax로 최종 결정) |
| **스트리밍** | 완성 전에 글자가 나오는 대로 바로 출력 |

---

## 필요한 라이브러리 설치

```bash
# Ollama 연동
pip install ollama langchain-ollama

# HuggingFace 기본
pip install transformers torch datasets huggingface_hub

# 이미지 생성
pip install Pillow diffusers accelerate

# 기타
pip install python-dotenv
```

---

## 학습 흐름 추천 순서

```
1.intro.py          기본 Ollama 대화
     ↓
2~4.langchain.py    LangChain으로 체인 구성 + 스트리밍
     ↓
7.hf_sentiment.py   HuggingFace pipeline 감성분석
     ↓
9.hf_sentiment3.py  모델/토크나이저 직접 다루기
     ↓
11.my_train.py      내 데이터로 직접 파인튜닝
     ↓
13.my_kr_train.py   한국어 모델 파인튜닝
     ↓
17.hf_image.py      이미지 생성 API
```
