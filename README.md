# IdeaSaarthi 🚀

**Startup Validation & Investor Matching Platform**

IdeaSaarthi is an advanced web platform that helps entrepreneurs validate their startup ideas and connect with relevant investors. The platform leverages AI (Google Gemini) to generate detailed SWOT analysis and potential scores for submitted ideas.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/suryansh18saxena/Startup-Idea-Validator)

---



## ✨ Core Features

The platform is designed for two primary user types: **Entrepreneurs (Users)** and **Investors**.

### 🚀 For Entrepreneurs

- **Secure Authentication**: Create an account and login securely
- **Idea Submission**: Submit your startup idea through a comprehensive form (problem, solution, market, etc.)
- **AI-Powered SWOT Analysis**: Get instant detailed SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis with scores for each section powered by Google Generative AI
- **Idea Dashboard**: Manage (Edit/Delete) all your submitted ideas in one place
- **View Reports**: Access detailed analysis reports for your ideas
- **Connection Management**: Accept or reject introduction requests from interested investors

### 💸 For Investors

- **Investor Authentication**: Separate signup and login system for investors
- **Deal Flow Dashboard**: Browse all startup ideas submitted by entrepreneurs
- **View Analysis**: Review detailed SWOT reports and scores to make data-driven investment decisions
- **Request Introduction**: Send introduction requests directly to entrepreneurs for ideas you're interested in
- **My Connections**: Track all sent requests and accepted connections

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Backend** | Python, Django |
| **Database** | SQLite3 (default) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **AI API** | Google Generative AI (Gemini) |
| **Deployment** | Ready for any WSGI server (Gunicorn) |

---

## 🗂️ Project Structure

The project is organized into three main Django apps:

- **`home`**: Handles static pages like Home, About, and Features
- **`accounts`**: Manages registration, login, and logout functionality for both Users and Investors
- **`dashboard`**: Core of the project - handles idea submission, AI analysis (`api_service.py`), user/investor dashboards, and the connection system (models: Ideas, Connection)

---

## 🚀 Getting Started

Follow these steps to run the project on your local machine:

### 1. Prerequisites

- Python 3.10+
- pip & virtualenv

### 2. Installation

**Clone the Repository:**

```bash
git clone https://github.com/suryansh18saxena/Startup-Idea-Validator.git
cd Startup-Idea-Validator/startup
```

**Create and Activate Virtual Environment:**

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Install Dependencies:**

```bash
pip install -r requirements.txt
```

**Set Environment Variables:**

Create a `.env` file in the `startup` directory:

```ini
# .env
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

> **Note**: Get your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

**Run Database Migrations:**

```bash
python manage.py migrate
```

**Create Superuser (Optional):**

For admin panel access:

```bash
python manage.py createsuperuser
```

**Run Development Server:**

```bash
python manage.py runserver
```

Access the project at `http://127.0.0.1:8000/`

---

## 📈 Usage

### Entrepreneur Flow

1. Navigate to `/accounts/signup/` and create a new "User" account
2. Login and you'll be redirected to the user dashboard
3. Click "Submit Idea" and fill out the form
4. After submission, AI analysis will run and you'll be redirected to the report page
5. View and manage all your ideas in "Manage Ideas"
6. Review and respond to investor introduction requests in "Connections"

### Investor Flow

1. Navigate to `/accounts/investor_signup/` and create a new "Investor" account
2. Login and you'll be redirected to the investor dashboard (Deal Flow)
3. Browse startup ideas submitted by entrepreneurs
4. Click "View Analysis" to review detailed SWOT reports
5. Click "Request Introduction" to connect with the idea's founder
6. Track your requests in "My Connections"

---

## 🔑 Key Highlights

- **AI-Powered Insights**: Leverages Google Gemini to provide objective, data-driven startup validation
- **Two-Sided Marketplace**: Connects entrepreneurs with potential investors seamlessly
- **Comprehensive Analysis**: SWOT framework with numerical scores for quick evaluation
- **User-Friendly Interface**: Clean, intuitive design for both entrepreneurs and investors
- **Secure Authentication**: Separate authentication flows for different user types

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/suryansh18saxena/Startup-Idea-Validator/issues).

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**Suryansh Saxena**

- GitHub: [@suryansh18saxena](https://github.com/suryansh18saxena)

---

## 🙏 Acknowledgments

- Google Generative AI (Gemini) for powering the SWOT analysis
- Django community for excellent documentation
- All contributors and users of IdeaSaarthi

---

**Made with ❤️ for the startup ecosystem**
