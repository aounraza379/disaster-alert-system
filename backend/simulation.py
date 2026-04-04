import random
import math
import json
from datetime import datetime, timezone, timedelta

# --- Haversine (standalone, no imports needed) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- Disaster zone center (simulated earthquake epicenter) ---
DISASTER_LAT = 24.8607
DISASTER_LON = 67.0011
DISASTER_RADIUS_KM = 150

# --- Trust score calculator (mirrors trust.py logic) ---
def calculate_trust(lat, lon, hours_old, vouch_count, is_near_disaster):
    location_score = 0.4 if is_near_disaster else 0.1

    vouch_score = min(vouch_count * 0.1, 0.4)

    if hours_old <= 6:
        temporal = 0.2
    elif hours_old <= 12:
        temporal = 0.15
    elif hours_old <= 24:
        temporal = 0.10
    else:
        temporal = 0.05

    return round(location_score + vouch_score + temporal, 3)

# --- Generate posts ---
def generate_posts(n_real=700, n_fake=300):
    posts = []

    # REAL posts — inside disaster zone, recent, some vouches
    for i in range(n_real):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, DISASTER_RADIUS_KM)
        lat = DISASTER_LAT + (distance / 111) * math.cos(angle)
        lon = DISASTER_LON + (distance / 111) * math.sin(angle)
        hours_old = random.uniform(0, 18)
        vouches = random.randint(0, 4)
        dist = haversine(lat, lon, DISASTER_LAT, DISASTER_LON)
        is_near = dist <= DISASTER_RADIUS_KM
        score = calculate_trust(lat, lon, hours_old, vouches, is_near)
        posts.append({
            "id": f"real_{i}",
            "label": "real",
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "hours_old": round(hours_old, 1),
            "vouch_count": vouches,
            "is_near_disaster": is_near,
            "trust_score": score
        })

    # FAKE/Sybil posts — far from zone, old, no vouches
    for i in range(n_fake):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(300, 800)
        lat = DISASTER_LAT + (distance / 111) * math.cos(angle)
        lon = DISASTER_LON + (distance / 111) * math.sin(angle)
        hours_old = random.uniform(20, 72)
        vouches = random.randint(0, 1)
        dist = haversine(lat, lon, DISASTER_LAT, DISASTER_LON)
        is_near = dist <= DISASTER_RADIUS_KM
        score = calculate_trust(lat, lon, hours_old, vouches, is_near)
        posts.append({
            "id": f"fake_{i}",
            "label": "fake",
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "hours_old": round(hours_old, 1),
            "vouch_count": vouches,
            "is_near_disaster": is_near,
            "trust_score": score
        })

    return posts

# --- Evaluate system performance ---
def evaluate(posts, threshold=0.3):
    tp = 0  # fake correctly flagged
    fp = 0  # real incorrectly flagged
    tn = 0  # real correctly passed
    fn = 0  # fake missed

    for post in posts:
        predicted_fake = post["trust_score"] <= threshold
        actually_fake = post["label"] == "fake"

        if predicted_fake and actually_fake:
            tp += 1
        elif predicted_fake and not actually_fake:
            fp += 1
        elif not predicted_fake and not actually_fake:
            tn += 1
        else:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (tp + tn) / len(posts)

    return {
        "total_posts": len(posts),
        "real_posts": sum(1 for p in posts if p["label"] == "real"),
        "fake_posts": sum(1 for p in posts if p["label"] == "fake"),
        "threshold": threshold,
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "accuracy": round(accuracy, 4)
    }

# --- Run ---
if __name__ == "__main__":
    random.seed(42)
    print("Generating 1000 posts (700 real, 300 fake)...")
    posts = generate_posts(700, 300)

    print("\n--- Spatial-Trust Simulation Results ---")
    for threshold in [0.2, 0.3, 0.35]:
        result = evaluate(posts, threshold)
        print(f"\nThreshold: {threshold}")
        print(f"  Accuracy:  {result['accuracy']*100:.1f}%")
        print(f"  Precision: {result['precision']*100:.1f}%")
        print(f"  Recall:    {result['recall']*100:.1f}%")
        print(f"  F1 Score:  {result['f1_score']*100:.1f}%")
        print(f"  Fakes caught: {result['true_positives']}/{result['fake_posts']}")
        print(f"  Real wrongly flagged: {result['false_positives']}/{result['real_posts']}")

    # save full results
    with open("simulation_results.json", "w") as f:
        json.dump({
            "summary": [evaluate(posts, t) for t in [0.2, 0.3, 0.35]],
            "sample_posts": posts[:20]
        }, f, indent=2)
    print("\nFull results saved to simulation_results.json")