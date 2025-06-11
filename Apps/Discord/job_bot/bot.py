import os
import json
import re
import logging
import asyncio
from logging.handlers import TimedRotatingFileHandler
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from dotenv import load_dotenv
from datetime import datetime, time as dtime, timedelta
from zoneinfo import ZoneInfo
import requests

# ---------- Logging Setup ----------
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("jobbot")
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler("logs/jobbot.log", when="midnight", backupCount=7, encoding="utf-8")
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())

# ---------- Environment Variables ----------
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
COUNTRY = os.getenv("ADZUNA_COUNTRY", "de")

# ---------- File Constants ----------
CONFIG_FILE = "config.json"
JOBS_SEEN_FILE = "jobs_seen.json"
SAVED_JOBS_FILE = "saved_jobs.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ---------- Configuration Management ----------
def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {"location": "Coburg", "radius": 100, "keywords": ["system administrator"], "work_type": "all", "execution_time": "12:00"}
        with open(CONFIG_FILE, "w") as f:
            json.dump(default, f, indent=2)
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# ---------- Job Memory ----------
def load_seen_jobs():
    if not os.path.exists(JOBS_SEEN_FILE):
        with open(JOBS_SEEN_FILE, "w") as f:
            json.dump({"posted_ids": []}, f)
    with open(JOBS_SEEN_FILE) as f:
        return set(json.load(f)["posted_ids"])

def save_seen_jobs(job_ids):
    with open(JOBS_SEEN_FILE, "w") as f:
        json.dump({"posted_ids": list(job_ids)}, f, indent=2)

# ---------- Saved Jobs ----------
def save_job(job):
    jobs = []
    if os.path.exists(SAVED_JOBS_FILE):
        with open(SAVED_JOBS_FILE) as f:
            jobs = json.load(f)
    jobs.append(job)
    with open(SAVED_JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

def load_saved_jobs():
    if os.path.exists(SAVED_JOBS_FILE):
        with open(SAVED_JOBS_FILE) as f:
            return json.load(f)
    return []

def clear_saved_jobs():
    with open(SAVED_JOBS_FILE, "w") as f:
        json.dump([], f)

# ---------- CSV Export (DISABLED) ----------
def export_saved_jobs():
    # Export is currently disabled to avoid syntax errors
    return "Export currently disabled."

# ---------- Keyword Highlighting ----------
def highlight_keywords(text, keywords):
    for kw in sorted(keywords, key=len, reverse=True):
        text = re.sub(rf"(?i)\\b({re.escape(kw)})\\b", r"**\\1**", text)
    return text

# ---------- Interactive Discord Buttons ----------
class JobView(View):
    def __init__(self, job):
        super().__init__(timeout=None)
        self.job = job

    @discord.ui.button(label="💾 Save", style=discord.ButtonStyle.green)
    async def save_button(self, interaction: discord.Interaction, button: Button):
        save_job(self.job)
        await interaction.response.send_message("✅ Job saved!", ephemeral=True)

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.grey)
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("⏩ Skipped.", ephemeral=True)

# ---------- Job Search ----------
async def search_jobs():
    config = load_config()
    keywords = config["keywords"]
    seen_ids = load_seen_jobs()
    all_jobs = []

    for kw in keywords:
        url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/1"
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": 3,
            "what": kw,
            "where": config["location"],
            "distance": config["radius"]
        }
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
            for job in data.get("results", []):
                job_id = job.get("id")
                if job_id in seen_ids:
                    continue
                job_obj = {
                    "id": job_id,
                    "title": job.get("title"),
                    "company": job.get("company", {}).get("display_name"),
                    "location": job.get("location", {}).get("display_name"),
                    "url": job.get("redirect_url")
                }
                all_jobs.append(job_obj)
                seen_ids.add(job_id)
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")

    if not all_jobs:
        logger.info("No new jobs found.")
        return

    save_seen_jobs(seen_ids)
    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
        for job in all_jobs:
            desc = f"🏢 **{highlight_keywords(job['title'], keywords)}**\n📍 {job['location']}\n🔗 {job['url']}"
            await channel.send(desc, view=JobView(job))
    except Exception as e:
        logger.error(f"Error sending job messages: {e}")

