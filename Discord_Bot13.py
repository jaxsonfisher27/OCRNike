import discord 
import pytesseract
from PIL import Image
import subprocess
import io
from io import BytesIO
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Discord Bot Token
DISCORD_BOT_TOKEN = "INSERT YOUR DISCORD BOT TOKEN HERE"

# Google Sheets Setup
SHEET_NAME = "Discord Bot Test" #INSERT YOUR SHEET NAME HERE
START_ROW = 100  # Starting row for output
COL_START = 1  # Start column for the first entry
COL_SPACING = 1  # Space between entries

# Google API Authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("INSERT_YOUR_API_KEY_HERE.json", scope) #ADD YOUR API .JSON FILE HERE
client_gs = gspread.authorize(creds)
sheet = client_gs.open(SHEET_NAME).sheet1

# Define intents for Discord bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True  # Required for fetching member nicknames

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    print("Bot is ready and waiting for image uploads.")

@client.event
async def on_message(message):
    if message.attachments:
        server_nickname = message.author.display_name  # Use server nickname
        extracted_data = []  # Store extracted data for this user

        for attachment in message.attachments:
            print(f"Processing: {attachment.filename}")

            if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg')):
                img_bytes = await attachment.read()
                img = Image.open(BytesIO(img_bytes))

                # Save the image temporarily
                img_path = "/tmp/temp_image.png"
                img.save(img_path)

                # Preprocess with ImageMagick for better OCR accuracy
                cleaned_image_path = "/tmp/cleaned_image.png"
                subprocess.run(['convert', img_path, '-deskew', '60%', '-threshold', '50%', cleaned_image_path])

                cleaned_img = Image.open(cleaned_image_path)
                extracted_text = pytesseract.image_to_string(cleaned_img)

                # Extract boss name
                lines = extracted_text.split("\n")
                boss_name = None
                for line in lines:
                    clean_line = re.sub(r'[^A-Za-z0-9 ]', '', line).strip()  # Remove non-alphanumeric characters
                    if clean_line and not clean_line.lower().startswith(("hp remaining", "total damage")):
                        boss_name = clean_line
                        break  # First valid text is the boss name

                # Extract TOTAL DAMAGE value
                match = re.search(r'TOTAL DAMAGE\s*([\d,]+)', extracted_text)
                if boss_name and match:
                    total_damage = format(int(match.group(1).replace(",", "")), ",")  # Ensure proper comma formatting
                    extracted_data.append((boss_name, total_damage))

        if extracted_data:
            insert_into_sheet(server_nickname, extracted_data)
            response = f"{server_nickname}: " + " | ".join([f"{boss}: {damage}" for boss, damage in extracted_data])
            await message.channel.send(response)
            print("Extracted:", response)
        else:
            print("No valid data found, skipping.")

def insert_into_sheet(nickname, data):
    """ Inserts extracted data into Google Sheets with each user getting one row """
    global START_ROW

    row = START_ROW
    col = COL_START

    # Insert the user's name in the first column
    sheet.update_cell(row, col, nickname)
    col += COL_SPACING + 1  # Move to the next column

    # Insert extracted data horizontally
    for boss, damage in data:
        sheet.update_cell(row, col, boss)
        sheet.update_cell(row, col + 1, damage)
        col += COL_SPACING + 2  # Move to the next pair of columns

    # Move START_ROW down for the next user
    START_ROW += 1  

# Run the bot
client.run(DISCORD_BOT_TOKEN)
