---

### 📄 `README.md`

````markdown
# BTC Cycle Timer 🕰️📈

**Освітній інструмент**, що візуалізує часову структуру ринку Біткоїна, ґрунтуючись на 4-річних циклах та халвінгах.

---

## 🔧 Основні функції

- ⏳ Таймери до:
  - Наступного халвінгу (орієнтовно квітень 2028)
  - Прогнозованого піку циклу (~жовтень 2025)
  - Прогнозованого дна циклу (~кінець 2026)
- 📉 Графік середнього циклу BTC з фазами (Accumulation, Parabolic, Distribution, Capitulation)
- 📈 Калькулятор прибутковості на основі минулих циклів
- 📊 Прогрес-бар проходження поточного циклу
- 🌐 Web-інтерфейс (Streamlit) та CLI з живим оновленням (`rich.live`)
- 🔄 Мультимовність: `ua`, `en`, `fr`
- 🤖 Telegram-бот (опційно)
- 🛠️ Підтримка .env (секретів) і Hugging Face Spaces

---

## 🚀 Запуск локально

```bash
git clone https://github.com/your-username/btc-cycle-timer.git
cd btc-cycle-timer
pip install -r requirements.txt
```

````

**Запуск CLI:**

```bash
python btc_cycle_timer/main.py --lang=ua
```

Або, якщо встановлено як пакет:

```bash
btc-cycle --lang=ua
```

**Запуск веб-версії:**

```bash
streamlit run btc_cycle_timer/app.py
```

---

## 🌍 Розгортання у Hugging Face Spaces

1. Fork цей репозиторій
2. Створи новий Space → обери шаблон `Streamlit`
3. Підключи GitHub репозиторій
4. Додай у Settings → Secrets:

   - `TELEGRAM_TOKEN`
   - `TELEGRAM_CHAT_ID`

5. Автоматичне оновлення після пушу до `main`

---

## 🧪 Змінні середовища (`.env`)

```env
TELEGRAM_TOKEN=...
TELEGRAM_CHAT_ID=...
APP_LANGUAGE=ua
DEBUG=false
```

---

## 📄 Ліцензія

MIT License

---

## 📬 Автор

Ігор Кушнерук · [BTC Cycle Timer on GitHub](https://github.com/igor-bro/btc-cycle-timer)

````
