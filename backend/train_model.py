"""
FreshSense ─ train_model.py
CNN Training with Transfer Learning (MobileNetV2)

Usage:
  cd backend
  python train_model.py

Output:
  model/fruit_model.h5         ← trained model (load with Keras)
  model/training_plot.png      ← accuracy/loss curves
  model/confusion_matrix.png   ← per-class confusion matrix
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = r"C:\Users\yashw\OneDrive\Desktop\Major-Project\Claude 1\dataset\fruits\train"
MODEL_DIR  = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "fruit_model.h5")
PLOT_PATH  = os.path.join(MODEL_DIR, "training_plot.png")
CM_PATH    = os.path.join(MODEL_DIR, "confusion_matrix.png")

DATASET_DIR = os.path.join(BASE_DIR, "..", "dataset", "fruits", "dataset", "dataset", "train")
IMG_SIZE      = (224, 224)
BATCH_SIZE    = 32
EPOCHS        = 20
LR            = 1e-4
VAL_SPLIT     = 0.2
SEED          = 42

import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

print(f"\n🌿  FreshSense Trainer")
print(f"    TF: {tf.__version__}  |  GPU: {bool(tf.config.list_physical_devices('GPU'))}\n")

# ── 1. Dataset ────────────────────────────────────────────────────────────────
if not os.path.isdir(DATASET_DIR):
    print(f"❌  Dataset not found at {DATASET_DIR}")
    print("    See dataset/README.md for download instructions.\n")
    sys.exit(1)

aug = tf.keras.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.2),
    layers.RandomZoom(0.15),
    layers.RandomBrightness(0.1),
    layers.RandomContrast(0.1),
])

norm = layers.Rescaling(1./255)

train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR, validation_split=VAL_SPLIT, subset="training",
    seed=SEED, image_size=IMG_SIZE, batch_size=BATCH_SIZE, label_mode="categorical")

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR, validation_split=VAL_SPLIT, subset="validation",
    seed=SEED, image_size=IMG_SIZE, batch_size=BATCH_SIZE, label_mode="categorical")

CLASS_NAMES = train_ds.class_names
NUM_CLASSES = len(CLASS_NAMES)
print(f"    Classes ({NUM_CLASSES}): {CLASS_NAMES}\n")

train_ds = (train_ds
    .map(lambda x,y: (norm(x),y), num_parallel_calls=tf.data.AUTOTUNE)
    .map(lambda x,y: (aug(x, training=True),y), num_parallel_calls=tf.data.AUTOTUNE)
    .prefetch(tf.data.AUTOTUNE))

val_ds = (val_ds
    .map(lambda x,y: (norm(x),y), num_parallel_calls=tf.data.AUTOTUNE)
    .prefetch(tf.data.AUTOTUNE))

# ── 2. Model ──────────────────────────────────────────────────────────────────
base = MobileNetV2(input_shape=(*IMG_SIZE,3), include_top=False, weights="imagenet")
base.trainable = False

inputs  = tf.keras.Input(shape=(*IMG_SIZE,3))
x       = base(inputs, training=False)
x       = layers.GlobalAveragePooling2D()(x)
x       = layers.BatchNormalization()(x)
x       = layers.Dense(256, activation="relu")(x)
x       = layers.Dropout(0.4)(x)
x       = layers.Dense(128, activation="relu")(x)
x       = layers.Dropout(0.25)(x)
outputs = layers.Dense(NUM_CLASSES, activation="softmax")(x)
model   = Model(inputs, outputs, name="FreshSense_MobileNetV2")
model.summary()

cbs = [
    EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=3, min_lr=1e-7, verbose=1),
    ModelCheckpoint(MODEL_PATH, monitor="val_accuracy", save_best_only=True, verbose=1),
]

# ── Phase 1: head only ────────────────────────────────────────────────────────
print("\n── Phase 1: Training head only ──")
model.compile(Adam(LR), loss="categorical_crossentropy", metrics=["accuracy"])
h1 = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS//2, callbacks=cbs, verbose=1)

# ── Phase 2: fine-tune top 30 base layers ────────────────────────────────────
print("\n── Phase 2: Fine-tuning top 30 layers ──")
base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False
model.compile(Adam(LR/10), loss="categorical_crossentropy", metrics=["accuracy"])
h2 = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS,
               initial_epoch=EPOCHS//2, callbacks=cbs, verbose=1)

# ── Merge histories ───────────────────────────────────────────────────────────
hist = {k: h1.history.get(k,[]) + h2.history.get(k,[])
        for k in set(list(h1.history)+list(h2.history))}

# ── 3. Evaluation ─────────────────────────────────────────────────────────────
val_loss, val_acc = model.evaluate(val_ds, verbose=0)
print(f"\n✅  Val Accuracy : {val_acc*100:.2f}%")
print(f"   Val Loss     : {val_loss:.4f}")

# ── 4. Training plot ──────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14,5))
fig.patch.set_facecolor("#1a3a2a")
for ax in axes:
    ax.set_facecolor("#0f2d1c")
    for spine in ax.spines.values(): spine.set_edgecolor("#2d6a4f")
    ax.tick_params(colors="white"); ax.xaxis.label.set_color("white"); ax.yaxis.label.set_color("white"); ax.title.set_color("white")

axes[0].plot(hist["accuracy"],     "#52b788", lw=2, label="Train")
axes[0].plot(hist["val_accuracy"], "#e9a800", lw=2, ls="--", label="Val")
axes[0].set_title("Accuracy"); axes[0].legend(facecolor="#1a3a2a", labelcolor="white"); axes[0].grid(alpha=.2, color="#52b788")

axes[1].plot(hist["loss"],     "#52b788", lw=2, label="Train")
axes[1].plot(hist["val_loss"], "#e9a800", lw=2, ls="--", label="Val")
axes[1].set_title("Loss"); axes[1].legend(facecolor="#1a3a2a", labelcolor="white"); axes[1].grid(alpha=.2, color="#52b788")

fig.suptitle("FreshSense — Training Curves", color="white", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(PLOT_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close()
print(f"   Plot saved → {PLOT_PATH}")

# ── 5. Confusion matrix ───────────────────────────────────────────────────────
try:
    from sklearn.metrics import confusion_matrix, classification_report
    import seaborn as sns

    y_true, y_pred = [], []
    for imgs, lbls in val_ds:
        y_pred.extend(np.argmax(model.predict(imgs, verbose=0), axis=1))
        y_true.extend(np.argmax(lbls.numpy(), axis=1))

    cm  = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(max(8, NUM_CLASSES), max(6, NUM_CLASSES-2)))
    fig.patch.set_facecolor("#1a3a2a"); ax.set_facecolor("#0f2d1c")
    sns.heatmap(cm, annot=True, fmt="d", cmap="Greens",
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES, ax=ax,
                linewidths=.5, linecolor="#1a3a2a")
    ax.set_title("Confusion Matrix", color="white", fontsize=13, fontweight="bold")
    ax.set_xlabel("Predicted", color="white"); ax.set_ylabel("Actual", color="white")
    ax.tick_params(colors="white")
    plt.tight_layout()
    plt.savefig(CM_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"   Confusion matrix → {CM_PATH}")
    print("\n── Classification Report ─────────────────────────")
    print(classification_report(y_true, y_pred, target_names=CLASS_NAMES))
except ImportError:
    print("   (sklearn/seaborn not installed — skipping confusion matrix)")

print(f"\n🎉  Done!  Model saved → {MODEL_PATH}\n")
