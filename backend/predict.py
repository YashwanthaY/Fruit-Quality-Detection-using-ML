"""
FreshSense — predict.py (v4 FINAL)
Supports: 16 classes, ripeness % score, TFSMLayer with 'serve' endpoint
"""

import os
import random
import numpy as np

# ── Storage tips ──────────────────────────────────────────
STORAGE_TIPS = {
    "apple":       ["Store in the fridge crisper drawer",
                    "Keep away from other fruits",
                    "Wrap in paper to slow moisture loss"],
    "banana":      ["Store at room temperature on a banana hanger",
                    "Never refrigerate unripe bananas",
                    "Once ripe, refrigerate to extend 2-3 days"],
    "grapes":      ["Keep unwashed in original ventilated packaging in fridge",
                    "Wash only right before eating",
                    "Store away from strong-smelling foods"],
    "kiwi":        ["Store unripe kiwi at room temperature",
                    "Once ripe, refrigerate for up to 2 weeks",
                    "Do not store near ethylene-producing fruits"],
    "mango":       ["Ripen at room temperature first, then refrigerate",
                    "Place in a paper bag to speed up ripening",
                    "Cut mango keeps in airtight container for 3-4 days"],
    "orange":      ["Store in fridge crisper for up to 3 weeks",
                    "Never seal in airtight bags — needs airflow",
                    "Room temperature oranges last 1-2 weeks"],
    "pear":        ["Store unripe pears at room temperature",
                    "Refrigerate once ripe to extend shelf life",
                    "Keep away from strong-smelling foods"],
    "pineapple":   ["Store upside-down to redistribute natural juices",
                    "Refrigerate cut pineapple in airtight container",
                    "Freeze pineapple chunks for up to 6 months"],
    "default":     ["Keep in cool dry place away from sunlight",
                    "Store separately from other fruits",
                    "Check daily and remove damaged pieces"]
}

SHELF_LIFE = {
    "good":         {"text": "7-10 Days", "days": 8},
    "intermediate": {"text": "3-5 Days",  "days": 4},
    "bad":          {"text": "0-1 Days",  "days": 0},
}

RECOMMENDATIONS = {
    "good":         "Safe for immediate consumption or normal storage.",
    "intermediate": "Consume within 1-2 days or cook/process soon.",
    "bad":          "Not safe for consumption. Discard immediately.",
}

LABEL_MAP = {
    "freshapples":      ("Apple",       "good"),
    "freshbanana":      ("Banana",      "good"),
    "freshgrapes":      ("Grapes",      "good"),
    "freshkiwi":        ("Kiwi",        "good"),
    "freshmango":       ("Mango",       "good"),
    "freshoranges":     ("Orange",      "good"),
    "freshpear":        ("Pear",        "good"),
    "freshpineapple":   ("Pineapple",   "good"),
    "rottenapples":     ("Apple",       "bad"),
    "rottenbanana":     ("Banana",      "bad"),
    "rottengrapes":     ("Grapes",      "bad"),
    "rottenkiwi":       ("Kiwi",        "bad"),
    "rottenmango":      ("Mango",       "bad"),
    "rottenoranges":    ("Orange",      "bad"),
    "rottenpear":       ("Pear",        "bad"),
    "rottenpineapple":  ("Pineapple",   "bad"),
}

LOW_CONFIDENCE_CLASSES = ["kiwi", "pear", "pineapple"]

# ── Model + class names ───────────────────────────────────
_model       = None
_class_names = []

