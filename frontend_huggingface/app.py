import cv2
import easyocr
import numpy as np
import gradio as gr
import os
import requests
import re

# Load Haar cascade for license plate detection
cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_russian_plate_number.xml')
plate_cascade = cv2.CascadeClassifier(cascade_path)

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])

VERIFY_URL = "https://numberplatedetection.glitch.me/verify_plate"

def clean_plate_text(text):
    # Remove any non-alphanumeric characters and convert to uppercase
    cleaned = re.sub(r'[^A-Za-z0-9]', '', text)
    return cleaned.upper()

def detect_plate(image):
    if image is None:
        return "No image uploaded", None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

    if len(plates) == 0:
        return "License plate not detected", image

    results_text = ""
    for (x, y, w, h) in plates:
        plate_img = image[y:y+h, x:x+w]
        result = reader.readtext(plate_img)
        raw_text = result[0][1] if result else "Text not recognized"

        if raw_text != "Text not recognized":
            text = clean_plate_text(raw_text)
            try:
                response = requests.post(VERIFY_URL, data={'car_number': text})
                response_json = response.json()

                if response.status_code == 200 and response_json.get("status") == "success":
                    data = response_json["data"]
                    results_text += (
                        f"Match Found:\n"
                        f"Name: {data['name']}\n"
                        f"Mobile: {data['mobile']}\n"
                        f"Email: {data['email']}\n"
                        f"Flat No: {data['flat_number']}\n"
                        f"Car Number: {data['car_number']}\n\n"
                    )
                else:
                    results_text += f"No match found for plate: {text}\n\n"

            except Exception as e:
                results_text += f"Error contacting backend for plate {text}: {e}\n\n"
        else:
            results_text += "License plate text could not be read.\n\n"

        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(image, f"Plate: {text if raw_text != 'Text not recognized' else 'N/A'}", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    return results_text.strip(), image

demo = gr.Interface(
    fn=detect_plate,
    inputs=gr.Image(type="numpy"),
    outputs=["text", "image"],
    title="License Plate Detector with User Info"
)

if __name__ == "__main__":
    demo.launch()

# import cv2
# import easyocr
# import numpy as np
# import gradio as gr
# import os
# import torch
# import requests
# import sqlite3

# # Load Haar cascade for license plate detection
# cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_russian_plate_number.xml')
# plate_cascade = cv2.CascadeClassifier(cascade_path)

# # Initialize EasyOCR Reader
# reader = easyocr.Reader(['en'])

# VERIFY_URL = "https://numberplatedetection.glitch.me/verify_plate"

# def detect_plate(image):
#     if image is None:
#         return "No image uploaded", None

#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

#     if len(plates) == 0:
#         return "License plate not detected", image

#     for (x, y, w, h) in plates:
#         plate_img = image[y:y+h, x:x+w]
#         result = reader.readtext(plate_img)
#         text = result[0][1] if result else "Text not recognized"

#         if text != "Text not recognized":
#             try:
#                 response = requests.post(VERIFY_URL, data={'car_number': text})
#                 response_json = response.json()

#                 if response.status_code == 200 and response_json.get("status") == "success":
#                     data = response_json["data"]
#                     result_text = (
#                         f"Match Found:\n\n"
#                         f"Name: {data['name']}\n"
#                         f"Mobile: {data['mobile']}\n"
#                         f"Email: {data['email']}\n"
#                         f"Flat No: {data['flat_number']}\n"
#                         f"Car Number: {data['car_number']}"
#                     )
#                 else:
#                     result_text = " No match found."

#             except Exception as e:
#                 result_text = f" Error contacting backend: {e}"
#         else:
#             result_text = " License plate text could not be read."

#         cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
#         cv2.putText(image, f"Plate: {text}", (x, y-10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

#         return result_text, image

#     return "No plate found", image

# demo = gr.Interface(
#     fn=detect_plate,
#     inputs=gr.Image(type="numpy"),
#     outputs=["text", "image"],
#     title="License Plate Detector with User Info"
# )

# if __name__ == "__main__":
#     demo.launch()