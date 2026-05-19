from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from .utils import generate_location_link, extract_requester_id, calculate_distance_directions, get_address_from_coords

# Store pending location requests
pending_requests = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Main menu or link click"""
    args = context.args
    
    # Check if this is a link click (Person B receiving a request)
    if args:
        requester_id = extract_requester_id(args[0])
        if requester_id:
            # This is Person B - they need to share their location
            context.user_data['requester_id'] = int(requester_id)
            context.user_data['role'] = 'location_provider'
            
            keyboard = [[KeyboardButton("📍 ቦታዬን አጋራ", request_location=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                "🔔 የቦታ ጥያቄ ደርሶናል!\n\n"
                "አንድ ሰው የአሁኑን ቦታዎ እንዲያገኙ ጠይቀዋል።\n\n"
                "📍 ከዚህ በታች ያለውን ቁልፍ በመጫን ቦታዎን ያጋሩ።\n\n"
                "🔒 የሚከተሉት መረጃዎች ይላካሉ:\n"
                "• 🗺️ የጉግል ካርታ አገናኝ\n"
                "• 🚗 የመንገድ አቅጣጫዎች\n"
                "• 📏 ርቀት ስሌት\n\n"
                "እባክዎ ቁልፉን ይጫኑ:",
                reply_markup=reply_markup
            )
            return
    
    # Regular start - Main menu with 4 options
    keyboard = [
        [InlineKeyboardButton("📍 ቦታዬን አጋራ", callback_data="share_my_location")],
        [InlineKeyboardButton("🔗 የሰው ቦታ ለማግኘት", callback_data="request_location")],
        [InlineKeyboardButton("📊 የቦታ ታሪኬ", callback_data="location_history")],
        [InlineKeyboardButton("❓ እርዳታ", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 የቦታ መጠየቂያ ቦት\n\n"
        "📍 እንኳን ደህና መጡ!\n\n"
        "ምን ማድረግ ይፈልጋሉ?\n\n"
        "📍 ቦታዬን አጋራ - የአሁኑን ቦታዎ ለሌላ ሰው ይላኩ\n"
        "🔗 የሰው ቦታ ለማግኘት - የሌላ ሰው ቦታ ከመንገድ ጋር ይጠይቁ\n"
        "📊 የቦታ ታሪኬ - ያገኙዋቸውን ቦታዎች ይመልከቱ\n"
        "❓ እርዳታ - የአጠቃቀም መመሪያ\n\n"
        "አንዱን ይምረጡ:",
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "share_my_location":
        # User wants to share their location directly
        context.user_data['role'] = 'direct_sharer'
        
        keyboard = [[KeyboardButton("📍 የአሁኑን ቦታዬ አጋራ", request_location=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        # Send new message instead of editing
        await query.message.reply_text(
            "📍 ቦታዎን ያጋሩ\n\n"
            "ከዚህ በታች ያለውን ቁልፍ በመጫን የአሁኑን ቦታዎ ያጋሩ።\n\n"
            "ቦታዎን ካጋሩ በኋላ ለማን እንደሚልኩ መምረጥ ይችላሉ።",
            reply_markup=reply_markup
        )
        
        # Delete the original menu message
        await query.message.delete()
    
    elif query.data == "request_location":
        # Generate location request link
        bot_info = await context.bot.get_me()
        requester_id = update.effective_user.id
        
        # Generate unique link
        link = generate_location_link(bot_info.username, requester_id)
        
        # Store request info
        pending_requests[requester_id] = {
            'requester_id': requester_id,
            'status': 'waiting_for_location',
            'timestamp': query.message.date
        }
        
        keyboard = [
            [InlineKeyboardButton("📋 አገናኙን ቅዳ", callback_data="copy_link")],
            [InlineKeyboardButton("🔙 ወደ መጀመሪያ ምናሌ", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            f"✅ የቦታ ጥያቄ አገናኝ ተፈጥሯል!\n\n"
            f"📤 ይህን አገናኝ ለሰውዬው ይላኩ:\n\n"
            f"{link}\n\n"
            f"📋 መመሪያ:\n"
            f"1. ከላይ ያለውን አገናኝ ቅዳ\n"
            f"2. በቴሌግራም ለሰውዬው ይላኩ\n"
            f"3. እነሱ ሲጫኑ እና ቦታቸውን ሲያጋሩ እርስዎ የሚከተሉትን ያገኛሉ:\n"
            f"   • 📍 ትክክለኛ ቦታቸው\n"
            f"   • 🗺️ የጉግል ካርታ አገናኝ\n"
            f"   • 🚗 ወደ እነሱ የሚወስድ መንገድ\n"
            f"   • 📏 ትክክለኛ ርቀት\n\n"
            f"⏳ ቦታቸውን ሲያጋሩ በመጠባበቅ ላይ...\n\n"
            f"💡 ሲመልሱ በራስ-ሰር ማሳወቂያ ይደርስዎታል።",
            reply_markup=reply_markup
        )
    
    elif query.data == "copy_link":
        # Copy link instruction
        bot_info = await context.bot.get_me()
        requester_id = update.effective_user.id
        link = generate_location_link(bot_info.username, requester_id)
        
        await query.message.reply_text(
            f"📋 አገናኙ እነሆ:\n\n"
            f"{link}\n\n"
            f"💡 አገናኙን ተጭነው ይያዙ እና 'Copy' ን ይምረጡ\n\n"
            f"📤 ከዚያ ለሚፈልጉት ሰው ይላኩት።"
        )
    
    elif query.data == "location_history":
        # Show location history
        history = context.user_data.get('received_locations', [])
        if not history:
            await query.message.edit_text(
                "📊 የቦታ ታሪክ\n\n"
                "እስካሁን ምንም የቦታ ጥያቄዎች የሉም።\n\n"
                "አገናኝ ፈጥረው ለሰው ይላኩ ታሪክ እዚህ ይታያል!"
            )
        else:
            history_text = "📊 ያገኙዋቸው ቦታዎች\n\n"
            for i, loc in enumerate(reversed(history[-5:]), 1):
                history_text += f"{i}. 📍 ከ: {loc.get('provider_name', 'አንድ ሰው')}\n"
                history_text += f"   📏 ርቀት: {loc['distance']}\n"
                history_text += f"   🕐 ሰዓት: {loc['timestamp'].strftime('%H:%M:%S')}\n"
                history_text += f"   🗺️ ካርታ: {loc['map_url']}\n\n"
            
            keyboard = [[InlineKeyboardButton("🔙 ወደ መጀመሪያ ምናሌ", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(
                history_text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    
    elif query.data == "help":
        help_text = (
            "📖 የቦታ ቦት አጠቃቀም\n\n"
            "📍 ቦታዎን ለማጋራት:\n"
            "1. 'ቦታዬን አጋራ' ን ይጫኑ\n"
            "2. ቦታዎን ያጋሩ\n"
            "3. ለማን እንደሚልኩ ይምረጡ\n\n"
            "🔗 የሌላ ሰው ቦታ ለማግኘት:\n"
            "1. 'የሰው ቦታ ለማግኘት' ን ይጫኑ\n"
            "2. አገናኙን ቅዳ\n"
            "3. አገናኙን ለሰውዬው ይላኩ\n"
            "4. እነሱ ቦታቸውን ያጋራሉ\n"
            "5. እርስዎ ቦታ + መንገድ + ርቀት ያገኛሉ\n\n"
            "**ቦታ ለሚያጋራ ሰው:**\n"
            "1. የደረሰዎትን አገናኝ ይጫኑ\n"
            "2. 'ቦታዬን አጋራ' ን ይጫኑ\n"
            "3. ቦታዎ በራስ-ሰር ይላካል\n\n"
            "🔒 ግላዊነት: ቦታዎች ለጠየቀው ሰው ብቻ ይላካሉ።"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 ወደ መጀመሪያ ምናሌ", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            help_text,
            reply_markup=reply_markup
        )
    
    elif query.data == "main_menu":
        # Return to main menu
        keyboard = [
            [InlineKeyboardButton("📍 ቦታዬን አጋራ", callback_data="share_my_location")],
            [InlineKeyboardButton("🔗 የሰው ቦታ ለማግኘት", callback_data="request_location")],
            [InlineKeyboardButton("📊 የቦታ ታሪኬ", callback_data="location_history")],
            [InlineKeyboardButton("❓ እርዳታ", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text(
            "🤖 ዋና ምናሌ\n\n"
            "ምን ማድረግ ይፈልጋሉ?\n\n"
            "📍 ቦታዎን ለማጋራት ወይም የሌላ ሰው ቦታ ለመጠየቅ ከላይ ያሉትን ቁልፎች ይጠቀሙ።",
            reply_markup=reply_markup
        )
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shared location - For both direct sharing and responses"""
    location = update.message.location
    user_id = update.effective_user.id
    latitude = location.latitude
    longitude = location.longitude
    
    # Get address from coordinates
    address = await get_address_from_coords(latitude, longitude)
    map_url = f"https://www.google.com/maps?q={latitude},{longitude}"
    
    # Check if this is Person B responding to a request
    requester_id = context.user_data.get('requester_id')
    
    if requester_id:
        # This is Person B sharing location with Person A (requester)
        print(f"📍 Person B ({user_id}) sharing location with Person A ({requester_id})")
        
        try:
            # Store Person B's location (this is the target location)
            context.bot_data[f'target_location_{requester_id}'] = {
                'lat': latitude,
                'lon': longitude,
                'address': address,
                'name': update.effective_user.first_name,
                'map_url': map_url
            }
            
            # Send location to Person A (requester)
            await context.bot.send_location(
                chat_id=requester_id,
                latitude=latitude,
                longitude=longitude
            )
            
            # Send location info with automatic directions request
            await context.bot.send_message(
                chat_id=requester_id,
                text=f"📍 ቦታ ደርሶናል!\n\n"
                     f"👤 ከሰውዬው: {update.effective_user.first_name}\n"
                     f"🏠 አድራሻ: {address}\n\n"
                     f"🗺️ ካርታ: {map_url}\n\n"
                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                     f"🚗 መንገድ እና ርቀት ለማግኘት\n"
                     f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                     f"💡 የአሁኑን ቦታዎ ለማጋራት ከዚህ በታች ያለውን ቁልፍ ይጫኑ:"
            )
            
            # Create button for Person A to share their location
            share_keyboard = [[KeyboardButton("📍 የአሁኑን ቦታዬ አጋራ", request_location=True)]]
            share_markup = ReplyKeyboardMarkup(share_keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            # Send button to Person A
            await context.bot.send_message(
                chat_id=requester_id,
                text="🔘 ከዚህ በታች ባለው ቁልፍ በመጫን የአሁኑን ቦታዎ ያጋሩ እና ወደ እነሱ ያለውን ርቀት እና መንገድ ያግኙ!",
                reply_markup=share_markup
            )
            
            # Confirm to Person B
            await update.message.reply_text(
                f"✅ ቦታዎ ተልኳል!\n\n"
                f"🗺️ ካርታ: {map_url}\n\n"
                f"📍 ጠያቂው አሁን ቦታቸውን ሲያጋሩ ርቀቱን እና መንገዱን ያገኛሉ።",
                reply_markup=ReplyKeyboardRemove()
            )
            
            # Clear the requester_id
            context.user_data['requester_id'] = None
            
        except Exception as e:
            print(f"Error sending location: {e}")
            await update.message.reply_text("❌ ስህተት: ቦታ መላክ አልተቻለም")
    
    # Check if this is Person A sharing location to get directions
    elif context.bot_data.get(f'target_location_{user_id}'):
        # Person A is sharing their location to get directions to Person B
        target = context.bot_data[f'target_location_{user_id}']
        
        # Calculate directions - WITH AWAIT
        directions = await calculate_distance_directions(
            latitude, longitude,
            target['lat'], target['lon']
        )
        
        # Get address for Person A's location
        requester_address = await get_address_from_coords(latitude, longitude)
        
        # Send full directions with distance
        await update.message.reply_text(
            f"🚗 ወደ {target['name']} መንገድ እና ርቀት\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 የእርስዎ ቦታ:\n{requester_address[:80]}...\n\n"
            f"📍 የ{target['name']} ቦታ:\n{target['address'][:80]}...\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 የርቀት እና የጉዞ መረጃ:\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📏 ቀጥተኛ ርቀት: {directions['straight_distance_km']} ኪሜ\n"
            f"🚗 የመኪና ርቀት: {directions['distance_km']} ኪሜ ({directions['distance_miles']} ማይል)\n"
            f"⏱️ የሚገመት የመኪና ጊዜ: {directions['duration_min']} ደቂቃ\n"
            f"🕐 የሚገመት መድረሻ: {directions['eta']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🗺️ ዝርዝር መንገድ እና አቅጣጫ:\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 የጉግል ካርታ አገናኝ:\n{directions['map_url']}\n\n"
            f"🛣️ {directions['summary']}",
            disable_web_page_preview=True
        )
        
        # Send turn-by-turn directions if available
        if directions.get('steps') and len(directions['steps']) > 0:
            steps_text = "🚦 ዝርዝር የመንገድ አቅጣጫዎች:\n\n"
            for i, step in enumerate(directions['steps'][:8], 1):
                steps_text += f"{i}. {step}\n"
            
            if len(directions['steps']) > 8:
                steps_text += f"\n... እና {len(directions['steps']) - 8} ተጨማሪ እርምጃዎች"
            
            await update.message.reply_text(steps_text)
        
        # Clean up
        del context.bot_data[f'target_location_{user_id}']
        
        # Return to main menu
        keyboard = [[InlineKeyboardButton("🔙 ወደ መጀመሪያ ምናሌ", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ መንገድ እና ርቀት ዝግጁ ነው!\n\n"
            "ሌላ አገልግሎት ለማግኘት /start ይጫኑ",
            reply_markup=reply_markup
        )
    
    elif context.user_data.get('role') == 'direct_sharer':
        # Direct location sharing
        context.user_data['last_location'] = {
            'lat': latitude,
            'lon': longitude,
            'address': address,
            'map_url': map_url
        }
        
        await update.message.reply_text(
            f"📍 ቦታዎ ተይዟል!\n\n"
            f"🏠 አድራሻ: {address}\n\n"
            f"🗺️ ካርታ: {map_url}\n\n"
            f"📤 ለማን መላክ ይፈልጋሉ?\n\n"
            f"የቴሌግራም መለያውን ይጻፉ (ለምሳሌ: username)\n\n"
            f"ለመሰረዝ /cancel ይጻፉ",
            reply_markup=ReplyKeyboardRemove()
        )
        
        context.user_data['awaiting_recipient'] = True
    
    else:
        # Default - just show location
        keyboard = [[InlineKeyboardButton("🔙 ወደ መጀመሪያ ምናሌ", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📍 ቦታ ተይዟል!\n\n"
            f"🏠 {address}\n\n"
            f"🗺️ {map_url}",
            reply_markup=reply_markup
        )
        
        
async def handle_recipient_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle recipient username for direct location sharing"""
    if not context.user_data.get('awaiting_recipient'):
        return
    
    recipient_input = update.message.text.strip()
    context.user_data['awaiting_recipient'] = False
    
    last_location = context.user_data.get('last_location')
    if not last_location:
        await update.message.reply_text("❌ ቦታ አልተገኘም. እንደገና ይሞክሩ")
        return
    
    # Parse recipient
    if recipient_input.startswith('@'):
        recipient_input = recipient_input[1:]
    
    try:
        # Try to get user by username
        recipient = await context.bot.get_chat(f"@{recipient_input}")
        recipient_id = recipient.id
        
        # Send location
        await context.bot.send_location(
            chat_id=recipient_id,
            latitude=last_location['lat'],
            longitude=last_location['lon']
        )
        
        await context.bot.send_message(
            chat_id=recipient_id,
            text=f"📍 አንድ ሰው ቦታውን አጋርቶልዎታል!\n\n"
                 f"🏠 {last_location['address']}\n\n"
                 f"🗺️ ካርታ: {last_location['map_url']}"
        )
        
        await update.message.reply_text(
            f"✅ ቦታዎ ተልኳል!\n\n"
            f"📍 ለ: {recipient_input}\n"
            f"🗺️ ካርታ: {last_location['map_url']}"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ ስህተት: ተጠቃሚ '{recipient_input}' አልተገኘም\n\nእባክዎ ትክክለኛ የቴሌግራም መለያ ይጻፉ")

async def handle_directions_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when Person A shares location to get directions to Person B"""
    location = update.message.location
    requester_id = update.effective_user.id
    requester_lat = location.latitude
    requester_lon = location.longitude
    
    # Get Person B's stored location
    target_location = context.bot_data.get(f'directions_target_{requester_id}')
    
    if not target_location:
        await update.message.reply_text(
            "❌ ምንም የቦታ ጥያቄ አልተገኘም።\n\n"
            "እባክዎ አዲስ የቦታ ጥያቄ ይፍጠሩ።",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Calculate directions - WITH AWAIT
    directions = await calculate_distance_directions(
        requester_lat, requester_lon,
        target_location['lat'], target_location['lon']
    )
    
    # Get address for Person A's location
    requester_address = await get_address_from_coords(requester_lat, requester_lon)
    
    # Send directions to Person A (requester)
    await update.message.reply_text(
        f"🚗 ወደ {target_location['provider_name']} መንገድ\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 የእርስዎ ቦታ: {requester_address[:100]}...\n\n"
        f"📍 የእነሱ ቦታ: {target_location['address'][:100]}...\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 የጉዞ ማጠቃለያ:\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📏 ርቀት: {directions['distance_km']} ኪሜ ({directions['distance_miles']} ማይል)\n"
        f"⏱️ የሚገመት ጊዜ: {directions['duration_min']} ደቂቃ\n"
        f"🚗 የሚገመት መድረሻ: {directions['eta']}\n\n"
        f"🗺️ የጉግል ካርታ አገናኝ:\n{directions['map_url']}\n\n"
        f"🛣️ ማጠቃለያ: {directions['summary']}",
        disable_web_page_preview=True
    )
    
    # Send turn-by-turn instructions
    if directions.get('steps'):
        steps_text = "🚦 ዝርዝር መንገድ:\n\n"
        for i, step in enumerate(directions['steps'][:5], 1):
            steps_text += f"{i}. {step}\n"
        
        await update.message.reply_text(steps_text)
    
    # Clean up
    del context.bot_data[f'directions_target_{requester_id}']
    
    # Return to main menu
    keyboard = [[InlineKeyboardButton("🔙 ወደ መጀመሪያ ምናሌ", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "✅ መንገድ ዝግጁ ነው!\n\n/start በመጠቀም እንደገና ይጀምሩ።",
        reply_markup=reply_markup
    )
async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ ተሰርዟል።\n\n/start በመጠቀም እንደገና ይጀምሩ።",
        reply_markup=ReplyKeyboardRemove()
    )