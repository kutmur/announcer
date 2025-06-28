# BTU Announcer Bot 🎓

A modular Telegram bot designed specifically for **Bursa Technical University (BTÜ)** students to automatically receive the latest announcements from their academic departments.

## Features ✨

- **📚 28 Department Support**: Covers all major BTÜ faculties and departments
- **🔔 Real-time Notifications**: Automatic announcement scraping every 30 minutes
- **🎯 Smart Filtering**: Only sends new, unseen announcements
- **📱 User-friendly Interface**: Simple department selection via keyboard
- **📊 Statistics**: Track bot usage and announcement delivery
- **🔄 Manual Updates**: Users can trigger manual checks with `/update`

## Supported Departments 🏛️

### Mühendislik ve Doğa Bilimleri Fakültesi
- Bilgisayar Mühendisliği
- Yapay Zeka Mühendisliği
- Elektrik-Elektronik Mühendisliği
- Makine Mühendisliği
- İnşaat Mühendisliği
- Kimya Mühendisliği
- Çevre Mühendisliği
- Gıda Mühendisliği
- Endüstri Mühendisliği
- Mekatronik Mühendisliği
- Metalurji ve Malzeme Mühendisliği
- Polimer Mühendisliği
- Biyomühendislik
- Veri Bilimi
- Fizik
- Kimya
- Matematik

### Orman Fakültesi
- Orman Mühendisliği
- Orman Endüstri Mühendisliği

### İnsan ve Toplum Bilimleri Fakültesi
- İşletme
- İktisat
- Psikoloji
- Sosyoloji
- Uluslararası İlişkiler
- Uluslararası Ticaret ve Lojistik

### Mimarlık ve Tasarım Fakültesi
- Mimarlık
- Peyzaj Mimarlığı
- Şehir ve Bölge Planlama

### Diş Hekimliği Fakültesi
- Diş Hekimliği
- Genel Aile Hekimliği

## Installation 🛠️

### Prerequisites
- Python 3.8 or higher
- A Telegram Bot Token (get one from [@BotFather](https://t.me/botfather))

### Setup Steps

1. **Clone the repository**
   ```bash
   cd /home/halil/Desktop/repos/announcer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Edit the `.env` file and add your bot token:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. **Test the components** (optional)
   ```bash
   python test_components.py
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## Usage 📱

### For Users

1. **Start the bot**: Send `/start` to the bot
2. **Select department**: Choose your department from the keyboard menu
3. **Receive notifications**: Get automatic notifications for new announcements
4. **Manual check**: Use `/update` to manually check for new announcements
5. **View statistics**: Use `/stats` to see bot statistics
6. **Get help**: Use `/help` for assistance

### Bot Commands

- `/start` - Start the bot and select department
- `/update` - Manually check for new announcements
- `/stats` - View bot and user statistics
- `/help` - Show help message

## Project Structure 📁

```
btu_announcer_bot/
├── main.py                 # Main bot entry point
├── handlers/
│   ├── __init__.py
│   ├── commands.py         # Telegram command handlers
│   ├── scraper.py          # Web scraping functionality
│   ├── departments.py      # Department configuration
│   └── database.py         # Database operations
├── data/                   # Database and data files
│   ├── bot_data.json      # TinyDB database
│   └── last_sent.json     # Legacy tracking (if needed)
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── test_components.py     # Component testing script
└── README.md              # This file
```

## Technical Details 🔧

### Tech Stack
- **Python 3.8+**
- **python-telegram-bot**: Telegram Bot API
- **BeautifulSoup4**: Web scraping
- **TinyDB**: Lightweight database
- **requests**: HTTP requests
- **python-dotenv**: Environment variable management

### Features

#### Smart Web Scraping
- Robust scraping that handles different BTU website structures
- Multiple fallback selectors for announcement detection
- Error handling and retry logic
- Respects server resources with delays

#### Database Management
- User subscription tracking
- Announcement deduplication
- Automatic cleanup of old records
- Statistics tracking

#### Notification System
- Real-time announcement checking every 30 minutes
- Smart filtering to avoid duplicate notifications
- Formatted messages with titles, dates, and links
- Error handling for failed deliveries

## Configuration ⚙️

### Environment Variables
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Adding New Departments

To add a new department, edit `handlers/departments.py`:

```python
DEPARTMENTS = {
    # ... existing departments ...
    "New Department Name": {
        "url": "https://department.btu.edu.tr/announcements",
        "faculty": "Faculty Name"
    }
}
```

## Monitoring & Logs 📊

The bot creates detailed logs in `bot.log` including:
- User interactions
- Scraping activities
- Error tracking
- Performance metrics

## Development 👨‍💻

### Running Tests
```bash
python test_components.py
```

### Adding Features
1. Create new handlers in `handlers/` directory
2. Register handlers in `main.py`
3. Update database schema if needed
4. Add tests to `test_components.py`

### Debugging
- Check `bot.log` for detailed logs
- Use `/update` command for manual testing
- Run `test_components.py` to verify scraping

## Troubleshooting 🔧

### Common Issues

1. **Bot not responding**
   - Check if token is correct in `.env`
   - Verify internet connection
   - Check logs for errors

2. **No announcements received**
   - Use `/update` to test manually
   - Check if department website is accessible
   - Verify scraping logic with `test_components.py`

3. **Database errors**
   - Check write permissions in `data/` directory
   - Verify TinyDB installation

### Getting Help

1. Check the logs in `bot.log`
2. Run the test script: `python test_components.py`
3. Use `/help` command in the bot
4. Check GitHub issues

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Disclaimer ⚠️

This bot is an unofficial tool created to help BTÜ students. It is not affiliated with Bursa Technical University. Please respect the university's websites and use responsibly.
