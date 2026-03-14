from src.notifier import send_discord_alert
import time

print("⚡ Booting up the Matrix Comms Test...")

# 1. Test a Bullish Alert (Should be Green in Discord)
print("Sending fake Bullish signal...")
send_discord_alert(
    asset="BTC/USDT", 
    signal="🔥 A+ Bullish", 
    price=71450.00, 
    timeframe="1h"
)

# Pause for 2 seconds so Discord doesn't rate-limit us
time.sleep(2)

# 2. Test a Bearish Alert (Should be Red in Discord)
print("Sending fake Bearish signal...")
send_discord_alert(
    asset="SOL/USDT", 
    signal="🔥 A+ Bearish", 
    price=89.50, 
    timeframe="1h"
)

print("✅ Test complete. Check your Discord channel!")