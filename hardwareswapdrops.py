import time, smtplib, os
import praw
import windows_toasts
from email.message import EmailMessage

from dotenv import load_dotenv

# Load config from .env file
load_dotenv()
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
user_agent = os.getenv('user_agent')
reddit_username = os.getenv('reddit_username')
reddit_password = os.getenv('reddit_password')
gmail_address = os.getenv('gmail_address')
to_gmail_addresses = os.getenv('to_gmail_addresses')
gmail_password = os.getenv('gmail_password')


server = None
timeout = 30
found_timeout = 600
found = False
sent_post_ids = []


# Setup for PRAW
reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        username=reddit_username,
        password=reddit_password,
    )
subreddit = reddit.subreddit("hardwareswap")

wintoaster = windows_toasts.WindowsToaster('Python')

# Change to list of words to be searched for in post title
query = ['webcam']

use_email = False


while True:
    timestamp = time.strftime('%a %H:%M:%S')
    print(timestamp)
    # Grabs the latest post
    for post in subreddit.new(limit=2):
        found = False
        print(f"Latest: {post.title[:111]}")
        for word in query:
            if word.lower() in post.title.lower():
                found = True

        # Check for new post by comparing to latest post
        if found and post.id not in sent_post_ids:
            print("New post found")
            print("Trying to send message")
            try:
                # First send windows notification
                text = f"HWSwap Bot New post found: {post.title}"
                newToast = windows_toasts.ToastText1()
                newToast.SetBody(text)
                wintoaster.show_toast(newToast)

                # Compose message
                msg = EmailMessage()
                msg.set_content(f"{post.title}\n\n\n{post.selftext}")
                msg['Subject'] = f"HWSwap bot found a new post"
                msg['From'] = gmail_address
                msg['To'] = to_gmail_addresses

                # Setup Server and send
                if use_email:
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(gmail_address, gmail_password)
                    server.send_message(msg)
                    server.quit()

                print("Successfully sent message")

            except Exception as e:
                print("Something failed when sending a message:", e)

            # Update after success
            sent_post_ids.append(post.id)
            print(f"Waiting {found_timeout} seconds")
            time.sleep(found_timeout)

    print(f"Checking again in {timeout} seconds\n")
    time.sleep(timeout)
