# 🤖 Telegram Location Bot

A powerful Telegram bot that enables users to share their location, request locations from others, and get accurate distance calculations and turn-by-turn directions.

## ✨ Features

### 📍 Location Sharing
- **Share your location directly** - Click a button to send your current location to anyone
- **Request location from others** - Generate a unique link and send it to anyone
- **Real-time feedback** - Get instant confirmation when location is received

### 🗺️ Navigation & Directions
- **Turn-by-turn directions** - Detailed step-by-step navigation instructions
- **Distance calculation** - Straight-line distance (Haversine formula) and driving distance
- **ETA estimation** - Accurate arrival time predictions
- **Map integration** - Direct links to Google Maps for full navigation

### 📊 Additional Features
- **Location history** - View your last 5 received location requests
- **Address geocoding** - Automatic address extraction from coordinates
- **Multi-user support** - Perfect for groups, meetups, and business coordination
- **Bilingual interface** - Amharic and English language support
- **Privacy-focused** - Locations are shared directly between users, not stored on servers

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from @BotFather)

### Installation

1. **Clone or download the project**
   ```bash
   cd telegrambot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables**
   Create a `.env` file in the `src/` directory:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

### Configuration

Create a bot via [@BotFather](https://t.me/botfather) and follow these steps:

1. Create a new bot and get your token
2. Set the bot commands:
   - `/start` - Start/Restart the bot
   - `/cancel` - Cancel current operation
3. Set a descriptive bot name and description

## 📖 How It Works

### Scenario 1: Sharing Your Location
1. Click "📍 ቦታዬን አጋራ" (Share My Location)
2. Allow location access on your device
3. Choose who to share with (by username or receive their location)
4. Share your location!

### Scenario 2: Requesting Someone's Location
1. Click "🔗 የሰው ቦታ ለማግኘት" (Request Location)
2. Copy the generated link
3. Send it to the person you want to locate
4. They click the link and share their location
5. You receive:
   - Their exact coordinates
   - Full address
   - Google Maps link
   - Turn-by-turn directions to them
   - Distance and ETA

### Scenario 3: Getting Directions
1. Someone requests your location
2. They share their location
3. You share your location
4. You instantly receive:
   - Distance to them (straight-line and driving)
   - Estimated travel time
   - Turn-by-step navigation
   - Google Maps route

## 🔧 Technical Details

### Architecture
- **Language**: Python 3.8+
- **Framework**: python-telegram-bot v21+
- **Async/Await**: Fully asynchronous operations
- **APIs Used**:
  - OpenStreetMap Nominatim (reverse geocoding)
  - OSRM (Open Source Routing Machine) (route planning)
  - Google Maps (direction links)

### Key Components

#### Main Entry Point (`main.py`)
- Initializes the Telegram application
- Registers command and message handlers
- Sets up bot menu commands
- Handles polling for updates

#### Handlers (`src/handlers.py`)
- `start()` - Main menu and link handling
- `handle_callback()` - Button click navigation
- `handle_location()` - Location sharing and direction requests
- `handle_directions_request()` - Direction calculation flow
- `handle_cancel()` - Cancel current operations

#### Utilities (`src/utils.py`)
- `generate_location_link()` - Creates unique request links
- `get_address_from_coords()` - Reverse geocoding
- `calculate_distance_directions()` - Route calculation with OSRM
- `calculate_haversine_distance()` - Geometric distance formula
- `calculate_eta()` - Time estimation

## 📁 Project Structure

```
telegrambot/
├── main.py                 # Entry point
├── requirements.txt       # Python dependencies
├── .env                    # Environment variables (create this)
└── src/
    ├── handlers.py        # Bot command handlers
    └── utils.py           # Utility functions
```

## 🛡️ Privacy & Security

- **No server-side storage** - User data is processed in memory
- **Location privacy** - Locations are sent directly between users
- **Session management** - Temporary storage that expires on cancel
- **HTTPS communication** - All API calls use secure protocols

## 🚧 Limitations

- Requires user's explicit permission to share location
- Internet connection required for maps and routing
- OSRM API may have rate limits for large-scale use
- Reverse geocoding depends on OpenStreetMap data availability

## 🐛 Troubleshooting

### Bot not responding
- Verify BOT_TOKEN is set correctly
- Check if bot is running (`python main.py`)
- Ensure no firewall blocking the application

### Location not sharing
- Allow location permissions on your device
- Check Telegram location permissions
- Verify the recipient exists and has Telegram

### Directions not showing
- OSRM API might be temporarily unavailable
- Check your internet connection
- Try refreshing the page

## 📝 Usage Examples

### Code Integration Example
```python
from telegram.ext import ApplicationBuilder

# Initialize bot with your token
app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()

# Add handlers
app.add_handler(CommandHandler("start", start))

# Run
app.run_polling()
```

### API Integration Example
```python
from src.utils import calculate_distance_directions

# Calculate distance between two points
directions = await calculate_distance_directions(
    from_lat=9.0152, from_lon=40.4897,  # Addis Ababa coordinates
    to_lat=9.0266, to_lon=38.7623        # Bole International Airport
)

print(f"Distance: {directions['distance_km']} km")
print(f"Duration: {directions['duration_min']} minutes")
print(f"Map URL: {directions['map_url']}")
```

## 🔄 Updates & Maintenance

To update the bot:
1. Pull the latest changes
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Restart the bot: `python main.py`

## 📄 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📞 Support

For support or questions:
- Check the troubleshooting section
- Review the code documentation
- Contact the development team

---

**Made with ❤️ using Python and the Telegram API**