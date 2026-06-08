from transformers import pipeline

# Load the classification pipeline with the specified model
pipe = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis")

# Classify a new sentence
sentence = "I love this product! It's amazing and works perfectly."
result = pipe(sentence)

# Print the result
print(result)

comments = [
    "배송이 정말 빨랐고 제품 품질도 기대 이상입니다.",
    "생각보다 성능이 좋아서 매우 만족스럽습니다.",
    "가격은 조금 비싸지만 그만한 가치가 있다고 생각합니다.",
    "디자인이 예쁘고 사용하기도 편해서 추천합니다.",
    "고객센터 응대가 친절해서 기분 좋게 구매했습니다.",

    "광고와 실제 제품이 너무 달라서 실망했습니다.",
    "사용한 지 하루 만에 고장이 나서 화가 납니다.",
    "배송이 늦고 포장 상태도 좋지 않았습니다.",
    "가격 대비 품질이 떨어져서 다시 구매하지 않을 것 같습니다.",
    "기대가 컸는데 전반적으로 만족스럽지 못했습니다."
]

for comment in comments:
    result = pipe(comment)
    print(comment)
    print(result)
    print("-" * 50)
