

# 📡 Webhook Alert Receiver and Telegram Notifier

This project is a simple **Flask-based Webhook API** that receives JSON alert data, saves the alerts into organized `.json` files based on `team`, `severity`, and `value`, and sends an alert notification message to a specified **Telegram chat**.

It can be used for **any system** that sends HTTP POST JSON alerts — it is **not limited to Prometheus**.

---

## ✨ How It Works

- Accepts incoming HTTP POST requests containing alerts in JSON format.
- Parses alert information:
  - `team`
  - `severity`
  - `value`
  - `summary`
  - `description`
- Saves the alert into a `.json` file based on `team`, `severity`, and `value`.
- Sends a formatted message to a Telegram group or user.
- If a file for that alert combination already exists, it appends the new alert to the existing file.

---

## 🛠 Technologies Used

- **Python 3**
- **Flask** for creating the webhook server
- **Requests** for sending messages to the Telegram Bot API
- **JSON** for data management
- **OS module** for directory and file operations

---