# ---------- Slash Commands ----------
@tree.command(name="favorites", description="Show saved jobs")
async def favorites(interaction: discord.Interaction):
    jobs = load_saved_jobs()
    if not jobs:
        await interaction.response.send_message("📭 No saved jobs found.", ephemeral=True)
        return
    msg_lines = [f"💼 **{job['title']}**\n🏢 {job['company']}\n📍 {job['location']}\n🔗 {job['url']}" for job in jobs[-10:]]
    await interaction.response.send_message("\n\n".join(msg_lines), ephemeral=True)

@tree.command(name="clear_favorites", description="Clear all saved jobs")
async def clear_favorites(interaction: discord.Interaction):
    clear_saved_jobs()
    await interaction.response.send_message("🧹 All saved jobs have been cleared.", ephemeral=True)

@tree.command(name="export_favorites", description="Export saved jobs as CSV (disabled)")
async def export_favorites(interaction: discord.Interaction):
    await interaction.response.send_message("📎 Export is currently disabled.", ephemeral=True)

@tree.command(name="config", description="Update job search settings")
@app_commands.describe(
    location="Job location",
    radius="Search radius in km",
    keywords="Comma-separated keywords",
    work_type="Type: remote, hybrid, onsite, all"
)
async def config(interaction: discord.Interaction, location: str, radius: int, keywords: str, work_type: str = "all"):
    config = {
        "location": location,
        "radius": radius,
        "keywords": [kw.strip() for kw in keywords.split(",")],
        "work_type": work_type.lower(),
        "execution_time": load_config().get("execution_time", "12:00")
    }
    save_config(config)
    await interaction.response.send_message("✅ Configuration saved.", ephemeral=True)

@tree.command(name="show_config", description="Show current search configuration")
async def show_config(interaction: discord.Interaction):
    config = load_config()
    kw = ", ".join(config["keywords"])
    msg = (
        f"📍 Location: {config['location']}\n"
        f"📏 Radius: {config['radius']} km\n"
        f"🔍 Keywords: {kw}\n"
        f"🧭 Work type: {config.get('work_type', 'all')}\n"
        f"⏰ Execution time: {config.get('execution_time', '12:00')}"
    )
    await interaction.response.send_message(msg, ephemeral=True)

@tree.command(name="set_time", description="Set daily job search time (HH:MM)")
@app_commands.describe(time="Format: HH:MM (e.g. 14:00)")
async def set_time(interaction: discord.Interaction, time: str):
    try:
        hour, minute = map(int, time.strip().split(":"))
        assert 0 <= hour < 24 and 0 <= minute < 60
    except:
        await interaction.response.send_message("❌ Invalid format. Use HH:MM (e.g. 08:00).", ephemeral=True)
        return
    config = load_config()
    config["execution_time"] = f"{hour:02d}:{minute:02d}"
    save_config(config)
    await interaction.response.send_message(f"✅ Time set to {hour:02d}:{minute:02d}.", ephemeral=True)

# ---------- Bot Startup ----------
@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user}")
    await tree.sync()
    await schedule_daily_search()

async def schedule_daily_search():
    config = load_config()
    hour, minute = map(int, config.get("execution_time", "12:00").split(":"))
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target < now:
        target += timedelta(days=1)
    delay = (target - now).total_seconds()
    logger.info(f"⏳ Waiting until {target.strftime('%Y-%m-%d %H:%M:%S %Z')} ({int(delay)}s)")
    await asyncio.sleep(delay)
    await search_jobs()
    while True:
        await asyncio.sleep(86400)
        await search_jobs()

bot.run(TOKEN)
