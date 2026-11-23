import argparse
import csv
import time
from pathlib import Path

import joblib
import pandas as pd

from app.ml.feature_adapter import adapt_features
from app.database.db import SessionLocal
from app.ml.models import AIFlowPrediction


MODEL_PATH = Path("models/portscan_random_forest_unique.joblib")


def save_predictions(results):
    if not results:
        return 0

    with SessionLocal() as db:
        for result in results:
            prediction = AIFlowPrediction(
                source_ip=result["source_ip"],
                destination_ip=result["destination_ip"],
                destination_port=int(result["destination_port"]),
                prediction=result["prediction"],
                confidence=result["confidence"],
            )
            db.add(prediction)

        db.commit()

    print(f"Saved AI predictions: {len(results)}", flush=True)
    return len(results)


def analyze_flows(csv_path):
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    features = bundle["features"]

    with open(csv_path, newline="") as file:
        flows = list(csv.DictReader(file))

    if not flows:
        print("No network flows available for analysis")
        return []

    samples = []

    for flow in flows:
        adapted = adapt_features(flow)
        samples.append([adapted[name] for name in features])

    frame = pd.DataFrame(samples, columns=features)
    predictions = model.predict(frame)
    probabilities = model.predict_proba(frame)

    results = []

    for index, (flow, prediction, probability) in enumerate(
        zip(flows, predictions, probabilities), start=1
    ):
        confidence = float(max(probability))

        result = {
            "source_ip": flow.get("src_ip", ""),
            "destination_ip": flow.get("dst_ip", ""),
            "destination_port": flow.get("dst_port", ""),
            "prediction": str(prediction),
            "confidence": confidence,
        }

        results.append(result)

        print(
            f"Flow {index}: "
            f"{result['source_ip']} -> {result['destination_ip']} "
            f"port {result['destination_port']} | "
            f"{result['prediction']} | "
            f"confidence {confidence:.2%}"
        )

    print(f"Total analyzed flows: {len(results)}")
    save_predictions(results)
    return results


def load_checkpoint(csv_path):
    checkpoint = Path(str(csv_path) + ".checkpoint")

    if not checkpoint.exists():
        return 0

    try:
        return max(0, int(checkpoint.read_text().strip()))
    except (ValueError, OSError):
        return 0


def save_checkpoint(csv_path, processed):
    checkpoint = Path(str(csv_path) + ".checkpoint")
    temporary = Path(str(checkpoint) + ".tmp")
    temporary.write_text(str(processed))
    temporary.replace(checkpoint)


def watch_flows(csv_path, interval=5):
    print(f"Watching AI flows: {csv_path}", flush=True)
    processed = load_checkpoint(csv_path)

    try:
        while True:
            path = Path(csv_path)

            if path.exists():
                with path.open(newline="") as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)

                if len(rows) < processed:
                    processed = 0

                if len(rows) > processed:
                    new_rows = rows[processed:]
                    print(
                        f"New flows detected: {len(new_rows)}",
                        flush=True,
                    )

                    temporary_path = path.with_name(
                        path.stem + "_pending.csv"
                    )

                    with temporary_path.open("w", newline="") as file:
                        writer = csv.DictWriter(
                            file,
                            fieldnames=list(rows[0].keys()),
                        )
                        writer.writeheader()
                        writer.writerows(new_rows)

                    analyze_flows(temporary_path)
                    processed = len(rows)
                    save_checkpoint(csv_path, processed)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("Processing remaining AI flows", flush=True)

        path = Path(csv_path)

        if path.exists():
            with path.open(newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            if len(rows) > processed:
                remaining = rows[processed:]
                temporary_path = path.with_name(
                    path.stem + "_final.csv"
                )

                with temporary_path.open("w", newline="") as file:
                    writer = csv.DictWriter(
                        file,
                        fieldnames=list(rows[0].keys()),
                    )
                    writer.writeheader()
                    writer.writerows(remaining)

                analyze_flows(temporary_path)
                processed = len(rows)
                save_checkpoint(csv_path, processed)

                print(
                    f"Final AI flows processed: {len(remaining)}",
                    flush=True,
                )

        print("AI flow monitoring stopped", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()

    if args.watch:
        watch_flows(args.csv_path)
    else:
        analyze_flows(args.csv_path)
