# 🏋️ Mahadev Fitness Club - Gym Management System

A modern, beautiful gym management system with manual WhatsApp integration for payment reminders and promotional messages.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 💪 **Member Management** - Add, edit, delete members
- 📊 **Revenue Dashboard** - Track payments and revenue
- 📱 **WhatsApp Integration** - Send payment reminders via WhatsApp
- 🔍 **Search & Filter** - Find members quickly
- 💳 **Payment Tracking** - Upload payment proofs
- 📋 **Pending Members** - See who needs to pay
- 💬 **Promotional Messages** - Send bulk messages to all members
- 🎨 **Modern UI** - Beautiful glass morphism design
- 📱 **Mobile Responsive** - Works on all devices

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/gym-management-system.git
cd gym-management-system

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Open browser
http://localhost:5000
```

**Default Login:**
- Username: `Ashish Singh`
- Password: `Ashish@123`

## 💰 Membership Plans & Fees

| Plan | Duration | Fees |
|------|----------|------|
| 1 Month | 31 days | ₹1,000 |
| 3 Months | 93 days | ₹2,500 |
| 6 Months | 186 days | ₹4,000 |
| 1 Year | 365 days | ₹8,000 |

## 📱 WhatsApp Features

### Individual Messages
- Click 📱 icon next to any member
- WhatsApp opens automatically with pre-filled message
- Just click send!

### Bulk/Promotional Messages
- Go to "Pending SMS" page
- Click "💬 Open All Phone Numbers"
- All phone numbers copied
- Create WhatsApp group/broadcast
- Paste numbers and send!

### Message Format
```
MAHADEV FITNESS CLUB
Hello {name},

Your gym fees of Rs.{fees} are due.
Plan: {plan}
Expiry: {expiry_date}

Pay Online: {payment_link}

UPI: ashishrajsngh@ybl
- Team Mahadev
```

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Custom CSS with Glass Morphism
- **Fonts:** Outfit, Space Mono (Google Fonts)

## 📁 Project Structure

```
gym-management-system/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment config
├── runtime.txt           # Python version
├── templates/            # HTML templates
│   ├── login.html
│   ├── dashboard.html
│   ├── members.html
│   ├── add_member.html
│   ├── edit_member.html
│   └── pending_sms.html
├── static/              # Static files
│   ├── style.css
│   └── uploads/         # Payment proof uploads
└── instance/            # Database (auto-created)
    └── database.db
```

## 🌐 Deploy to Render

1. Fork this repository
2. Go to [Render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name:** gym-management
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. Click "Create Web Service"

Your app will be live at: `https://your-app-name.onrender.com`

## 🔒 Security Notes

- Change default admin password in production
- Keep database backups
- Review payment proofs before confirmation
- Use HTTPS in production (Render provides this automatically)

## 📸 Screenshots

### Dashboard
Revenue tracking with beautiful charts and statistics

### Members Page
Search, filter, and manage all gym members

### Pending SMS
Send WhatsApp messages manually - no API needed!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created with ❤️ for Mahadev Fitness Club

## 🆘 Support

For issues or questions, please open an issue on GitHub.

---

**⭐ If you find this project helpful, please give it a star!**
