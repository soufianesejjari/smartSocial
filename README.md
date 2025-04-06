# SmartSocial Manager

SmartSocial Manager is a social media management application powered by LLMs (Large Language Models) and Facebook Graph API. It provides features like sentiment analysis, content creation, post scheduling, and automated comment replies.

## Features

- **Dashboard**: View recent posts, comments, and sentiment analysis.
- **Sentiment Analysis**: Analyze the sentiment of comments (positive, negative, neutral).
- **Content Creation**: Generate content suggestions using LLMs.
- **Post Scheduling**: Schedule posts for future publication.
- **Automated Replies**: Generate and send professional replies to comments.
- **Profile Management**: Configure page profiles, target audience, and response templates.

---

## Project Structure

```
├── app/
│   ├── __init__.py         # Application factory
│   ├── config.py           # Configuration using Pydantic
│   ├── models.py           # Database models
│   ├── services/           # Service layer for business logic
│   │   ├── __init__.py
│   │   ├── facebook_service.py  # Facebook Graph API integration
│   │   ├── llm_service.py       # LLM integration (Groq)
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── dashboard_service.py # Dashboard logic
│   │   └── scheduling_service.py # Post scheduling logic
│   ├── blueprints/         # Flask blueprints for routes
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication routes
│   │   ├── dashboard.py        # Dashboard routes
│   │   ├── content.py          # Content creation routes
│   │   ├── comments.py         # Comment management routes
│   │   └── settings.py         # Profile settings routes
│   ├── templates/          # HTML templates
│   │   ├── base.html           # Base layout
│   │   ├── auth/               # Login and register templates
│   │   ├── dashboard/          # Dashboard templates
│   │   ├── content/            # Content creation templates
│   │   ├── comments/           # Comment management templates
│   │   └── settings/           # Profile settings templates
│   ├── static/             # Static files (CSS, JS)
│   │   └── css/
│   │       └── style.css       # Custom styles
├── tests/                  # Unit tests (not implemented)
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── run.py                  # CLI for running the application
└── README.md               # Project documentation
```

---

## Installation

### Prerequisites

- Python 3.9 or higher
- MongoDB installed and running locally
- Facebook Page Access Token with required permissions
- Groq API Key

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/smartsocial.git
   cd smartsocial
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the `.env` file:
   ```plaintext
   FACEBOOK_PAGE_ACCESS_TOKEN=your_facebook_page_access_token
   FACEBOOK_PAGE_ID=your_facebook_page_id
   GROQ_API_KEY=your_groq_api_key
   MONGODB_URI=mongodb://localhost:27017/smartsocial
   SECRET_KEY=your_secret_key
   ```

5. Initialize the database:
   ```bash
   python run.py init-db
   ```

6. Create an admin user:
   ```bash
   python run.py create-admin
   ```

7. Run the application:
   ```bash
   python run.py run
   ```

---

## Usage

### CLI Commands

- **Run the application**:
  ```bash
  python run.py run
  ```

- **Initialize the database**:
  ```bash
  python run.py init-db
  ```

- **Create an admin user**:
  ```bash
  python run.py create-admin
  ```

- **Perform a health check**:
  ```bash
  python run.py health-check
  ```

---

## Features in Detail

### Dashboard
- View recent posts and comments.
- Analyze sentiment of comments (positive, negative, neutral).
- View engagement metrics like total comments and average comments per post.

### Content Creation
- Create new posts and schedule them for future publication.
- Generate content suggestions using LLMs.

### Comment Management
- Monitor comments on posts.
- Automatically reply to comments using AI-generated responses.
- Filter and view negative comments.

### Profile Settings
- Configure page profile details like name, category, and target audience.
- Manage response templates for automated replies.

---

## Technologies Used

- **Backend**: Flask
- **Database**: MongoDB
- **LLM Integration**: Groq (via `langchain_groq`)
- **Frontend**: Bootstrap 5
- **APIs**: Facebook Graph API

---

## Development

### Running Tests
(Tests are not implemented yet. Add unit tests in the `tests/` directory.)

### Logging
Logs are stored in the `logs/` directory. You can view logs for debugging:
```bash
tail -f logs/smartsocial.log
```

---

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact

For questions or support, please contact:
- **Email**: sejjari.soufiane@gmail.com
- **GitHub**: [https://github.com/soufianesejjari/smartsocial](https://github.com/soufianesejjari/smartsocial)