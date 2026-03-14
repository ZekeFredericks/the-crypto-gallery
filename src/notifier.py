import requests
import json

# 🛑 PASTE YOUR DISCORD WEBHOOK URL HERE
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1482466626053079040/tYd0-jgsi9PLVBMvQlNm7E4yeQc1UIj1vNutwUj2VVt5L27z7ozTyEo0ycfuDa9pEMxj"

def send_discord_alert(asset, signal, price, timeframe):
    """Sends a beautifully formatted embed message to Discord."""
    if not DISCORD_WEBHOOK_URL or "discord.com/api/webhooks" not in DISCORD_WEBHOOK_URL:
        print("⚠️ Discord Webhook URL not configured.")
        return

    # Make the sidebar of the Discord message Green or Red based on the signal
    color = 65280 if "Bullish" in signal else 16711680 

    # We format this as a Discord "Embed" so it looks professional, not just plain text
    data = {
        "username": "The Matrix Engine",
        "embeds": [
            {
                "title": f"🚨 A+ CONFLUENCE DETECTED: {asset}",
                "description": f"**Signal:** {signal}\n**Price:** ${price}\n**Timeframe:** {timeframe}",
                "color": color,
                "footer": {"text": "Quant Matrix Live Scanner | Phase 2"}
            }
        ]
    }

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL, 
            data=json.dumps(data), 
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print(f"✅ Alert sent to Discord for {asset}!")
    except Exception as e:
        print(f"❌ Error sending Discord alert: {e}")