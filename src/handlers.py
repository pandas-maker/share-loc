import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from .utils import generate_location_link, extract_requester_id, calculate_distance_directions, get_address_from_coords

logger = logging.getLogger(__name__)

# Store pending location requests
pending_requests = {}

# Language translations
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
        'request_link_text': "✅ የቦታ ጥያቄ አገናኝ ተፈጥሯል!\n\n📤 ይህን አገናኝ ለሰውዬው ይላኩ:\n\n{link}\n\n📋 መመሪያ:\n1. አገናኙን ቅዳ\n2. በቴሌግራም ለሰውዬው ይላኩ\n3. እነሱ ቦታቸውን ሲያጋሩ መንገድ እና ርቀት ያገኛሉ",
        'help_text': "📖 የቦታ ቦት አጠቃቀም\n\n📍 ቦታዎን ለማጋራት:\n1. 'ቦታዬን አጋራ' ን ይጫኑ\n2. ቦታዎን ያጋሩ\n3. ለማን እንደሚልኩ ይምረጡ\n\n🔗 የሌላ ሰው ቦታ ለማግኘት:\n1. 'የሰው ቦታ ለማግኘት' ን ይጫኑ\n2. አገናኙን ቅዳ\n3. ለሰውዬው ይላኩ\n4. እነሱ ቦታቸውን ሲያጋሩ መንገድ እና ርቀት ያገኛሉ",
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
        'request_link_text': "✅ Location request link created!\n\n📤 Send this link to the person:\n\n{link}\n\n📋 Instructions:\n1. Copy the link\n2. Send it on Telegram\n3. When they share their location, you'll get directions and distance",
        'help_text': "📖 How to use the Location Bot\n\n📍 To share your location:\n1. Tap 'Share My Location'\n2. Share your location\n3. Choose who to send it to\n\n🔗 To get someone's location:\n1. Tap 'Get Someone's Location'\n2. Copy the link\n3. Send it to the person\n4. When they share their location, you'll get directions and distance",
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
        
        pending_requests[requester_id] = {
            'requester_id': requester_id,
            'status': 'waiting_for_location',
            'timestamp': query.message.date
        }
        
        keyboard = [
            [InlineKeyboardButton(texts['copy_link_btn'], callback_data="copy_link")],
            [InlineKeyboardButton(texts['back_btn'], callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            texts['request_link_text'].format(link=link),
            reply_markup=reply_markup
        )
    
    elif query.data == "copy_link":
        bot_info = await context.bot.get_me()
        requester_id = update.effective_user.id
        link = generate_location_link(bot_info.username, requester_id)
        
        copy_text_am = f"📋 አገናኙ እነሆ:\n\n{link}\n\n💡 አገናኙን ተጭነው ይያዙ እና 'Copy' ን ይምረጡ"
        copy_text_en = f"📋 Here's the link:\n\n{link}\n\n💡 Press and hold the link, then select 'Copy'"
        copy_text = copy_text_am if lang == 'am' else copy_text_en
        
        await query.message.reply_text(copy_text)
    
    elif query.data == "location_history":
        history = context.user_data.get('received_locations', [])
        if not history:
            history_text_am = "📊 የቦታ ታሪክ\n\nእስካሁን ምንም የቦታ ጥያቄዎች የሉም።"
            history_text_en = "📊 Location History\n\nNo location requests yet."
            history_text = history_text_am if lang == 'am' else history_text_en
            await query.message.edit_text(history_text)
        else:
            history_text_am = "📊 ያገኙዋቸው ቦታዎች\n\n"
            history_text_en = "📊 Locations received\n\n"
            history_text = history_text_am if lang == 'am' else history_text_en
            
            for i, loc in enumerate(reversed(history[-5:]), 1):
                if lang == 'am':
                    history_text += f"{i}. 📍 ከ: {loc.get('provider_name', 'አንድ ሰው')}\n"
                    history_text += f"   📏 ርቀት: {loc.get('distance', 'N/A')}\n"
                else:
                    history_text += f"{i}. 📍 From: {loc.get('provider_name', 'Someone')}\n"
                    history_text += f"   📏 Distance: {loc.get('distance', 'N/A')}\n"
            
            keyboard = [[InlineKeyboardButton(texts['back_btn'], callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(history_text, reply_markup=reply_markup, disable_web_page_preview=True)
    
    elif query.data == "help":
        keyboard = [[InlineKeyboardButton(texts['back_btn'], callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text(texts['help_text'], reply_markup=reply_markup)
    
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
    user_id = update.effective_user.id
    lang = get_user_language(context)
    texts = TEXTS[lang]
    
    latitude = location.latitude
    longitude = location.longitude
    
    address = await get_address_from_coords(latitude, longitude)
    map_url = f"https://www.google.com/maps?q={latitude},{longitude}"
    
    requester_id = context.user_data.get('requester_id')
    
    if requester_id:
        # Person B sharing location with Person A (requester)
        try:
            context.bot_data[f'target_location_{requester_id}'] = {
                'lat': latitude, 'lon': longitude, 'address': address,
                'name': update.effective_user.first_name, 'map_url': map_url
            }
            
            await context.bot.send_location(chat_id=requester_id, latitude=latitude, longitude=longitude)
            
            response_am = f"📍 ቦታ ደርሶናል!\n\n👤 ከ: {update.effective_user.first_name}\n🏠 {address}\n\n🗺️ {map_url}"
            response_en = f"📍 Location received!\n\n👤 From: {update.effective_user.first_name}\n🏠 {address}\n\n🗺️ {map_url}"
            response = response_am if lang == 'am' else response_en
            
            await context.bot.send_message(chat_id=requester_id, text=response)
            
            # Create button for Person A to share their location for directions
            share_keyboard = [[KeyboardButton("📍 Share my location for directions", request_location=True)]]
            share_markup = ReplyKeyboardMarkup(share_keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await context.bot.send_message(
                chat_id=requester_id,
                text="To get directions and distance to this person, share your location using the button below:",
                reply_markup=share_markup
            )
            
            confirm_am = f"✅ ቦታዎ ተልኳል!\n\n🗺️ {map_url}"
            confirm_en = f"✅ Your location has been sent!\n\n🗺️ {map_url}"
            confirm = confirm_am if lang == 'am' else confirm_en
            
            await update.message.reply_text(confirm, reply_markup=ReplyKeyboardRemove())
            context.user_data['requester_id'] = None
            
        except Exception as e:
            logger.error(f"Error sending location: {e}")
            await update.message.reply_text(f"{texts['error']}: {e}")
    
    elif context.bot_data.get(f'target_location_{user_id}'):
        # Person A sharing their location to get directions to Person B
        target = context.bot_data[f'target_location_{user_id}']
        
        directions = await calculate_distance_directions(latitude, longitude, target['lat'], target['lon'])
        
        await update.message.reply_text(
            f"🚗 Directions to {target['name']}\n\n"
            f"📏 Distance: {directions['distance_km']} km ({directions['distance_miles']} miles)\n"
            f"⏱️ Estimated time: {directions['duration_min']} minutes\n"
            f"🗺️ Google Maps: {directions['map_url']}\n\n"
            f"📍 Your location: {address[:100]}...\n"
            f"📍 Their location: {target['address'][:100]}...",
            disable_web_page_preview=True
        )
        
        del context.bot_data[f'target_location_{user_id}']
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("✅ Directions sent!", reply_markup=reply_markup)
    
    elif context.user_data.get('role') == 'direct_sharer':
        context.user_data['last_location'] = {'lat': latitude, 'lon': longitude, 'address': address, 'map_url': map_url}
        
        prompt_am = f"📍 {address[:100]}...\n\n📤 ለማን መላክ ይፈልጋሉ?\n\nየቴሌግራም መለያውን ይጻፉ\n\nለመሰረዝ /cancel"
        prompt_en = f"📍 {address[:100]}...\n\n📤 Who would you like to send this location to?\n\nEnter their Telegram username\n\nTo cancel, type /cancel"
        prompt = prompt_am if lang == 'am' else prompt_en
        
        await update.message.reply_text(prompt, reply_markup=ReplyKeyboardRemove())
        context.user_data['awaiting_recipient'] = True
    else:
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        location_text_am = f"📍 ቦታ ተይዟል!\n\n🏠 {address}\n\n🗺️ {map_url}"
        location_text_en = f"📍 Location received!\n\n🏠 {address}\n\n🗺️ {map_url}"
        location_text = location_text_am if lang == 'am' else location_text_en
        
        await update.message.reply_text(location_text, reply_markup=reply_markup)

async def handle_recipient_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle recipient username for direct location sharing"""
    if not context.user_data.get('awaiting_recipient'):
        return
    
    lang = get_user_language(context)
    texts = TEXTS[lang]
    
    recipient_input = update.message.text.strip()
    context.user_data['awaiting_recipient'] = False
    
    if recipient_input.lower() == '/cancel':
        await handle_cancel(update, context)
        return
    
    last_location = context.user_data.get('last_location')
    if not last_location:
        await update.message.reply_text(f"{texts['error']}. Please try again.")
        return
    
    if recipient_input.startswith('@'):
        recipient_input = recipient_input[1:]
    
    try:
        recipient = await context.bot.get_chat(f"@{recipient_input}")
        
        await context.bot.send_location(
            chat_id=recipient.id,
            latitude=last_location['lat'],
            longitude=last_location['lon']
        )
        
        sent_am = f"✅ ቦታዎ ተልኳል!\n\n📍 ለ: {recipient_input}\n🗺️ {last_location['map_url']}"
        sent_en = f"✅ Location sent!\n\n📍 To: {recipient_input}\n🗺️ {last_location['map_url']}"
        sent = sent_am if lang == 'am' else sent_en
        
        await update.message.reply_text(sent)
        
        context.user_data.pop('last_location', None)
        
    except Exception as e:
        error_am = f"❌ ስህተት: '{recipient_input}' አልተገኘም\n\nእባክዎ ትክክለኛ መለያ ይጻፉ"
        error_en = f"❌ Error: '{recipient_input}' not found\n\nPlease enter a valid username"
        error = error_am if lang == 'am' else error_en
        
        await update.message.reply_text(error)
        context.user_data['awaiting_recipient'] = True

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    lang = get_user_language(context)
    texts = TEXTS[lang]
    
    context.user_data.clear()
    await update.message.reply_text(texts['cancel'], reply_markup=ReplyKeyboardRemove())