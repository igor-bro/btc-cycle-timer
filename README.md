# BTC Cycle Timer 🕰️📈

**Educational tool** that visualizes the temporal structure of the Bitcoin market based on 4-year cycles and halvings.

---

## 🔧 Key Features

- ⏳ Timers to:
  - Next halving (approximately April 2028)
  - Forecasted cycle peak (~October 2025)
  - Forecasted cycle bottom (~end of 2026)
- 📉 BTC average cycle chart with phases (Accumulation, Parabolic, Distribution, Capitulation)
- 📈 Profitability calculator based on past cycles
- 📊 Progress bar for current cycle completion
- 🌐 Web interface (Streamlit) and CLI with live updates (`rich.live`)
- 🔄 Multilingual support: `ua`, `en`, `fr`
- 🤖 Telegram bot (optional)
- 🛠️ .env support (secrets) and Hugging Face Spaces
- 📊 **Pattern projection** - historical pattern visualization based on previous cycles

---

## 🚀 Local Setup

```bash
git clone https://github.com/your-username/btc-cycle-timer.git
cd btc-cycle-timer
pip install -r requirements.txt
```

**CLI Launch:**

```bash
python btc_cycle_timer/main.py --lang=ua
```

Or, if installed as a package:

```bash
btc-cycle --lang=ua
```

**Web Version Launch:**

```bash
streamlit run btc_cycle_timer/app.py
```

---

## 🌍 Deployment on Hugging Face Spaces

1. Fork this repository
2. Create a new Space → choose `Streamlit` template
3. Connect GitHub repository
4. Add in Settings → Secrets:

   - `TELEGRAM_TOKEN`
   - `TELEGRAM_CHAT_ID`

5. Automatic update after push to `main`

---

## 🧪 Environment Variables (`.env`)

```env
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=...
APP_LANGUAGE=ua
DEBUG=false
```

---

## 📄 License

MIT License

---

## 📬 Author

Igor Kushneruk · [BTC Cycle Timer on GitHub](https://github.com/igor-bro/btc-cycle-timer)

---

## 🔄 Version History

### v0.1.1 (Current)

- ✅ **Pattern projection** - shows historical price patterns projected onto current cycle
- ✅ **Extended view** - displays 180 days from current date with full cycle visualization
- ✅ **Improved error handling** - silent error handling for production
- ✅ **Code cleanup** - removed debug outputs and Ukrainian comments
- ✅ **English comments** - all code comments now in English
- ✅ **Optimized performance** - reduced data loading operations

### v0.1.0

- Initial release with basic cycle timer functionality
- CLI and web interface
- Multilingual support
- Telegram bot integration

---

## 📚 Additional Documentation

- [API Documentation](API.md) - Complete API reference
- [Test Report](tests/report.md) - Detailed testing results
