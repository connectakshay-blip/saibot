import feedparser
import asyncio
from telegram import Bot

# Replace with your bot token and channel username
BOT_TOKEN = "8112696022:AAHIx3-HTPh90k1K_HWBN9zVYhEDlzw4raw"
CHANNEL_ID = "@success_achievers_institute"   # Example: @successachieversofficial

# Replace with your YouTube channel ID
YOUTUBE_FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCNyCddbKRExE2JDCqqa9ymQ"

bot = Bot(token=BOT_TOKEN)

async def check_youtube():
    last_video_id = None
    pinned_message_id = None   # track pinned LIVE
    pinned_video_id = None     # track which LIVE video is pinned

    while True:
        try:
            feed = feedparser.parse(YOUTUBE_FEED_URL)

            if feed.entries:
                latest = feed.entries[0]
                video_id = latest.yt_videoid
                title = latest.title
                link = latest.link

                # Thumbnail
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

                # Check if LIVE (tags may contain "live")
                is_live = any(
                    "live" in tag.term.lower()
                    for tag in getattr(latest, "tags", [])
                )

                # ✅ If new video detected
                if video_id != last_video_id:
                    caption = (
                        f"🔴 *Live Class Started!*\n\n🎥 {title}\n👉 {link}"
                        if is_live
                        else f"📢 *New Lecture Uploaded!*\n\n🎥 {title}\n👉 {link}"
                    )

                    msg = await bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=thumbnail_url,
                        caption=caption,
                        parse_mode="Markdown"
                    )

                    # ✅ Pin new LIVE (unpin old one if needed)
                    if is_live:
                        if pinned_message_id:
                            try:
                                await bot.unpin_chat_message(chat_id=CHANNEL_ID, message_id=pinned_message_id)
                                print("📍 Unpinned previous LIVE")
                            except Exception as e:
                                print(f"⚠️ Failed to unpin old LIVE: {e}")

                        await bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=msg.message_id, disable_notification=False)
                        pinned_message_id = msg.message_id
                        pinned_video_id = video_id
                        print(f"📌 Pinned LIVE: {title}")

                    else:
                        print(f"✅ Posted normal video: {title}")

                    last_video_id = video_id

                # ✅ If current video is not live, but old LIVE was pinned → unpin
                elif not is_live and pinned_message_id and pinned_video_id == video_id:
                    try:
                        await bot.unpin_chat_message(chat_id=CHANNEL_ID, message_id=pinned_message_id)
                        print("📍 Unpinned old LIVE (ended)")
                        pinned_message_id = None
                        pinned_video_id = None
                    except Exception as e:
                        print(f"⚠️ Unpin failed: {e}")

        except Exception as e:
            print(f"❌ Error: {e}")

        await asyncio.sleep(300)  # check every 5 minutes

async def main():
    await check_youtube()

if __name__ == "__main__":
    asyncio.run(main())
