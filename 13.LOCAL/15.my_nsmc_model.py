# NSMC = Naver Sentiment Movie Corpus (네이버 영화 리뷰)

import numpy as np
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer, 
    Trainer, TrainingArguments
)
from datasets import load_dataset

MODEL = "beomi/KcBERT-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL)


ds = load_dataset("nsmc", trust_remote_code=True)

train_ds = ds["train"].filter(lambda x: bool(x["document"])).shuffle(seed=42).select(range(2000))
eval_ds = ds["test"].filter(lambda x: bool(x["document"])).shuffle(seed=42).select(range(500))

print(f"학습 데이터 수: {len(train_ds)}, 평가 데이터 수: {len(eval_ds)}")
print(f"예시: {train_ds[0]['document']}, {eval_ds[0]['document']}")


def tokenize(batch):
    return tokenizer(batch['document'], padding="max_length", truncation=True)

train_ds = train_ds.map(tokenize, batched=True)
eval_ds = eval_ds.map(tokenize, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL, num_labels=2,
    id2label={0: "부정", 1: "긍정"},
    label2id={"부정": 0, "긍정": 1}
)

def compute_matrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": float((preds == labels).mean())}

args = TrainingArguments(
    output_dir="./results_nsmc_kr",
    eval_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    num_train_epochs=1,
    logging_steps=25
)
trainer = Trainer(
    model=model, args=args,
    train_dataset=train_ds, eval_dataset=eval_ds,
    compute_metrics=compute_matrics
)

trainer.train()
print("평가 결과:", trainer.evaluate())

save_path="./my_local_model_nsmc_kr"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print("내 모델 저장 완료: ", save_path)

