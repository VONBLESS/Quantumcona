import os
import re
import logging
import asyncio
from telethon import TelegramClient, errors
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with your own credentials
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')  # Your phone number used to sign up for Telegram
group_link = os.getenv('GROUP_LINK')  # Your group invite link

# Specify the download directory
DOWNLOAD_DIR = 'telegram_data'

# Create a Telegram client
session_name = 'session_name'
client = TelegramClient(session_name, api_id, api_hash)

async def download_file(message, category, year, month, file_name):
    """Asynchronously download a file and save it in the specified directory."""
    dir_path = os.path.join(DOWNLOAD_DIR, category, year, month)
    os.makedirs(dir_path, exist_ok=True)

    file_path = os.path.join(dir_path, file_name)

    try:
        await client.download_media(message, file_path)
        logging.info(f'Downloaded: {file_path}')
    except Exception as e:
        logging.error(f'Failed to download {file_name}: {e}')

async def main():
    # Connect to the client
    await client.start()

    # Resolve the group using the invite link
    group = await client.get_entity(group_link)

    download_tasks = []  # List to hold all download tasks

    # Get all messages in the group
    async for message in client.iter_messages(group):
        logging.info(f"Processing message ID: {message.id}, Date: {message.date}")

        # Check if the message contains a document
        if message.document:
            file_name = message.document.attributes[0].file_name
            logging.info(f"Found document: {file_name}")

            # Only process files with a .feather extension
            if file_name.endswith('.feather'):
                # Check if file is nfo or bfo and extract date from file name
                category = 'nfo' if 'nfo' in file_name.lower() else 'bfo' if 'bfo' in file_name.lower() else None
                if category is None:
                    logging.warning(f"File {file_name} is neither NFO nor BFO.")
                    continue  # Skip files that don't contain nfo or bfo

                # Extract the date from the file name
                match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', file_name)
                if match:
                    year, month, _ = match.groups()
                    # Create a download task and add it to the list
                    download_tasks.append(download_file(message, category, year, month, file_name))
                else:
                    logging.warning(f"File name {file_name} does not match date format.")
        else:
            logging.info("No document found in this message.")

    # Run all download tasks concurrently
    if download_tasks:
        await asyncio.gather(*download_tasks)

async def maintain_session():
    """Keep the session alive and handle reconnections."""
    global session_name
    while True:
        try:
            await main()
            break  # Exit the loop if `main` runs successfully
        except errors.SessionPasswordNeeded:
            logging.error("Session requires a password. Please enter your password.")
            break
        except errors.SessionRevoked:
            logging.error("Session has been revoked. Creating a new session.")
            os.remove(f'{session_name}.session')  # Remove the expired session
            await client.start()  # Start a new session
        except errors.FloodWait as e:
            logging.error(f"Flood wait error: {e}. Retrying in {e.seconds} seconds...")
            await asyncio.sleep(e.seconds)  # Wait before trying again
        except (errors.ConnectionError, errors.RPCError) as e:
            logging.error(f"Connection error: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)  # Wait before trying again
        except errors.SecurityError as e:
            logging.error(f"Security error: {e}. Session might have expired.")
            os.remove(f'{session_name}.session')  # Remove the expired session
            await client.start()  # Start a new session
        except Exception as e:
            logging.error(f"Error in main loop: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)  # Wait before trying again

with client:
    client.loop.run_until_complete(maintain_session())