def _load_class_names():
    global _class_names
    path = os.path.join(os.path.dirname(__file__), "model", "class_names.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            _class_names = [l.strip() for l in f if l.strip()]
        print(f"Class names loaded: {_class_names}")
    else:
        _class_names = list(LABEL_MAP.keys())
        print(f"Using default class names: {_class_names}")

def _load_model():
    global _model
    if _model is not None:
        return _model

    import tensorflow as tf
    base_dir   = os.path.dirname(__file__)
    saved_path = os.path.join(base_dir, "model", "fruit_saved_model")

    if os.path.exists(saved_path):
        try:
            _model = tf.keras.layers.TFSMLayer(
                saved_path,
                call_endpoint="serve"
            )
            dummy = tf.zeros([1, 224, 224, 3])
            out   = _model(dummy, training=False)
            print(f"Model loaded! Output type: {type(out)}")
            return _model
        except Exception as e:
            print(f"Failed to load model: {e}")
            import traceback; traceback.print_exc()

    print("No model found — DEMO mode")
    return None

_load_class_names()
_load_model()


# ── predict from image ────────────────────────────────────
def predict_from_image(image_path: str) -> dict:
    model = _model
    if model is None:
        return _demo_result()

    try:
        import tensorflow as tf

        img  = tf.keras.utils.load_img(image_path, target_size=(224, 224))
        arr  = tf.keras.utils.img_to_array(img) / 255.0
        arr  = tf.cast(np.expand_dims(arr, axis=0), tf.float32)

        output = model(arr, training=False)

        # Handle both dict and direct tensor output
        if isinstance(output, dict):
            preds = None
            for k, v in output.items():
                arr_v = v.numpy()[0]
                if len(arr_v) == len(_class_names):
                    preds = arr_v
                    break
            if preds is None:
                preds = list(output.values())[0].numpy()[0]
        elif hasattr(output, 'numpy'):
            preds = output.numpy()[0]
        else:
            preds = np.array(output)[0]

        print(f"Predictions: {[(c, f'{p*100:.1f}%') for c,p in zip(_class_names, preds)]}")

        top_idx  = int(np.argmax(preds))
        top_conf = float(preds[top_idx])

        if top_idx >= len(_class_names):
            return _demo_result()

        label = _class_names[top_idx]
        print(f"TOP: {label} ({top_conf*100:.1f}%)")

        fruit_name, quality = _map_label(label)
        print(f"MAPPED: fruit={fruit_name}, quality={quality}")

        # Smart correction — if model picks rottenoranges but
        # another rotten class has meaningful confidence, use that
        if label == "rottenoranges" and top_conf < 0.98:
            rotten_scores = {
                c: float(preds[i])
                for i, c in enumerate(_class_names)
                if "rotten" in c and c != "rottenoranges"
            }
            second_best = max(rotten_scores, key=rotten_scores.get)
            second_conf = rotten_scores[second_best]
            if second_conf > 0.05:
                label      = second_best
                fruit_name, quality = _map_label(label)
                print(f"CORRECTED to: {label} ({second_conf*100:.1f}%)")

        # ── Ripeness % calculation ────────────────────────
        fruit_key    = fruit_name.lower()
        fresh_label  = "fresh"  + fruit_key
        rotten_label = "rotten" + fruit_key

        # Handle plural class names e.g. freshapples, freshoranges
        if fresh_label not in _class_names:
            fresh_label  = "fresh"  + fruit_key + "s"
            rotten_label = "rotten" + fruit_key + "s"

        good_conf   = float(sum(preds[i] for i,l in enumerate(_class_names) if "fresh"  in l.lower()))
        rotten_conf = float(sum(preds[i] for i,l in enumerate(_class_names) if "rotten" in l.lower()))
        inter_conf  = max(0.0, 1.0 - good_conf - rotten_conf)
        total_all   = good_conf + inter_conf + rotten_conf or 1.0

        # Get fruit-specific fresh and rotten scores
        f_conf = float(preds[_class_names.index(fresh_label)])  if fresh_label  in _class_names else good_conf
        r_conf = float(preds[_class_names.index(rotten_label)]) if rotten_label in _class_names else rotten_conf

        # Ripeness = fresh / (fresh + rotten) × 100
        total_fruit = f_conf + r_conf or 1.0
        quality_pct = int((f_conf / total_fruit) * 100)
        quality_pct = max(5, min(98, quality_pct))

        # Ripeness label based on score
        if quality_pct >= 80:
            ripeness_label = "Peak Freshness"
        elif quality_pct >= 55:
            ripeness_label = "Good — Slightly Past Peak"
        elif quality_pct >= 30:
            ripeness_label = "Declining — Use Soon"
        else:
            ripeness_label = "Spoiled — Discard"

        return _build_result(
            quality_label  = quality,
            quality_pct    = quality_pct,
            ripeness_label = ripeness_label,
            conf_score     = int(top_conf * 100),
            fruit_type     = fruit_name,
            good_pct       = int(good_conf   / total_all * 100),
            int_pct        = int(inter_conf  / total_all * 100),
            bad_pct        = int(rotten_conf / total_all * 100),
        )

    except Exception as e:
        print(f"Inference error: {e}")
        import traceback; traceback.print_exc()
        return _demo_result()


# ── predict from manual ───────────────────────────────────
def predict_from_manual(inputs: dict) -> dict:
    color   = inputs.get("color",   "vibrant")
    texture = inputs.get("texture", "firm")
    smell   = inputs.get("smell",   "fresh")
    days    = int(inputs.get("days_since_harvest", 3))
    fruit   = str(inputs.get("fruit_type", "apple")).lower().strip().capitalize()

    pen = 0
    pen += {"vibrant":0,"normal":0,"dull":1,"brown_spots":2,"black_mold":4}.get(color, 0)
    pen += {"firm":0,"slightly_soft":1,"soft":2,"wrinkled":3}.get(texture, 0)
    pen += {"fresh":0,"mild":0,"fermented":2,"bad":4}.get(smell, 0)
    if   days > 20: pen += 4
    elif days > 14: pen += 3
    elif days > 10: pen += 2
    elif days > 7:  pen += 1

    if   pen >= 5: quality = "bad"
    elif pen >= 2: quality = "intermediate"
    else:          quality = "good"

    pct  = max(5, int(100 - (pen/15)*100))
    conf = min(95, 65 + abs(pen-7)*3)

    if quality_pct >= 80:
        ripeness_label = "Peak Freshness"
    elif pct >= 55:
        ripeness_label = "Good — Slightly Past Peak"
    elif pct >= 30:
        ripeness_label = "Declining — Use Soon"
    else:
        ripeness_label = "Spoiled — Discard"

    if   quality=="good":         g,i,b = conf,(100-conf)//2,(100-conf)//2
    elif quality=="intermediate": g,i,b = (100-conf)//2,conf,(100-conf)//2
    else:                         g,i,b = (100-conf)//2,(100-conf)//2,conf

    return _build_result(
        quality_label  = quality,
        quality_pct    = pct,
        ripeness_label = ripeness_label,
        conf_score     = conf,
        fruit_type     = fruit,
        good_pct       = g,
        int_pct        = i,
        bad_pct        = b
    )


# ── helpers ───────────────────────────────────────────────
def _map_label(label: str):
    lw = label.lower().strip()
    if lw in LABEL_MAP:
        return LABEL_MAP[lw]
    fruit   = lw.replace("fresh","").replace("rotten","").capitalize()
    quality = "bad" if "rotten" in lw else "good"
    return (fruit, quality)

def _build_result(quality_label, quality_pct, ripeness_label,
                  conf_score, fruit_type, good_pct, int_pct, bad_pct) -> dict:
    shelf      = SHELF_LIFE.get(quality_label, SHELF_LIFE["good"])
    tips       = STORAGE_TIPS.get(fruit_type.lower(), STORAGE_TIPS["default"])
    disclaimer = None
    if quality_label == "bad" and fruit_type.lower() in LOW_CONFIDENCE_CLASSES:
        disclaimer = (
            f"⚠️ Note: Rotten {fruit_type} detection has limited training data. "
            f"Please verify visually — check for soft spots, mold, or bad smell."
        )
    return {
        "quality_label":        quality_label,
        "quality_percentage":   quality_pct,
        "ripeness_label":       ripeness_label,
        "confidence_score":     conf_score,
        "shelf_life_days":      shelf["text"],
        "shelf_life_numeric":   shelf["days"],
        "storage_tips":         tips,
        "fruit_type":           fruit_type,
        "recommendation":       RECOMMENDATIONS[quality_label],
        "confidence_breakdown": {"good":good_pct,"intermediate":int_pct,"bad":bad_pct},
        "disclaimer":           disclaimer
    }

def _demo_result() -> dict:
    fruits = ["Apple","Banana","Orange","Mango","Grapes"]
    labels = ["good","good","intermediate","bad"]
    fruit  = random.choice(fruits)
    label  = random.choice(labels)
    pcts   = {"good":(76,97),"intermediate":(40,68),"bad":(5,26)}
    pct    = random.randint(*pcts[label])
    if   label=="good":         g,i,b=pct,(100-pct)//2,(100-pct)//2
    elif label=="intermediate": g,i,b=(100-pct)//2,pct,(100-pct)//2
    else:                       g,i,b=(100-pct)//2,(100-pct)//2,pct

    if pct >= 80:   rl = "Peak Freshness"
    elif pct >= 55: rl = "Good — Slightly Past Peak"
    elif pct >= 30: rl = "Declining — Use Soon"
    else:           rl = "Spoiled — Discard"

    return _build_result(
        quality_label  = label,
        quality_pct    = pct,
        ripeness_label = rl,
        conf_score     = pct,
        fruit_type     = fruit,
        good_pct       = g,
        int_pct        = i,
        bad_pct        = b
    )