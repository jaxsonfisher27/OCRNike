# OCRNike
Uses Tesseract-OCR and ImageMagick

Custom OCR Damage Tracker
Custom discord bot that will output Server_nickname, boss_name, and total_damage, ignoring all images that do not contain text matching the latter two criteria. Contains Google sheet integration with minimal setup. Every user who uploads various screenshots in a single message will be allocated a row in Sheets starting from cell 100 for easy copy/paste formatting

Install Dependencies (Roughly from what I can remember) May require --break-system-packages

  pip install opencv-python-headless
  apt install imagemagick
  apt-get install tesseract-ocr
  pip install gspread oath2client

![image](https://github.com/user-attachments/assets/c1f592bd-466e-49ac-b180-fde3d15f6d75)
![image](https://github.com/user-attachments/assets/0fb47405-bed7-4764-97c2-b96a01bc7b91)
![image](https://github.com/user-attachments/assets/03942ad8-b8e7-4926-96a7-f198a85464b7)
