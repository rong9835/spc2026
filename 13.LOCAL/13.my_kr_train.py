# 나만의 데이터로 모델 추가 학습하기 (fine-tuning)
# pip install transformers torch datasets

import numpy as np
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer, 
    Trainer, TrainingArguments
)
from datasets import Dataset

# 학습 데이터 추가 (1=긍정, 0=부정)
train_data = {
    "text": [
        "정말 만족스러운 제품입니다. 다음에도 구매할 생각입니다.",
        "기대한 것보다 품질이 너무 떨어져서 실망했습니다.",
        "배송도 빠르고 상품 상태도 좋아서 만족합니다.",
        "사용한 지 하루 만에 고장 나서 화가 납니다.",
        "가격 대비 성능이 뛰어나서 추천하고 싶습니다.",
        "고객센터 응대가 불친절해서 기분이 나빴습니다.",
        "디자인이 예쁘고 사용하기도 편리합니다.",
        "광고와 실제 제품이 너무 달라서 실망했습니다."
    ],
    "label": [1, 0, 1, 0, 1, 0, 1, 0]
}

eval_data = {
    "text": [
        "생각보다 훨씬 좋아서 만족스럽게 사용하고 있습니다.",
        "돈이 아까울 정도로 품질이 좋지 않습니다.",
        "친구들에게도 추천하고 싶을 만큼 마음에 듭니다.",
        "다시는 구매하고 싶지 않을 정도로 별로였습니다."
    ],
    "label": [1, 0, 1, 0]
}

model_name = "beomi/kcbert-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)


def tokenize(batch):
    return tokenizer(batch['text'], padding="max_length", truncation=True)

train_ds = Dataset.from_dict(train_data).map(tokenize, batched=True)
eval_ds = Dataset.from_dict(eval_data).map(tokenize, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    model_name, num_labels=2,
    id2label={0: "부정", 1: "긍정"},
    label2id={"부정": 0, "긍정": 1}
)

def compute_matrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": float((preds == labels).mean())}

args = TrainingArguments(
    output_dir="./results_kr",
    eval_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=20,
    logging_steps=1
)
trainer = Trainer(
    model=model, args=args,
    train_dataset=train_ds, eval_dataset=eval_ds,
    compute_metrics=compute_matrics
)

trainer.train()
print("평가 결과:", trainer.evaluate())

save_path="./my_local_model_kr"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print("내 모델 저장 완료: ", save_path)
