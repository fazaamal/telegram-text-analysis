import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient, events
import pandas as pd
import nltk
from dotenv import load_dotenv
import os

load_dotenv()
# Replace with your actual API ID, API hash, and phone number
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")
group_name = os.getenv("GROUP_NAME")

print(api_id, api_hash, phone_number, group_name)

# Set the time range to get messages from
start_time = datetime.now() - timedelta(hours=24)

async def get_group_messages():
    df = pd.DataFrame({'Data': [''], 'name': [''], 'mobile': [''], 'sentiment_score': [0.0]})

    client = TelegramClient('session_name', api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input('Enter the code: '))

    # Get the entity using the group name
    entity = await client.get_entity(group_name)

    date_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = date_today - timedelta(days=5)

    messages = []

    async for message in client.iter_messages(entity, min_id=1):
        print(message.date, yesterday)
        if str(message.date) < str(yesterday):
            break

        # Check sentiment of the message
        sentiment_score = calculate_sentiment_score(message.text)
        df = df._append({'Data': message.text, 'name': message.sender_id, 'mobile': message.date, 'sentiment_score': sentiment_score}, ignore_index=True)

    # Save dataframe to CSV
    df.to_csv('telegram_messages.csv', index=False)

def calculate_sentiment_score(message_text):
    # Load word files
    with open('booster_decr.txt', 'r') as f:
        booster_decr = f.read().splitlines()

    with open('booster_inc.txt', 'r') as f:
        booster_inc = f.read().splitlines()

    with open('negation.txt', 'r') as f:
        negation = f.read().splitlines()

    with open('negative.txt', 'r') as f:
        negative = f.read().splitlines()

    with open('positive.txt', 'r') as f:
        positive = f.read().splitlines()

    # Calculate sentiment score
    if(message_text == None):
      return 0
    words = nltk.word_tokenize(message_text.lower())
    sentiment_score = 0.0

    for word in words:
        if word in booster_decr:
            sentiment_score -= 1
        elif word in booster_inc:
            sentiment_score += 1
        elif word in negation:
            sentiment_score = -sentiment_score
        elif word in negative:
            sentiment_score -= 1
        elif word in positive:
            sentiment_score += 1

    # Normalize sentiment score between 0 and 1
    if(len(words) == 0):
      return 0
    normalized_score = (sentiment_score + len(words)) / (2 * len(words))
    return normalized_score

asyncio.run(get_group_messages())