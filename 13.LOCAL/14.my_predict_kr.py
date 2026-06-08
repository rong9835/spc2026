import os
from transformers import pipeline

MODEL_DIR = "./my_local_model_kr"

classifier = pipeline("sentiment-analysis", model=MODEL_DIR, tokenizer=MODEL_DIR)

test_sentences = [
    "정말 만족스럽습니다. 다음에도 구매하고 싶어요.",
    "지금까지 사용한 제품 중 최악이었습니다.",
    "가격 대비 성능이 뛰어나서 매우 만족합니다.",
    "생각보다 품질이 좋지 않아 실망했습니다.",

    # 애매한 문장도 테스트
    "배송은 느렸지만 제품은 마음에 듭니다.",
    "나쁘지는 않지만 기대했던 수준은 아닙니다.",
    "가격이 조금 비싸지만 품질은 좋은 편입니다.",
    "그럭저럭 사용할 만하지만 추천할 정도는 아닙니다."
]

for sentence in test_sentences:
    result = classifier(sentence)
    print(f"문장: {sentence}")
    print(result)
    print("-" * 50)
