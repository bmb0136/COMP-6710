import numpy as np
import pandas as pd
import torch

from datasets import Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MODEL_NAME = "bert-base-uncased"
DATA_PATH = "data.csv"

TEXT_COLUMN = "text"
LABEL_COLUMN = "label"

MAX_LENGTH = 256
BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 2e-5

# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

df = pd.read_csv(DATA_PATH)

# Remove missing values
df = df.dropna(subset=[TEXT_COLUMN, LABEL_COLUMN]).reset_index(drop=True)

# Convert string labels to integer IDs
label_encoder = LabelEncoder()
df["label"] = label_encoder.fit_transform(df[LABEL_COLUMN])

num_labels = len(label_encoder.classes_)

print("Classes:", label_encoder.classes_)
print("Number of classes:", num_labels)

# ---------------------------------------------------------
# Train / validation split
# ---------------------------------------------------------

train_df, val_df = train_test_split(
    df[[TEXT_COLUMN, "label"]],
    test_size=0.2,
    random_state=42,
    stratify=df["label"],
)

train_dataset = Dataset.from_pandas(train_df, preserve_index=False)
val_dataset = Dataset.from_pandas(val_df, preserve_index=False)

# ---------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(batch):
    return tokenizer(
        batch[TEXT_COLUMN],
        truncation=True,
        max_length=MAX_LENGTH,
    )

train_dataset = train_dataset.map(tokenize, batched=True)
val_dataset = val_dataset.map(tokenize, batched=True)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# ---------------------------------------------------------
# Model
# ---------------------------------------------------------

id2label = {
    i: str(label)
    for i, label in enumerate(label_encoder.classes_)
}

label2id = {
    str(label): i
    for i, label in enumerate(label_encoder.classes_)
}

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=num_labels,
    id2label=id2label,
    label2id=label2id,
)

# ---------------------------------------------------------
# Evaluation metrics
# ---------------------------------------------------------

def compute_metrics(eval_pred):
    logits, labels = eval_pred

    predictions = np.argmax(logits, axis=-1)

    accuracy = accuracy_score(labels, predictions)

    precision, recall, f1, _ = precision_recall_fscore_support(
        labels,
        predictions,
        average="weighted",
        zero_division=0,
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }

# ---------------------------------------------------------
# Training configuration
# ---------------------------------------------------------

training_args = TrainingArguments(
    output_dir="./bert_classifier",

    learning_rate=LEARNING_RATE,

    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,

    num_train_epochs=EPOCHS,

    weight_decay=0.01,

    eval_strategy="epoch",
    save_strategy="epoch",

    load_best_model_at_end=True,
    metric_for_best_model="f1",

    logging_steps=50,

    report_to="none",
)

# ---------------------------------------------------------
# Trainer
# ---------------------------------------------------------

trainer = Trainer(
    model=model,
    args=training_args,

    train_dataset=train_dataset,
    eval_dataset=val_dataset,

    processing_class=tokenizer,
    data_collator=data_collator,

    compute_metrics=compute_metrics,
)

# ---------------------------------------------------------
# Fine-tune BERT
# ---------------------------------------------------------

trainer.train()

# ---------------------------------------------------------
# Evaluate
# ---------------------------------------------------------

results = trainer.evaluate()

print("\nEvaluation results:")

for key, value in results.items():
    print(f"{key}: {value}")

# ---------------------------------------------------------
# Save model
# ---------------------------------------------------------

SAVE_PATH = "./bert_text_classifier"

trainer.save_model(SAVE_PATH)
tokenizer.save_pretrained(SAVE_PATH)

print(f"\nModel saved to: {SAVE_PATH}")

# ---------------------------------------------------------
# Prediction function
# ---------------------------------------------------------

def predict(text):
    model.eval()

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LENGTH,
        padding=True,
    )

    # Move input tensors to the same device as the model
    inputs = {
        key: value.to(model.device)
        for key, value in inputs.items()
    }

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.softmax(
        outputs.logits,
        dim=-1,
    )

    predicted_id = torch.argmax(
        probabilities,
        dim=-1,
    ).item()

    predicted_label = label_encoder.inverse_transform(
        [predicted_id]
    )[0]

    confidence = probabilities[0][predicted_id].item()

    return {
        "text": text,
        "label": predicted_label,
        "confidence": confidence,
    }

# ---------------------------------------------------------
# Example prediction
# ---------------------------------------------------------

example = "This movie was absolutely fantastic!"

prediction = predict(example)

print("\nPrediction:")
print(prediction)
