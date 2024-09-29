import os
import re
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')
group_link = os.getenv('GROUP_LINK')

DOWNLOAD_DIR = 'telegram_data'

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start()

    group = await client.get_entity(group_link)

    async for message in client.iter_messages(group):
        print(f"Processing message ID: {message.id}, Date: {message.date}")

        if message.document:
            file_name = message.document.attributes[0].file_name
            print(f"Found document: {file_name}")

            if file_name.endswith('.feather'):
                # Extract the date from the file name
                match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', file_name)

                if match:
                    year, month, day = match.groups()

                    # Create directory structure: year/month/
                    dir_path = os.path.join(DOWNLOAD_DIR, year, month)
                    os.makedirs(dir_path, exist_ok=True)

                    # Download the file to the appropriate directory
                    file_path = os.path.join(dir_path, file_name)
                    await client.download_media(message, file_path)
                    print(f'Downloaded: {file_path}')
                else:
                    print(f"File name {file_name} does not match date format.")
        else:
            print("No document found in this message.")

with client:
    client.loop.run_until_complete(main())
