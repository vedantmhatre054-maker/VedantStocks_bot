from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import yfinance as yf

# =========================
# CONFIG
# =========================
import os
BOT_TOKEN = os.getenv("8543565347:AAHJWaQIZxj4BC_sKW5krFl5RqRq3421uHE")


WATCHLIST = [
    "RELIANCE",
    "TCS",
    "INFY",
    "ICICIBANK",
    "HDFCBANK",
    "ITC",
    "SBIN",
    "LT"
]

# =========================
# COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to VedantStocks_bot 📊\n\n"
        "Indian Swing Trading Assistant\n\n"
        "Commands:\n"
        "/start  - Start bot\n"
        "/help   - Help\n"
        "/market - Indian market summary\n"
        "/scan   - Swing stock scan\n"
        "/alert  - Set price alert\n\n"
        "Example:\n"
        "/alert RELIANCE 2500"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Available Commands\n\n"
        "/start  - Start bot\n"
        "/help   - Help menu\n"
        "/market - NIFTY & BANKNIFTY summary\n"
        "/scan   - Swing stock scan\n"
        "/alert RELIANCE 2500"
    )

async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        nifty = yf.Ticker("^NSEI").history(period="1d")
        bank = yf.Ticker("^NSEBANK").history(period="1d")

        nifty_change = ((nifty["Close"][-1] - nifty["Open"][-1]) / nifty["Open"][-1]) * 100
        bank_change = ((bank["Close"][-1] - bank["Open"][-1]) / bank["Open"][-1]) * 100

        msg = (
            "📊 Indian Market Summary\n\n"
            f"NIFTY 50 : {nifty_change:+.2f}%\n"
            f"BANKNIFTY: {bank_change:+.2f}%"
        )

        await update.message.reply_text(msg)

    except Exception:
        await update.message.reply_text("Unable to fetch market data.")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = []

    for stock in WATCHLIST:
        try:
            data = yf.Ticker(stock + ".NS").history(period="3mo")
            close = data["Close"]

            ema20 = close.ewm(span=20).mean()
            ema50 = close.ewm(span=50).mean()

            if close[-1] > ema20[-1] and close[-1] > ema50[-1]:
                results.append(stock)

        except Exception:
            continue

    if not results:
        await update.message.reply_text("No swing setups found today.")
        return

    msg = "📈 Swing Scan (NSE)\n\n"
    for i, s in enumerate(results, 1):
        msg += f"{i}. {s}\n"

    await update.message.reply_text(msg)

async def alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text(
            "Usage:\n/alert STOCK PRICE\nExample:\n/alert RELIANCE 2500"
        )
        return

    stock = context.args[0].upper()
    price = context.args[1]

    if not price.isdigit():
        await update.message.reply_text("Price must be a number.")
        return

    alert_data = {"stock": stock, "price": int(price)}

    try:
        with open("alerts.json", "r") as f:
            alerts = json.load(f)
    except FileNotFoundError:
        alerts = []

    alerts.append(alert_data)

    with open("alerts.json", "w") as f:
        json.dump(alerts, f, indent=2)

    await update.message.reply_text(
        f"✅ Alert set for {stock} at ₹{price}\n\n"
        "⚠️ Auto-trigger is disabled for now (stable mode)."
    )

# =========================
# MAIN
# =========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("scan", scan))
    app.add_handler(CommandHandler("alert", alert))

    print("VedantStocks_bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
