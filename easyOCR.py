import easyocr
import os
import csv
import cv2

reader = easyocr.Reader(['tr'])
image_folder = "/Users/mehmetmustafatunc/Desktop/KolayYol/tabela"
  # klasör adını senin yapına göre düzenle

output_csv = "ocr_sonuclari.csv"

with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Gorsel", "Okunan_Yazi", "Guven_Skoru"])

    for filename in os.listdir(image_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(image_folder, filename)
            image = cv2.imread(path)

            results = reader.readtext(image)
            print(f"📷 {filename}")

            for (bbox, text, conf) in results:
                print(f"   📝 {text} (güven: {conf:.2f})")
                writer.writerow([filename, text, round(conf, 2)])

print(f"\n✅ OCR tamamlandı. Sonuçlar şuraya yazıldı: {output_csv}")
