import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from .utils import generate_location_link, extract_requester_id, calculate_distance_directions, get_address_from_coords

logger = logging.getLogger(__name__)

# Store pending location requests
pending_requests = {}

# Language translations (simplified for testing)
TEXTS = {
    'am': {
        'share_location_btn': "📍 ቦታዬን አጋራ",
        'get_location_btn': "🔗 የሰው ቦታ ለማግኘት",
        'history_btn': "📊 የቦታ ታሪኬ",
        'help_btn': "❓ እርዳታ",
        'back_btn': "🔙 ወደ መጀመሪያ ምናሌ",
        'copy_link_btn': "📋 አገናኙን ቅዳ",
        'share_now_btn': "📍 የአሁኑን ቦታዬ አጋራ",
        'welcome': "🤖 የቦታ መጠየቂያ ቦት\n\n📍 እንኳን ደህና መጡ!\n\nምን ማድረግ ይፈልጋሉ?",
        'share_prompt': "📍 ቦታዎን ያጋሩ\n\nከዚህ በታች ያለውን ቁልፍ በመጫን የአሁኑን ቦታዎ ያጋሩ።",
    },
    'en': {
        'share_location_btn': "📍 Share My Location",
        'get_location_btn': "🔗 Get Someone's Location",
        'history_btn': "📊 Location History",
        'help_btn': "❓ Help",
        'back_btn': "🔙 Back to Main Menu",
        'copy_link_btn': "📋 Copy Link",
        'share_now_btn': "📍 Share My Current Location",
        'welcome': "🤖 Location Request Bot\n\n📍 Welcome!\n\nWhat would you like to do?",
        'share_prompt': "📍 Share your location\n\nTap the button below to share your current location.",
    }
}

