import os
import re
from telethon import TelegramClient

# Replace with your own credentials
api_id = '25196204'
api_hash = 'c00313cf2dc7feaad8bfe93f21a6b515'
phone_number = '9321452817'  # Your phone number used to sign up for Telegram
group_link = 't.me/nfo_data'  # Your group invite link

# Specify the download directory
DOWNLOAD_DIR = 'telegram_data'

# Create the download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Create a Telegram client
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # Connect to the client
    await client.start()

    # Resolve the group using the invite link
    group = await client.get_entity(group_link)

    # Get all messages in the group
    async for message in client.iter_messages(group):
        # Log basic message information
        print(f"Processing message ID: {message.id}, Date: {message.date}")

        # Check if the message contains a document
        if message.document:
            file_name = message.document.attributes[0].file_name
            print(f"Found document: {file_name}")

            # Only process files with a .feather extension
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
