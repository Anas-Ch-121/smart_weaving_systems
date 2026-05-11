# 🧵 Smart Weaving Management System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://smart-weaving.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-green.svg)](https://supabase.com/)

A professional, industrial-grade management solution for weaving factories. This system streamlines production tracking, inventory management, and financial oversight through a sleek, high-performance interface.

---

## 🚀 Overview

The **Smart Weaving Management System** is designed to replace manual ledger-keeping with a digital-first approach. It provides real-time insights into factory operations, helping owners and managers make data-driven decisions.

### Key Modules:
- **📊 Dynamic Dashboard:** At-a-glance view of Net Profit, Total Income, Expenses, and Active Looms.
- **📦 Inventory Control:** Real-time tracking of raw materials (yarn, thread, etc.) with restocking capabilities.
- **⚙️ Loom Management:** Monitor loom status (Active, Idle, Maintenance) and schedule service dates.
- **🏭 Production Logs:** Detailed recording of daily output mapped to specific operators and materials used.
- **💰 Financial Suite:** Automated profit/loss calculation based on production income and operational expenses.
- **🔐 Secure Access:** Role-based access control (RBAC) for Admins and Operators.

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) (Data-focused UI Framework)
- **Backend/DB:** [Supabase](https://supabase.com/) (PostgreSQL + Real-time APIs)
- **Data Handling:** [Pandas](https://pandas.pydata.org/) (Data Manipulation)
- **Styling:** Custom CSS with [Google Fonts](https://fonts.google.com/) (Rajdhani, Share Tech Mono)

---

## 📂 Project Structure

```bash
smart_weaving_machine/
├── streamlit_app.py     # Main frontend application
├── app_backend.py      # Optional Flask API (Alternative access layer)
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/smart-weaving-machine.git
cd smart_weaving_machine
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Supabase
Create a `.streamlit/secrets.toml` file in the root directory and add your Supabase credentials:

```toml
SUPABASE_URL = "your_supabase_project_url"
SUPABASE_KEY = "your_supabase_anon_key"
```

### 4. Run the Application
```bash
streamlit run streamlit_app.py
```

---

## 📊 Database Schema

The system relies on a PostgreSQL schema hosted on Supabase. Key tables include:
- `app_user`: System users and credentials.
- `resource`: Universal table for Looms and Raw Materials.
- `production`: Daily logs of weaving output.
- `financial_record`: Ledger for income and expenses.

*For a full SQL export of the schema, please contact the administrator.*

---

## 🎨 UI Aesthetics

The application features a **Cyber-Industrial Dark Theme** optimized for high-contrast visibility in factory environments. It uses:
- **Neon Blue Accents** for primary actions.
- **Share Tech Mono** font for numeric data to ensure readability.
- **Glassmorphic** stat cards for a premium feel.

---

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---
*Developed for the DB Lab Project — Semester 4*
