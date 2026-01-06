import cv2
import os
import pandas as pd
from datetime import datetime

LABEL_KEYS = {
    "1": "open_palm",
    "2": "fist",
    "3": "thumbs_up",
    "4": "thumbs_down",
    "5": "ok_sign",
}

def main():
    os.makedirs("data/raw", exist_ok=True)
    labels_path = "data/raw/labels.csv"

    if os.path.exists(labels_path):
        df = pd.read_csv(labels_path)
    else:
        df = pd.DataFrame(columns=["image_id","label","source","collected_at","consent","notes"])

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam")

    next_idx = len(df) + 1

    print("Press 1-5 to save labeled image. Press q to quit.")
    print("Labels:", LABEL_KEYS)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Collector", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        if key != 255:
            key_char = chr(key)
            if key_char in LABEL_KEYS:
                label = LABEL_KEYS[key_char]
                image_id = f"image_{next_idx:04d}.jpg"
                path = os.path.join("data/raw", image_id)

                cv2.imwrite(path, frame)

                row = {
                    "image_id": image_id,
                    "label": label,
                    "source": "webcam",
                    "collected_at": datetime.now().isoformat(timespec="seconds"),
                    "consent": "yes",
                    "notes": ""
                }

                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                df.to_csv(labels_path, index=False)

                print(f"Saved {image_id} as {label}")
                next_idx += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
