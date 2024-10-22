import os
import dotenv

dotenv.load_dotenv()
bot_token = os.getenv("TG_BOT_KEY")
db_url = os.getenv("TG_BOT_DB")
