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
    "text": ["I love this!", "This is terrible!", "I am happy", "I am sad", "This product is amazing", "Worst experience ever.", "Absolutely fantastic", "I hate it."],
    "label": [1, 0, 1, 0, 1, 0, 1, 0]
}
eval_data = {
    "text": ["I feel greate today!", "The service was awful", "I'm super excited about this!", "Not what I expected"],
    "label": [1, 0, 1, 0]
}

model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)


def tokenize(batch):
    return tokenizer(batch['text'], padding="max_length", truncation=True)

train_ds = Dataset.from_dict(train_data).map(tokenize, batched=True)
eval_ds = Dataset.from_dict(eval_data).map(tokenize, batched=True)

model = AutoModelForSequenceClassification.from_pretrained(
    model_name, num_labels=2,
    id2label={0: "NEGATIVE", 1: "POSITIVE"},
    label2id={"NEGATIVE": 0, "POSITIVE": 1}
)

def compute_matrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": float((preds == labels).mean())}

args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=7,
    logging_steps=1
)
trainer = Trainer(
    model=model, args=args,
    train_dataset=train_ds, eval_dataset=eval_ds,
    compute_metrics=compute_matrics
)

trainer.train()
print("평가 결과:", trainer.evaluate())

save_path="./my_local_model"
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print("내 모델 저장 완료: ", save_path)