def get_user_language(context):
    return context.user_data.get('language', 'am')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    logger.info(f"Start command received from user {update.effective_user.id}")
    
    args = context.args
    
    # Initialize language if not set
    if 'language' not in context.user_data:
        keyboard = [
            [InlineKeyboardButton("አማርኛ", callback_data="lang_am")],
            [InlineKeyboardButton("English", callback_data="lang_en")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🌐 Please select your language / ቋንቋ ይምረጡ:",
            reply_markup=reply_markup
        )
        return
    
    # Check if this is a location request link click
    if args:
        requester_id = extract_requester_id(args[0])
        if requester_id:
            context.user_data['requester_id'] = int(requester_id)
            context.user_data['role'] = 'location_provider'
            
            lang = get_user_language(context)
            texts = TEXTS[lang]
            
            keyboard = [[KeyboardButton(texts['share_now_btn'], request_location=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            share_text_am = "🔔 የቦታ ጥያቄ ደርሶናል!\n\nአንድ ሰው የአሁኑን ቦታዎ እንዲያገኙ ጠይቀዋል።\n\n📍 ከዚህ በታች ያለውን ቁልፍ በመጫን ቦታዎን ያጋሩ።"
            share_text_en = "🔔 Location request received!\n\nSomeone has asked for your current location.\n\n📍 Tap the button below to share your location."
            share_text = share_text_am if lang == 'am' else share_text_en
            
            await update.message.reply_text(share_text, reply_markup=reply_markup)
            return
    
    # Regular start - Show main menu
    lang = get_user_language(context)
    texts = TEXTS[lang]
    
    keyboard = [
        [InlineKeyboardButton(texts['share_location_btn'], callback_data="share_my_location")],
        [InlineKeyboardButton(texts['get_location_btn'], callback_data="request_location")],
        [InlineKeyboardButton(texts['history_btn'], callback_data="location_history")],
        [InlineKeyboardButton(texts['help_btn'], callback_data="help")],
        [InlineKeyboardButton("🌐 Change Language / ቋንቋ ቀይር", callback_data="change_language")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(texts['welcome'], reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    logger.info(f"🔥🔥🔥 CALLBACK RECEIVED: {query.data} 🔥🔥🔥")  # ADD THIS LINE
    logger.info(f"📱 Callback received: {query.data} from user {update.effective_user.id}")
    
    await query.answer()
    
    # Handle language selection
    if query.data == "change_language":
        keyboard = [
            [InlineKeyboardButton("አማርኛ", callback_data="lang_am")],
            [InlineKeyboardButton("English", callback_data="lang_en")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(
            "🌐 Please select your language / ቋንቋ ይምረጡ:",
            reply_markup=reply_markup
        )
        return
    
    if query.data.startswith("lang_"):
        lang = query.data.split('_')[1]
        context.user_data['language'] = lang
        texts = TEXTS[lang]
        
        keyboard = [
            [InlineKeyboardButton(texts['share_location_btn'], callback_data="share_my_location")],
            [InlineKeyboardButton(texts['get_location_btn'], callback_data="request_location")],
            [InlineKeyboardButton(texts['history_btn'], callback_data="location_history")],
            [InlineKeyboardButton(texts['help_btn'], callback_data="help")],
            [InlineKeyboardButton("🌐 Change Language / ቋንቋ ቀይር", callback_data="change_language")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(texts['welcome'], reply_markup=reply_markup)
        return
    
    # Handle main menu buttons
    lang = get_user_language(context)
    texts = TEXTS[lang]
    
    if query.data == "share_my_location":
        logger.info("📍 Share location button clicked")
        context.user_data['role'] = 'direct_sharer'
        
        keyboard = [[KeyboardButton(texts['share_now_btn'], request_location=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await query.message.reply_text(texts['share_prompt'], reply_markup=reply_markup)
        await query.message.delete()
    
    elif query.data == "request_location":
        logger.info("🔗 Request location button clicked")
        bot_info = await context.bot.get_me()
        requester_id = update.effective_user.id
        link = generate_location_link(bot_info.username, requester_id)
        
        keyboard = [
            [InlineKeyboardButton(texts['copy_link_btn'], callback_data="copy_link")],
            [InlineKeyboardButton(texts['back_btn'], callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            f"✅ Share this link with the person:\n\n{link}\n\nThey will share their location with you.",
            reply_markup=reply_markup
        )
    
    elif query.data == "copy_link":
        bot_info = await context.bot.get_me()
        requester_id = update.effective_user.id
        link = generate_location_link(bot_info.username, requester_id)
        await query.message.reply_text(f"📋 Link: {link}")
    
    elif query.data == "location_history":
        await query.message.edit_text("📊 Location history feature coming soon!")
    
    elif query.data == "help":
        help_text = "📖 Help:\n\n1. Share Location - Send your location to someone\n2. Get Location - Request someone's location\n3. History - View past locations"
        keyboard = [[InlineKeyboardButton(texts['back_btn'], callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(help_text, reply_markup=reply_markup)
    
    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton(texts['share_location_btn'], callback_data="share_my_location")],
            [InlineKeyboardButton(texts['get_location_btn'], callback_data="request_location")],
            [InlineKeyboardButton(texts['history_btn'], callback_data="location_history")],
            [InlineKeyboardButton(texts['help_btn'], callback_data="help")],
            [InlineKeyboardButton("🌐 Change Language / ቋንቋ ቀይር", callback_data="change_language")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(texts['welcome'], reply_markup=reply_markup)

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shared location"""
    logger.info(f"📍 Location received from user {update.effective_user.id}")
    location = update.message.location
    
    await update.message.reply_text(
        f"✅ Location received!\n\n"
        f"Latitude: {location.latitude}\n"
        f"Longitude: {location.longitude}\n\n"
        f"📍 Google Maps: https://www.google.com/maps?q={location.latitude},{location.longitude}"
    )

async def handle_recipient_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle recipient input"""
    logger.info(f"📝 Text received from user {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text("Feature coming soon!")

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled. Use /start to begin again.", reply_markup=ReplyKeyboardRemove())