from pyrogram import filters, Client, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Modules import teleshop_bot, LOG_GROUP
from database import fetch_group_listings
import time

# Helper to format group info
async def format_group(group, idx, total):
    from database import get_user_rating
    import string
    import random
    
    # Get seller rating
    seller_id = group.get('seller_id', 0)
    if seller_id:
        rating_info = await get_user_rating(seller_id)
        if rating_info['total_ratings'] > 0:
            rating_stars = "⭐" * int(rating_info['average_rating'])
            rating_display = f"{rating_stars} ({rating_info['average_rating']:.1f}/5)"
        else:
            rating_display = "No ratings yet"
    else:
        rating_display = "No ratings yet"
    
    # Generate consistent anonymous seller ID based on seller_id and group_id
    def generate_consistent_seller_id(seller_id, group_id):
        """Generate a consistent 10-character anonymous seller identifier"""
        # Use seller_id and group_id as seed for consistency
        random.seed(f"{seller_id}_{group_id}")
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=10))
    
    anonymous_seller_id = generate_consistent_seller_id(seller_id, group.get('group_id', 0))
    
    return (
        f"📝 **Group {idx+1} of {total}:**\n\n"
        f"**Group Name:** {group.get('name', 'N/A')}\n"
        f"• Members: {group.get('members', 'N/A')}\n"
        f"• Niche: {group.get('niche', 'N/A')}\n"
        f"• Price: {group.get('price', 'N/A')}\n"
        f"• Seller: `{anonymous_seller_id}`\n"
        f"• Seller Rating: {rating_display}\n"
        f"{'• ' + group.get('notes', '') if group.get('notes') else ''}"
    )

# Entry point: show first group
@teleshop_bot.on_message(filters.command(["buy"]) & filters.private)
async def buy_command(client: Client, message: Message):
    try:
        # Use filtered listings based on user settings
        from database import fetch_filtered_group_listings
        groups = await fetch_filtered_group_listings(message.from_user.id)
        
        # Ensure groups is a list
        if groups is None:
            groups = []
        
        # Filter out groups that belong to the current user
        user_id = message.from_user.id
        available_groups = [
            group for group in groups 
            if group.get('seller_id') != user_id
        ]
        
        if not available_groups or len(available_groups) == 0:
            # Check if user has their own listings
            user_groups = [group for group in groups if group.get('seller_id') == user_id]
            if user_groups:
                await message.reply_text(
                    "❌ No groups match your current filters.\n\n"
                    f"📝 You have {len(user_groups)} group(s) listed for sale.\n"
                    "💡 Try adjusting your filters in /settings or browse without filters!"
                )
            else:
                await message.reply_text(
                    "❌ No groups match your current filters.\n\n"
                    "💡 Try adjusting your filters in /settings to see more results!"
                )
            return

        # Use filtered groups
        groups = available_groups
        idx = 0
        total = len(groups)
        group = groups[idx]
        kb = []
        
        # Navigation buttons
        if total > 1:
            kb.append([
                InlineKeyboardButton("⬅️ Back", callback_data=f"buy_back_{idx}"),
                InlineKeyboardButton("➡️ Next", callback_data=f"buy_next_{idx}")
            ])
        
        # Seller reputation button
        kb.append([
            InlineKeyboardButton("👤 Seller Reputation", callback_data=f"seller_reputation_{group.get('seller_id', 0)}")
        ])
        
        # Accept Deal button
        kb.append([
            InlineKeyboardButton("✅ Accept Deal", callback_data=f"accept_deal_{group.get('group_id', '')}_{group.get('seller_id', '')}")
        ])
        
        # Add settings reminder if filters are active
        from database import get_user_settings
        user_settings = await get_user_settings(user_id)
        has_filters = any([
            user_settings.get('min_seller_rating'),
            user_settings.get('max_price'),
            user_settings.get('min_price'),
            user_settings.get('creation_year_filter'),
            user_settings.get('min_members')
        ])
        
        formatted_group = await format_group(group, idx, total)
        
        # Add filter info if active
        if has_filters:
            filter_info = "\n\n🔍 **Filters active** - Use /settings to modify"
            formatted_group += filter_info
        
        await message.reply_text(
            formatted_group,
            reply_markup=InlineKeyboardMarkup(kb) if kb else None
        )
        
    except Exception as e:
        print(f"Error in buy_command: {e}")
        await message.reply_text(
            "❌ Error loading group listings. Please try again later."
        )

# Callback for next/back navigation
@teleshop_bot.on_callback_query(filters.regex(r"^buy_(next|back)_(\d+)"))
async def buy_pagination_callback(client: Client, callback_query):
    try:
        action, idx = callback_query.data.split('_')[1:]
        idx = int(idx)
        groups = await fetch_group_listings()
        
        # Ensure groups is a list
        if groups is None:
            groups = []
        
        # Filter out groups that belong to the current user
        user_id = callback_query.from_user.id
        available_groups = [
            group for group in groups 
            if group.get('seller_id') != user_id
        ]
        
        if not available_groups or len(available_groups) == 0:
            await callback_query.answer("No groups available for purchase.", show_alert=True)
            return
        
        # Use filtered groups
        groups = available_groups
        total = len(groups)
        
        if action == "next":
            idx = (idx + 1) % total
        elif action == "back":
            idx = (idx - 1 + total) % total

        group = groups[idx]
        kb = []
        
        # Navigation buttons
        if total > 1:
            kb.append([
                InlineKeyboardButton("⬅️ Back", callback_data=f"buy_back_{idx}"),
                InlineKeyboardButton("➡️ Next", callback_data=f"buy_next_{idx}")
            ])
        
        # Seller reputation button
        kb.append([
            InlineKeyboardButton("👤 Seller Reputation", callback_data=f"seller_reputation_{group.get('seller_id', 0)}")
        ])
        
        # Accept Deal button
        kb.append([
            InlineKeyboardButton("✅ Accept Deal", callback_data=f"accept_deal_{group.get('group_id', '')}_{group.get('seller_id', '')}")
        ])
        
        formatted_group = await format_group(group, idx, total)
        await callback_query.message.edit_text(
            formatted_group,
            reply_markup=InlineKeyboardMarkup(kb) if kb else None
        )
        await callback_query.answer()
        
    except Exception as e:
        print(f"Error in buy_pagination_callback: {e}")
        await callback_query.answer("❌ Error loading groups!", show_alert=True)

# Handle seller reputation view
@teleshop_bot.on_callback_query(filters.regex(r"^seller_reputation_(\d+)"))
async def seller_reputation_callback(client: Client, callback_query):
    try:
        seller_id = int(callback_query.data.split('_')[2])
        
        from database import get_user_rating, get_user_sales_history
        rating_info = await get_user_rating(seller_id)
        sales_history = await get_user_sales_history(seller_id)
        
        # Calculate reputation metrics
        total_sales = len(sales_history)
        
        if rating_info['total_ratings'] > 0:
            rating_stars = "⭐" * int(rating_info['average_rating'])
            reputation_level = "Excellent" if rating_info['average_rating'] >= 4.5 else \
                             "Good" if rating_info['average_rating'] >= 4.0 else \
                             "Average" if rating_info['average_rating'] >= 3.0 else \
                             "Poor"
        else:
            rating_stars = ""
            reputation_level = "New Seller"
        
        reputation_text = (
            f"👤 **Seller Reputation**\n\n"
            f"**Overall Rating:** {rating_info['average_rating']:.1f}/5.0 {rating_stars}\n"
            f"**Total Reviews:** {rating_info['total_ratings']}\n"
            f"**Reputation Level:** {reputation_level}\n"
            f"**Groups Sold:** {total_sales}\n\n"
        )
        
        if rating_info['total_ratings'] > 0:
            reputation_text += (
                f"**Trust Indicators:**\n"
                f"• {'✅' if rating_info['average_rating'] >= 4.0 else '⚠️'} Customer Satisfaction\n"
                f"• {'✅' if total_sales >= 5 else '⚠️'} Sales Experience\n"
                f"• {'✅' if rating_info['total_ratings'] >= 3 else '⚠️'} Review History\n\n"
            )
        else:
            reputation_text += (
                f"**Trust Indicators:**\n"
                f"• ⚠️ New seller - no reviews yet\n"
                f"• ⚠️ No sales history\n"
                f"• ⚠️ Proceed with caution\n\n"
            )
        
        reputation_text += (
            f"💡 **Tip:** Check reputation before making deals.\n"
            f"Higher ratings indicate more trustworthy sellers."
        )
        
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Listing", callback_data="back_to_listing")]
        ])
        
        await callback_query.message.edit_text(reputation_text, reply_markup=back_keyboard)
        await callback_query.answer("Seller reputation displayed")
        
    except Exception as e:
        print(f"Error in seller_reputation_callback: {e}")
        await callback_query.answer("❌ Error loading seller reputation!", show_alert=True)

# Handle back to listing from reputation view
@teleshop_bot.on_callback_query(filters.regex(r"^back_to_listing$"))
async def back_to_listing_callback(client: Client, callback_query):
    try:
        # Refresh the buy command display
        groups = await fetch_group_listings()
        
        # Filter out groups that belong to the current user
        user_id = callback_query.from_user.id
        available_groups = [
            group for group in groups 
            if group.get('seller_id') != user_id
        ]
        
        if not available_groups or len(available_groups) == 0:
            await callback_query.message.edit_text(
                "❌ No groups are currently available for purchase."
            )
            return
        
        # Use filtered groups
        groups = available_groups
        idx = 0
        total = len(groups)
        group = groups[idx]
        kb = []
        
        # Navigation buttons
        if total > 1:
            kb.append([
                InlineKeyboardButton("⬅️ Back", callback_data=f"buy_back_{idx}"),
                InlineKeyboardButton("➡️ Next", callback_data=f"buy_next_{idx}")
            ])
        
        # Seller reputation button
        kb.append([
            InlineKeyboardButton("👤 Seller Reputation", callback_data=f"seller_reputation_{group.get('seller_id', 0)}")
        ])
        
        # Accept Deal button
        kb.append([
            InlineKeyboardButton("✅ Accept Deal", callback_data=f"accept_deal_{group.get('group_id', '')}_{group.get('seller_id', '')}")
        ])
        
        formatted_group = await format_group(group, idx, total)
        await callback_query.message.edit_text(
            formatted_group,
            reply_markup=InlineKeyboardMarkup(kb) if kb else None
        )
        await callback_query.answer()
        
    except Exception as e:
        print(f"Error in back_to_listing_callback: {e}")
        await callback_query.answer("❌ Error returning to listing!", show_alert=True)

# Handle Accept Deal button
@teleshop_bot.on_callback_query(filters.regex(r"^accept_deal_(-?\d+)_(\d+)"))
async def accept_deal_callback(client: Client, callback_query):
    try:
        group_id, seller_id = callback_query.data.split('_')[2:]
        group_id = int(group_id)
        seller_id = int(seller_id)
        
        buyer = callback_query.from_user
        
        # Check if buyer is trying to buy their own group
        if buyer.id == seller_id:
            await callback_query.answer(
                "❌ You cannot buy your own group! Please select a different group.",
                show_alert=True
            )
            return
        
        # Check if seller is already in an active conversation
        seller_in_chat = False
        if hasattr(client, 'active_chats') and seller_id in client.active_chats:
            seller_in_chat = True
        
        # If seller is busy, add buyer to queue
        if seller_in_chat:
            await callback_query.answer("Seller is busy. You've been added to the queue.", show_alert=True)
            
            # Initialize buyer queue if not exists
            if not hasattr(client, 'buyer_queue'):
                client.buyer_queue = {}
            if seller_id not in client.buyer_queue:
                client.buyer_queue[seller_id] = []
            
            # Add buyer to queue
            queue_entry = {
                'buyer_id': buyer.id,
                'buyer_name': buyer.first_name,
                'group_id': group_id,
                'timestamp': callback_query.message.date.timestamp()
            }
            client.buyer_queue[seller_id].append(queue_entry)
            queue_position = len(client.buyer_queue[seller_id])
            
            # Notify buyer about queue
            await callback_query.message.reply_text(
                f"⏳ **Added to Queue**\n\n"
                f"The seller is currently in another conversation.\n"
                f"📍 **Your position:** {queue_position} in queue\n\n"
                f"You'll be notified when it's your turn. The seller will also be informed about your interest.\n\n"
                f"💡 **Note:** You can browse other groups while waiting."
            )
            
            # Notify seller about queued buyer
            current_deal_id = client.active_chats[seller_id]['deal_id']
            current_deal = client.active_deals[current_deal_id]
            
            queue_notification = (
                f"📋 **New Buyer in Queue**\n\n"
                f"Another buyer is interested in your group while you're chatting with `{current_deal['anonymous_buyer_id']}`\n\n"
                f"**Queue Status:**\n"
                f"• Total waiting: {queue_position}\n"
                f"• Group: {current_deal['group_name']}\n\n"
                f"**Options:**\n"
                f"• Continue your current conversation normally\n"
                f"• Use 'Manage Queue' button when ready"
            )
            
            queue_management_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Manage Queue", callback_data=f"manage_queue_{seller_id}")]
            ])
            
            try:
                await client.send_message(seller_id, queue_notification, reply_markup=queue_management_keyboard)
            except:
                pass
            
            return
        
        # Continue with normal flow if seller is not busy
        # Generate completely anonymous 10-character identifiers
        import string
        import random
        
        def generate_anonymous_id():
            """Generate a 10-character anonymous identifier"""
            chars = string.ascii_uppercase + string.digits
            return ''.join(random.choices(chars, k=10))
        
        # Create anonymous identifiers
        anonymous_buyer_id = generate_anonymous_id()
        anonymous_seller_id = generate_anonymous_id()
        
        # Get buyer's rating for seller notification
        from database import get_user_rating
        buyer_rating_info = await get_user_rating(buyer.id)
        
        # Get group details
        groups = await fetch_group_listings()
        group_info = None
        for group in groups:
            if group.get('group_id') == group_id:
                group_info = group
                break
        
        if not group_info:
            await callback_query.answer("❌ Group not found or no longer available.", show_alert=True)
            return
        
        # Double-check seller ownership (extra security)
        if group_info.get('seller_id') == buyer.id:
            await callback_query.answer(
                "❌ This is your own group listing! You cannot purchase it.",
                show_alert=True
            )
            return
        
        await callback_query.answer("Please add your note for the seller!")
        
        # Ask buyer for optional note
        note_message = await callback_query.message.reply_text(
            f"📝 **Add a note for the seller** (Optional)\n\n"
            f"You can include specific requirements or payment preferences:\n"
            f"• Payment method (e.g., 'I can pay only in INR')\n"
            f"• Timeline preferences\n"
            f"• Any questions about the group\n\n"
            f"⚠️ **Do NOT include personal information like your name, phone, or email**\n\n"
            f"**Type your note or send 'skip' to continue without a note:**"
        )
        
        # Wait for buyer's note
        note_response = await client.listen(
            chat_id=callback_query.message.chat.id,
            filters=filters.text & filters.user(buyer.id),
            timeout=300
        )
        
        buyer_note = ""
        if note_response:
            if note_response.text.strip().lower() != 'skip':
                buyer_note = note_response.text.strip()
                await note_response.reply_text("✅ Note added successfully!")
            else:
                await note_response.reply_text("✅ Proceeding without note.")
        else:
            await note_message.reply_text("⌛ Timeout - proceeding without note.")
        
        # Create unique deal ID for tracking
        deal_id = f"{buyer.id}_{group_id}_{int(callback_query.message.date.timestamp())}"
        
        # Format buyer reputation for seller notification
        buyer_reputation_text = ""
        if buyer_rating_info['total_ratings'] > 0:
            buyer_stars = "⭐" * int(buyer_rating_info['average_rating'])
            trust_level = 'Excellent' if buyer_rating_info['average_rating'] >= 4.5 else \
                         'Good' if buyer_rating_info['average_rating'] >= 4.0 else \
                         'Fair' if buyer_rating_info['average_rating'] >= 3.0 else 'Poor'
            buyer_reputation_text = (
                f"**Buyer Reputation:**\n"
                f"• Rating: {buyer_rating_info['average_rating']:.1f}/5.0 {buyer_stars}\n"
                f"• Total Reviews: {buyer_rating_info['total_ratings']}\n"
                f"• Trust Level: {trust_level}\n\n"
            )
        else:
            buyer_reputation_text = (
                f"**Buyer Reputation:**\n"
                f"• New buyer - no reviews yet\n"
                f"• Trust Level: Unverified\n"
                f"• Proceed with caution\n\n"
            )
        
        # Notify the seller with acceptance/rejection options (completely anonymous)
        seller_notification = (
            f"🎉 **Someone is interested in your group!**\n\n"
            f"**Anonymous Buyer ID:** `{anonymous_buyer_id}`\n\n"
            f"{buyer_reputation_text}"
            f"**Group Details:**\n"
            f"• Group Name: {group_info.get('name', 'N/A')}\n"
            f"• Price: {group_info.get('price', 'N/A')}\n"
            f"• Members: {group_info.get('members', 'N/A')}\n\n"
        )
        
        if buyer_note:
            seller_notification += f"💬 **Buyer's Message:**\n{buyer_note}\n\n"
        
        seller_notification += (
            f"🔒 **Privacy Protection:** Both parties remain anonymous until deal completion.\n\n"
            f"Please review the buyer's interest and choose your response:"
        )
        
        seller_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Accept Deal", callback_data=f"seller_accept_{deal_id}"),
                InlineKeyboardButton("❌ Reject Deal", callback_data=f"seller_reject_{deal_id}")
            ]
        ])
        
        try:
            await client.send_message(seller_id, seller_notification, reply_markup=seller_keyboard)
            seller_notified = True
        except Exception as e:
            print(f"Failed to notify seller {seller_id}: {e}")
            seller_notified = False
        
        # Notify the buyer (completely anonymous)
        if seller_notified:
            buyer_response = (
                f"✅ **Deal Interest Sent Successfully!**\n\n"
                f"**Anonymous Seller ID:** `{anonymous_seller_id}`\n\n"
                f"The seller has been notified about your interest in:\n"
                f"**{group_info.get('name', 'N/A')}** - {group_info.get('price', 'N/A')}\n\n"
            )
            
            if buyer_note:
                buyer_response += f"📝 **Your message:** {buyer_note}\n\n"
            
            buyer_response += (
                f"⏳ The seller will review your request and respond soon.\n"
                f"You'll be notified of their decision.\n\n"
                f"🔒 **Privacy Protection:** Your identity remains anonymous until deal completion.\n\n"
                f"🔐 **Safety Tips:**\n"
                f"• Always verify the group before payment\n"
                f"• Use secure payment methods\n"
                f"• Don't share personal information in messages\n"
                f"• Report suspicious behavior to admins"
            )
        else:
            buyer_response = (
                f"❌ **Failed to notify seller**\n\n"
                f"The seller might have blocked the bot or their account is unavailable. "
                f"Please try contacting them through other groups or choose another listing."
            )
        
        await callback_query.message.reply_text(buyer_response)
        
        # Store deal info for later use (with anonymous IDs for user display)
        deal_info = {
            'buyer_id': buyer.id,
            'buyer_name': anonymous_buyer_id,  # Use anonymous ID instead of name
            'buyer_username': 'Anonymous',     # No username disclosure
            'buyer_note': buyer_note,
            'seller_id': seller_id,
            'group_id': group_id,
            'group_name': group_info.get('name', 'N/A'),
            'price': group_info.get('price', 'N/A'),
            'anonymous_buyer_id': anonymous_buyer_id,
            'anonymous_seller_id': anonymous_seller_id
        }
        
        # Store in a global dict
        if not hasattr(client, 'pending_deals'):
            client.pending_deals = {}
        client.pending_deals[deal_id] = deal_info
        
        # Log to admin group if available (with real info for admin tracking only)
        if LOG_GROUP:
            log_message = (
                f"📊 **Deal Interest Logged**\n\n"
                f"**Deal ID:** `{deal_id}`\n"
                f"**Anonymous Buyer ID:** `{anonymous_buyer_id}`\n"
                f"**Anonymous Seller ID:** `{anonymous_seller_id}`\n"
                f"**Real Buyer:** {buyer.first_name} (ID: {buyer.id})\n"
                f"**Real Seller ID:** `{seller_id}`\n"
                f"**Buyer Rating:** {buyer_rating_info['average_rating']:.1f}/5 ({buyer_rating_info['total_ratings']} reviews)\n"
                f"**Group:** {group_info.get('name', 'N/A')}\n"
                f"**Price:** {group_info.get('price', 'N/A')}\n"
                f"**Buyer Note:** {buyer_note if buyer_note else 'None'}\n"
                f"**Notification Status:** {'✅ Sent' if seller_notified else '❌ Failed'}"
            )
            await client.send_message(LOG_GROUP, log_message)
            
    except Exception as e:
        print(f"Error in accept_deal_callback: {e}")
        await callback_query.answer("❌ An error occurred. Please try again.", show_alert=True)

# Handle seller's acceptance/rejection
@teleshop_bot.on_callback_query(filters.regex(r"^seller_(accept|reject)_(.+)"))
async def seller_response_callback(client: Client, callback_query):
    try:
        action, deal_id = callback_query.data.split('_', 2)[1:]
        
        # Get deal info
        if not hasattr(client, 'pending_deals') or deal_id not in client.pending_deals:
            await callback_query.answer("❌ Deal information not found.", show_alert=True)
            return
        
        deal_info = client.pending_deals[deal_id]
        
        if action == "accept":
            await callback_query.answer("Deal accepted! Starting anonymous chat.")
            
            # Create anonymous chat keyboard for seller
            from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
            seller_chat_keyboard = ReplyKeyboardMarkup([
                [KeyboardButton("✅ Deal Completed")],
                [KeyboardButton("❌ Report Issue"), KeyboardButton("📞 End Chat")]
            ], resize_keyboard=True)
            
            # Update seller message
            await callback_query.message.edit_text(
                f"✅ **Deal Accepted!**\n\n"
                f"You have accepted the deal with buyer `{deal_info['anonymous_buyer_id']}` "
                f"for **{deal_info['group_name']}** - {deal_info['price']}\n\n"
                f"🔒 **Anonymous Chat Started**\n"
                f"You can now communicate directly with the buyer through this bot. "
                f"All messages will be forwarded anonymously.\n\n"
                f"💬 **How to chat:**\n"
                f"• Type any message to send to the buyer\n"
                f"• Click '✅ Deal Completed' when transaction is done\n"
                f"• Click '❌ Report Issue' if there are problems\n"
                f"• Click '📞 End Chat' to stop anonymous messaging\n\n"
                f"⚠️ **Remember:** Keep discussions professional and deal-related only."
            )
            
            # Send keyboard separately to seller
            await client.send_message(
                deal_info['seller_id'],
                "💬 **Anonymous Chat Active**\nUse the keyboard below or type messages directly:",
                reply_markup=seller_chat_keyboard
            )
            
            # Create anonymous chat keyboard for buyer  
            buyer_chat_keyboard = ReplyKeyboardMarkup([
                [KeyboardButton("✅ Deal Completed")],
                [KeyboardButton("❌ Report Issue"), KeyboardButton("📞 End Chat")]
            ], resize_keyboard=True)
            
            # Notify buyer of acceptance
            buyer_notification = (
                f"🎉 **Your deal request was ACCEPTED!**\n\n"
                f"**Anonymous Seller ID:** `{deal_info['anonymous_seller_id']}`\n"
                f"**Group:** {deal_info['group_name']}\n"
                f"**Price:** {deal_info['price']}\n\n"
                f"🔒 **Anonymous Chat Started**\n"
                f"You can now communicate directly with the seller through this bot. "
                f"All messages will be forwarded anonymously.\n\n"
                f"💬 **How to chat:**\n"
                f"• Type any message to send to the seller\n"
                f"• Click '✅ Deal Completed' when you receive the group\n"
                f"• Click '❌ Report Issue' if there are problems\n"
                f"• Click '📞 End Chat' to stop anonymous messaging\n\n"
                f"⚠️ **Remember:** Keep discussions professional and deal-related only."
            )
            
            try:
                await client.send_message(deal_info['buyer_id'], buyer_notification)
                await client.send_message(
                    deal_info['buyer_id'],
                    "💬 **Anonymous Chat Active**\nUse the keyboard below or type messages directly:",
                    reply_markup=buyer_chat_keyboard
                )
                buyer_notified = True
            except:
                buyer_notified = False
            
            # Store deal as active for chat and completion tracking
            if not hasattr(client, 'active_deals'):
                client.active_deals = {}
            client.active_deals[deal_id] = {
                **deal_info,
                'seller_completed': False,
                'buyer_completed': False,
                'seller_rating': None,
                'buyer_rating': None,
                'chat_active': True,
                'seller_in_chat': True,
                'buyer_in_chat': True
            }
            
            # Store chat mapping for message forwarding
            if not hasattr(client, 'active_chats'):
                client.active_chats = {}
            client.active_chats[deal_info['seller_id']] = {
                'deal_id': deal_id,
                'partner_id': deal_info['buyer_id'],
                'partner_name': deal_info['anonymous_buyer_id'],
                'role': 'seller'
            }
            client.active_chats[deal_info['buyer_id']] = {
                'deal_id': deal_id,
                'partner_id': deal_info['seller_id'],
                'partner_name': deal_info['anonymous_seller_id'],
                'role': 'buyer'
            }
        
        else:  # reject
            # Ask seller for rejection reason
            await callback_query.answer("Please provide a reason for rejection.")
            
            await callback_query.message.edit_text(
                f"❌ **Rejecting Deal Request**\n\n"
                f"**Anonymous Buyer ID:** `{deal_info['anonymous_buyer_id']}`\n"
                f"**Group:** {deal_info['group_name']}\n"
                f"**Price:** {deal_info['price']}\n\n"
                f"Please provide a reason for rejection (this will be shared with the buyer):\n\n"
                f"⚠️ **Do NOT include personal information in your message**"
            )
            
            # Wait for rejection reason
            rejection_reason_response = await client.listen(
                chat_id=callback_query.message.chat.id,
                filters=filters.text & filters.user(callback_query.from_user.id),
                timeout=300
            )
            
            rejection_reason = "No reason provided"
            if rejection_reason_response:
                rejection_reason = rejection_reason_response.text.strip()
                await rejection_reason_response.reply_text("✅ Rejection reason noted.")
            
            # Update seller message
            await callback_query.message.reply_text(
                f"❌ **Deal Rejected**\n\n"
                f"You have rejected the deal with buyer `{deal_info['anonymous_buyer_id']}` "
                f"for **{deal_info['group_name']}**\n\n"
                f"**Reason:** {rejection_reason}\n\n"
                f"The buyer has been notified of your decision."
            )
            
            # Notify buyer of rejection
            buyer_notification = (
                f"❌ **Your deal request was REJECTED**\n\n"
                f"**Anonymous Seller ID:** `{deal_info['anonymous_seller_id']}`\n"
                f"**Group:** {deal_info['group_name']}\n"
                f"**Price:** {deal_info['price']}\n\n"
                f"**Seller's Reason:**\n{rejection_reason}\n\n"
                f"Don't worry! You can browse other groups or try again later. "
                f"Use /buy to see more available groups."
            )
            
            try:
                await client.send_message(deal_info['buyer_id'], buyer_notification)
                buyer_notified = True
            except:
                buyer_notified = False
            
            # Log rejection
            if LOG_GROUP:
                log_message = (
                    f"❌ **Deal REJECTED**\n\n"
                    f"**Deal ID:** `{deal_id}`\n"
                    f"**Anonymous Seller:** `{deal_info['anonymous_seller_id']}`\n"
                    f"**Anonymous Buyer:** `{deal_info['anonymous_buyer_id']}`\n"
                    f"**Real Seller ID:** `{deal_info['seller_id']}`\n"
                    f"**Real Buyer ID:** `{deal_info['buyer_id']}`\n"
                    f"**Group:** {deal_info['group_name']}\n"
                    f"**Price:** {deal_info['price']}\n"
                    f"**Reason:** {rejection_reason}\n"
                    f"**Buyer Notified:** {'✅ Yes' if buyer_notified else '❌ Failed'}"
                )
                await client.send_message(LOG_GROUP, log_message)
        
        # Clean up deal info
        del client.pending_deals[deal_id]
        
    except Exception as e:
        print(f"Error in seller_response_callback: {e}")
        await callback_query.answer("❌ An error occurred. Please try again.", show_alert=True)

# Handle deal completion
@teleshop_bot.on_callback_query(filters.regex(r"^deal_completed_(seller|buyer)_(.+)"))
async def deal_completion_callback(client: Client, callback_query):
    try:
        user_type, deal_id = callback_query.data.split('_', 3)[2:]
        
        # Get active deal info
        if not hasattr(client, 'active_deals') or deal_id not in client.active_deals:
            await callback_query.answer("❌ Deal information not found.", show_alert=True)
            return
        
        deal_info = client.active_deals[deal_id]
        user_id = callback_query.from_user.id
        
        # Verify user authorization
        if user_type == "seller" and user_id != deal_info['seller_id']:
            await callback_query.answer("❌ You are not the seller of this deal!", show_alert=True)
            return
        elif user_type == "buyer" and user_id != deal_info['buyer_id']:
            await callback_query.answer("❌ You are not the buyer of this deal!", show_alert=True)
            return
        
        # Mark user as completed
        if user_type == "seller":
            deal_info['seller_completed'] = True
        else:
            deal_info['buyer_completed'] = True
        
        await callback_query.answer("Deal marked as completed! Please rate your experience.")
        
        # Ask for rating
        rating_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⭐ 1", callback_data=f"rate_deal_{user_type}_{deal_id}_1"),
                InlineKeyboardButton("⭐⭐ 2", callback_data=f"rate_deal_{user_type}_{deal_id}_2"),
                InlineKeyboardButton("⭐⭐⭐ 3", callback_data=f"rate_deal_{user_type}_{deal_id}_3")
            ],
            [
                InlineKeyboardButton("⭐⭐⭐⭐ 4", callback_data=f"rate_deal_{user_type}_{deal_id}_4"),
                InlineKeyboardButton("⭐⭐⭐⭐⭐ 5", callback_data=f"rate_deal_{user_type}_{deal_id}_5")
            ]
        ])
        
        # Use anonymous identifiers in the rating message
        if user_type == "seller":
            other_party_id = deal_info.get('anonymous_buyer_id', 'Anonymous Buyer')
            other_party_name = f"buyer `{other_party_id}`"
        else:
            other_party_id = deal_info.get('anonymous_seller_id', 'Anonymous Seller')  
            other_party_name = f"seller `{other_party_id}`"
        
        await callback_query.message.edit_text(
            f"✅ **Deal Completed!**\n\n"
            f"Thank you for confirming the completion of your deal for **{deal_info['group_name']}**\n\n"
            f"🌟 **Please rate your experience with {other_party_name}:**\n"
            f"How would you rate this transaction out of 5 stars?\n\n"
            f"🔒 **Anonymous Rating:** Your identity remains protected.",
            reply_markup=rating_keyboard
        )
        
    except Exception as e:
        print(f"Error in deal_completion_callback: {e}")
        await callback_query.answer("❌ An error occurred. Please try again.", show_alert=True)

# Handle deal rating
@teleshop_bot.on_callback_query(filters.regex(r"^rate_deal_(seller|buyer)_(.+)_(\d)"))
async def deal_rating_callback(client: Client, callback_query):
    try:
        # More robust parsing of callback data
        callback_data = callback_query.data
        print(f"Rating callback data: {callback_data}")  # Debug log
        
        # Split by underscore but be more careful
        parts = callback_data.split('_')
        
        if len(parts) < 4:
            await callback_query.answer("❌ Invalid rating data format!", show_alert=True)
            return
        
        # First two parts are always "rate" and "deal"
        # Third part is user_type (seller/buyer)
        user_type = parts[2]
        
        # Last part is always the rating
        rating = int(parts[-1])
        
        # Everything in between (parts[3:-1]) forms the deal_id
        deal_id = '_'.join(parts[3:-1])
        
        print(f"Parsed - user_type: {user_type}, deal_id: {deal_id}, rating: {rating}")  # Debug log
        
        # Validate user_type
        if user_type not in ['seller', 'buyer']:
            await callback_query.answer("❌ Invalid user type!", show_alert=True)
            return
        
        # Validate rating
        if rating < 1 or rating > 5:
            await callback_query.answer("❌ Invalid rating value!", show_alert=True)
            return
        
        # Get active deal info
        if not hasattr(client, 'active_deals') or deal_id not in client.active_deals:
            await callback_query.answer("❌ Deal information not found.", show_alert=True)
            print(f"Deal {deal_id} not found in active_deals")
            return

        deal_info = client.active_deals[deal_id]

        # Verify the user is authorized to rate this deal
        user_id = callback_query.from_user.id
        if user_type == "seller" and user_id != deal_info['seller_id']:
            await callback_query.answer("❌ You are not authorized to rate this deal as seller!", show_alert=True)
            return
        elif user_type == "buyer" and user_id != deal_info['buyer_id']:
            await callback_query.answer("❌ You are not authorized to rate this deal as buyer!", show_alert=True)
            return

        # Set rating and determine who got rated
        if user_type == "seller":
            deal_info['seller_rating'] = rating
            rated_party_id = deal_info['buyer_id']
        else:
            deal_info['buyer_rating'] = rating
            rated_party_id = deal_info['seller_id']

        await callback_query.answer(f"Thank you for rating {rating} stars!")

        # Update database with rating
        from database import add_user_rating, update_deal_statistics, remove_group_from_listings, mark_group_as_sold_with_buyer
        await add_user_rating(rated_party_id, rating)

        stars = "⭐" * rating
        await callback_query.message.edit_text(
            f"✅ **Rating Submitted!**\n\n"
            f"You rated this deal: {stars} ({rating}/5)\n\n"
            f"Thank you for your feedback! This helps maintain quality in our marketplace."
        )

        # Check if both parties completed and rated the deal
        if (deal_info.get('seller_completed', False) and deal_info.get('buyer_completed', False) and 
            deal_info.get('seller_rating') is not None and deal_info.get('buyer_rating') is not None):

            # Mark group as sold with buyer information first
            await mark_group_as_sold_with_buyer(deal_info['group_id'], deal_info['buyer_id'])

            # Update deal statistics for both users
            await update_deal_statistics(deal_info['seller_id'], 'sold')
            await update_deal_statistics(deal_info['buyer_id'], 'bought')

            # Ensure group is removed from active listings
            await remove_group_from_listings(deal_info['group_id'])

            # Verify group is removed from active listings
            active_groups = await fetch_group_listings()
            group_still_active = any(g.get('group_id') == deal_info['group_id'] for g in active_groups)
            
            # Log completed deal with verification
            if LOG_GROUP:
                avg_rating = (deal_info['seller_rating'] + deal_info['buyer_rating']) / 2
                log_message = (
                    f"🎯 **Deal COMPLETED & RATED**\n\n"
                    f"**Deal ID:** `{deal_id}`\n"
                    f"**Group:** {deal_info['group_name']}\n"
                    f"**Group ID:** {deal_info['group_id']}\n"
                    f"**Anonymous Seller:** `{deal_info['anonymous_seller_id']}`\n"
                    f"**Anonymous Buyer:** `{deal_info['anonymous_buyer_id']}`\n"
                    f"**Real Seller ID:** `{deal_info['seller_id']}`\n"
                    f"**Real Buyer ID:** `{deal_info['buyer_id']}`\n"
                    f"**Price:** {deal_info['price']}\n"
                    f"**Seller Rating:** {deal_info['buyer_rating']}⭐\n"
                    f"**Buyer Rating:** {deal_info['seller_rating']}⭐\n"
                    f"**Average Rating:** {avg_rating:.1f}/5 ⭐\n"
                    f"**Status:** {'✅ Removed from listings' if not group_still_active else '❌ Still in listings'}"
                )
                await client.send_message(LOG_GROUP, log_message)

            # Clean up completed deal
            del client.active_deals[deal_id]

    except ValueError as ve:
        print(f"ValueError in deal_rating_callback: {ve}")
        await callback_query.answer("❌ Invalid rating format!", show_alert=True)
    except KeyError as ke:
        print(f"KeyError in deal_rating_callback: {ke}")
        await callback_query.answer("❌ Missing deal information!", show_alert=True)
    except Exception as e:
        print(f"Error in deal_rating_callback: {e}")
        import traceback
        traceback.print_exc()
        await callback_query.answer("❌ An error occurred. Please try again.", show_alert=True)

# Handle anonymous chat messages - make this more specific
@teleshop_bot.on_message(filters.text & filters.private, group=10)  # Lower priority
async def handle_anonymous_chat(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        
        # Check if user is in an active chat
        if not hasattr(client, 'active_chats') or user_id not in client.active_chats:
            return  # Not in chat, let other handlers process
        
        chat_info = client.active_chats[user_id]
        deal_id = chat_info['deal_id']
        
        # Check if deal is still active
        if not hasattr(client, 'active_deals') or deal_id not in client.active_deals:
            # Clean up stale chat
            if user_id in client.active_chats:
                del client.active_chats[user_id]
            return
        
        deal_info = client.active_deals[deal_id]
        
        # Check if chat is still active
        if not deal_info.get('chat_active', False):
            # Clean up stale chat mapping
            if user_id in client.active_chats:
                del client.active_chats[user_id]
            return
        
        # Check if user is still in chat
        user_role = chat_info['role']
        if user_role == "seller" and not deal_info.get('seller_in_chat', False):
            # Seller left chat, clean up
            if user_id in client.active_chats:
                del client.active_chats[user_id]
            return
        elif user_role == "buyer" and not deal_info.get('buyer_in_chat', False):
            # Buyer left chat, clean up
            if user_id in client.active_chats:
                del client.active_chats[user_id]
            return
        
        text = message.text.strip()
        print(f"Anonymous chat handler received: '{text}'")  # Debug log
        
        # Handle special commands
        if text == "✅ Deal Completed":
            await handle_deal_completion_request(client, message, user_id, deal_id)
            return
        elif text == "❌ Report Issue":
            await handle_issue_report(client, message, user_id, deal_id)
            return
        elif text == "📞 End Chat":
            await handle_end_chat(client, message, user_id, deal_id)
            return
        # Skip menu navigation messages - let start.py handle them
        elif any(keyword in text.lower() for keyword in ["buy groups", "sell groups", "my profile", "help", "settings", "back to main menu"]):
            return  # Let the start.py handler deal with these
        
        # Check for links and block them
        link_patterns = [
            r'https?://[^\s]+',  # HTTP/HTTPS links
            r'www\.[^\s]+',      # www links
            r't\.me/[^\s]+',     # Telegram links
            r'@[a-zA-Z0-9_]+',   # Username mentions
            r'\+\d{10,15}',      # Phone numbers
        ]
        
        import re
        for pattern in link_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                await message.reply_text(
                    "🚫 **Link/Contact Sharing Blocked**\n\n"
                    "For security reasons, sharing links, usernames, or contact information is not allowed in anonymous chat.\n\n"
                    "💡 **Alternative:**\n"
                    "• Use the deal completion process to exchange details safely\n"
                    "• Complete the transaction through the bot's secure system"
                )
                return
        
        # Forward regular messages
        partner_id = chat_info['partner_id']
        partner_name = chat_info['partner_name']
        
        # Double check partner is still in chat
        if partner_id not in client.active_chats:
            await message.reply_text(
                "❌ **Chat partner has left**\n\n"
                "The other party is no longer in the chat. Your message was not delivered."
            )
            return
        
        # Create simplified forwarded message
        forwarded_message = f"💬 **{partner_name}:** {text}"
        
        try:
            await client.send_message(partner_id, forwarded_message)
            
            # Confirm message sent with shorter confirmation
            await message.reply_text(f"✅ Sent to {partner_name}")
            
        except Exception as e:
            await message.reply_text(
                f"❌ Failed to send message to {partner_name}. "
                f"They might have ended the chat or blocked the bot."
            )
            print(f"Failed to forward message: {e}")
            
    except Exception as e:
        print(f"Error in handle_anonymous_chat: {e}")

async def handle_deal_completion_request(client: Client, message: Message, user_id: int, deal_id: str):
    """Handle deal completion request"""
    try:
        deal_info = client.active_deals[deal_id]
        user_role = client.active_chats[user_id]['role']
        
        # Mark user as completed
        if user_role == "seller":
            deal_info['seller_completed'] = True
            completion_message = "✅ **You marked the deal as completed!**\n\nWaiting for buyer confirmation..."
        else:
            deal_info['buyer_completed'] = True  
            completion_message = "✅ **You marked the deal as completed!**\n\nWaiting for seller confirmation..."
        
        await message.reply_text(completion_message)
        
        # Notify partner
        partner_id = client.active_chats[user_id]['partner_id']
        partner_name = client.active_chats[user_id]['partner_name']
        
        partner_notification = (
            f"✅ **{partner_name} marked the deal as completed!**\n\n"
            f"If you have also completed your part of the transaction, "
            f"click '✅ Deal Completed' to proceed to rating."
        )
        
        try:
            await client.send_message(partner_id, partner_notification)
        except:
            pass
        
        # Check if both completed
        if deal_info['seller_completed'] and deal_info['buyer_completed']:
            await finalize_deal_completion(client, deal_id)
            
    except Exception as e:
        print(f"Error in handle_deal_completion_request: {e}")

async def handle_issue_report(client: Client, message: Message, user_id: int, deal_id: str):
    """Handle issue reporting"""
    try:
        deal_info = client.active_deals[deal_id]
        user_role = client.active_chats[user_id]['role']
        
        await message.reply_text(
            "⚠️ **Report an Issue**\n\n"
            "Please describe the issue you're experiencing with this deal. "
            "An admin will review your report.\n\n"
            "Type your issue description:"
        )
        
        # Wait for issue description
        issue_response = await client.listen(
            chat_id=message.chat.id,
            filters=filters.text & filters.user(user_id),
            timeout=300
        )
        
        if issue_response:
            issue_text = issue_response.text.strip()
            
            # Send to log group
            if LOG_GROUP:
                report_message = (
                    f"⚠️ **ISSUE REPORTED**\n\n"
                    f"**Deal ID:** `{deal_id}`\n"
                    f"**Reporter:** {user_role.title()} (`{user_id}`)\n"
                    f"**Group:** {deal_info['group_name']}\n"
                    f"**Price:** {deal_info['price']}\n"
                    f"**Issue:** {issue_text}\n\n"
                    f"**Seller ID:** `{deal_info['seller_id']}`\n"
                    f"**Buyer ID:** `{deal_info['buyer_id']}`"
                )
                await client.send_message(LOG_GROUP, report_message)
            
            await issue_response.reply_text(
                "✅ **Issue reported successfully!**\n\n"
                "An admin will review your report and contact you if needed. "
                "You can continue with the deal or end the chat if necessary."
            )
        else:
            await message.reply_text("⌛ Timeout. Issue report cancelled.")
            
    except Exception as e:
        print(f"Error in handle_issue_report: {e}")

async def handle_end_chat(client: Client, message: Message, user_id: int, deal_id: str):
    """Handle ending anonymous chat"""
    try:
        deal_info = client.active_deals[deal_id]
        user_role = client.active_chats[user_id]['role']
        partner_id = client.active_chats[user_id]['partner_id']
        partner_name = client.active_chats[user_id]['partner_name']
        
        # Remove user from chat
        if user_role == "seller":
            deal_info['seller_in_chat'] = False
        else:
            deal_info['buyer_in_chat'] = False
        
        # Remove from chat mapping FIRST
        del client.active_chats[user_id]
        
        # Send main keyboard back to user
        from Modules.modules.start import get_main_keyboard
        await message.reply_text(
            "📞 **Chat Ended**\n\n"
            "You have left the anonymous chat. You can no longer send messages to the other party.\n\n"
            "💡 If you need to complete the deal, you can still use the /profile command to manage your transactions.",
            reply_markup=get_main_keyboard()  # Return main keyboard
        )
        
        # Notify partner and remove their keyboard too
        try:
            await client.send_message(
                partner_id,
                f"📞 **{partner_name} has left the chat**\n\n"
                f"The anonymous chat has ended. You can no longer send messages to them."
            )
            
            # Also remove partner from chat if they're still in it
            if partner_id in client.active_chats:
                del client.active_chats[partner_id]
                
                # Send main keyboard to partner
                await client.send_message(
                    partner_id,
                    "💬 **Anonymous chat ended**\n\nReturning to main menu.",
                    reply_markup=get_main_keyboard()
                )
        except:
            pass
        
        # Deactivate chat completely
        deal_info['chat_active'] = False
        deal_info['seller_in_chat'] = False
        deal_info['buyer_in_chat'] = False
            
    except Exception as e:
        print(f"Error in handle_end_chat: {e}")

async def finalize_deal_completion(client: Client, deal_id: str):
    """Finalize deal when both parties mark as completed"""
    try:
        deal_info = client.active_deals[deal_id]
        
        # End chat for both parties completely
        deal_info['chat_active'] = False
        deal_info['seller_in_chat'] = False
        deal_info['buyer_in_chat'] = False
        
        # Clean up chat mappings
        seller_id = deal_info['seller_id']
        buyer_id = deal_info['buyer_id']
        
        if hasattr(client, 'active_chats'):
            if seller_id in client.active_chats:
                del client.active_chats[seller_id]
            if buyer_id in client.active_chats:
                del client.active_chats[buyer_id]
        
        # Start rating process for both
        await start_rating_process(client, seller_id, deal_id, 'seller')
        await start_rating_process(client, buyer_id, deal_id, 'buyer')
        
    except Exception as e:
        print(f"Error in finalize_deal_completion: {e}")

async def start_rating_process(client: Client, user_id: int, deal_id: str, user_type: str):
    """Start rating process for a user"""
    try:
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        deal_info = client.active_deals[deal_id]
        
        # Remove chat keyboard and show rating
        from Modules.modules.start import get_main_keyboard
        await client.send_message(
            user_id,
            "✅ **Deal Completed by Both Parties!**\n\n"
            "The anonymous chat has ended. Please rate your experience.",
            reply_markup=get_main_keyboard()
        )
        
        # Ask for rating
        rating_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⭐ 1", callback_data=f"rate_deal_{user_type}_{deal_id}_1"),
                InlineKeyboardButton("⭐⭐ 2", callback_data=f"rate_deal_{user_type}_{deal_id}_2"),
                InlineKeyboardButton("⭐⭐⭐ 3", callback_data=f"rate_deal_{user_type}_{deal_id}_3")
            ],
            [
                InlineKeyboardButton("⭐⭐⭐⭐ 4", callback_data=f"rate_deal_{user_type}_{deal_id}_4"),
                InlineKeyboardButton("⭐⭐⭐⭐⭐ 5", callback_data=f"rate_deal_{user_type}_{deal_id}_5")
            ]
        ])
        
        # Use anonymous identifiers in the rating message
        if user_type == "seller":
            other_party_id = deal_info.get('anonymous_buyer_id', 'Anonymous Buyer')
            other_party_name = f"buyer `{other_party_id}`"
        else:
            other_party_id = deal_info.get('anonymous_seller_id', 'Anonymous Seller')  
            other_party_name = f"seller `{other_party_id}`"
        
        await client.send_message(
            user_id,
            f"🌟 **Please rate your experience with {other_party_name}:**\n"
            f"How would you rate this transaction out of 5 stars?\n\n"
            f"🔒 **Anonymous Rating:** Your identity remains protected.",
            reply_markup=rating_keyboard
        )
        
    except Exception as e:
        print(f"Error in start_rating_process: {e}")

# Handle queue management
@teleshop_bot.on_callback_query(filters.regex(r"^manage_queue_(\d+)"))
async def manage_queue_callback(client: Client, callback_query):
    try:
        seller_id = int(callback_query.data.split('_')[2])
        
        # Check if user is the seller
        if callback_query.from_user.id != seller_id:
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
        
        # Check if seller has a queue
        if not hasattr(client, 'buyer_queue') or seller_id not in client.buyer_queue:
            await callback_query.answer("No buyers in queue.", show_alert=True)
            return
        
        queue = client.buyer_queue[seller_id]
        if not queue:
            await callback_query.answer("No buyers in queue.", show_alert=True)
            return
        
        # Show queue status
        queue_text = f"📋 **Your Buyer Queue**\n\n**Total waiting: {len(queue)} buyer(s)**\n\n"
        
        for i, buyer in enumerate(queue[:5], 1):  # Show first 5
            queue_text += f"{i}. Buyer interested in group (ID: {buyer['group_id']})\n"
        
        if len(queue) > 5:
            queue_text += f"... and {len(queue) - 5} more\n"
        
        queue_text += (
            f"\n**Options:**\n"
            f"• **Hold Current:** Keep current conversation, queue will wait\n"
            f"• **Next Buyer:** End current chat and start with next buyer\n"
            f"• **Clear Queue:** Reject all waiting buyers"
        )
        
        queue_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸️ Hold Current", callback_data=f"queue_hold_{seller_id}"),
                InlineKeyboardButton("⏭️ Next Buyer", callback_data=f"queue_next_{seller_id}")
            ],
            [InlineKeyboardButton("🗑️ Clear Queue", callback_data=f"queue_clear_{seller_id}")]
        ])
        
        await callback_query.message.edit_text(queue_text, reply_markup=queue_keyboard)
        await callback_query.answer()
        
    except Exception as e:
        print(f"Error in manage_queue_callback: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# Handle queue actions
@teleshop_bot.on_callback_query(filters.regex(r"^queue_(hold|next|clear)_(\d+)"))
async def queue_action_callback(client: Client, callback_query):
    try:
        action, seller_id = callback_query.data.split('_')[1:]
        seller_id = int(seller_id)
        
        # Check if user is the seller
        if callback_query.from_user.id != seller_id:
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
        
        if action == "hold":
            await callback_query.answer("Current conversation will continue. Queue is on hold.")
            await callback_query.message.edit_text(
                "⏸️ **Queue On Hold**\n\n"
                "You've chosen to continue your current conversation.\n"
                "The queue will remain active and you can manage it anytime.\n\n"
                "Use the queue management button when you're ready for the next buyer."
            )
            
        elif action == "next":
            # End current conversation and start with next buyer
            if hasattr(client, 'active_chats') and seller_id in client.active_chats:
                current_deal_id = client.active_chats[seller_id]['deal_id']
                await force_end_current_chat(client, seller_id, current_deal_id)
            
            # Process next buyer in queue
            if hasattr(client, 'buyer_queue') and seller_id in client.buyer_queue and client.buyer_queue[seller_id]:
                next_buyer = client.buyer_queue[seller_id].pop(0)
                await process_queued_buyer(client, seller_id, next_buyer)
                
                await callback_query.message.edit_text(
                    "⏭️ **Processing Next Buyer**\n\n"
                    "Your current conversation has been ended.\n"
                    "Starting conversation with the next buyer in queue."
                )
            else:
                await callback_query.message.edit_text(
                    "❌ **No Buyers in Queue**\n\n"
                    "The queue is empty."
                )
                
        elif action == "clear":
            # Clear entire queue
            if hasattr(client, 'buyer_queue') and seller_id in client.buyer_queue:
                cleared_count = len(client.buyer_queue[seller_id])
                
                # Notify all queued buyers
                for buyer in client.buyer_queue[seller_id]:
                    try:
                        await client.send_message(
                            buyer['buyer_id'],
                            "❌ **Queue Cleared**\n\n"
                            "The seller has cleared their buyer queue.\n"
                            "You can try again later or browse other groups."
                        )
                    except:
                        pass
                
                client.buyer_queue[seller_id] = []
                
                await callback_query.message.edit_text(
                    f"🗑️ **Queue Cleared**\n\n"
                    f"Removed {cleared_count} buyer(s) from queue.\n"
                    f"All waiting buyers have been notified."
                )
            else:
                await callback_query.message.edit_text(
                    "❌ **Queue Already Empty**"
                )
        
        await callback_query.answer()
        
    except Exception as e:
        print(f"Error in queue_action_callback: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

async def force_end_current_chat(client: Client, seller_id: int, deal_id: str):
    """Force end current chat to make room for next buyer"""
    try:
        if hasattr(client, 'active_deals') and deal_id in client.active_deals:
            deal_info = client.active_deals[deal_id]
            buyer_id = deal_info['buyer_id']
            
            # End chat for both parties
            deal_info['chat_active'] = False
            deal_info['seller_in_chat'] = False
            deal_info['buyer_in_chat'] = False
            
            # Clean up chat mappings
            if hasattr(client, 'active_chats'):
                if seller_id in client.active_chats:
                    del client.active_chats[seller_id]
                if buyer_id in client.active_chats:
                    del client.active_chats[buyer_id]
            
            # Notify both parties
            from Modules.modules.start import get_main_keyboard
            
            try:
                await client.send_message(
                    seller_id,
                    "📞 **Chat Ended by Queue Management**\n\n"
                    "Your previous conversation has been ended to process the next buyer in queue.",
                    reply_markup=get_main_keyboard()
                )
            except:
                pass
            
            try:
                await client.send_message(
                    buyer_id,
                    "📞 **Chat Ended**\n\n"
                    "The seller has ended this conversation to manage their buyer queue.\n"
                    "You can browse other groups or try again later.",
                    reply_markup=get_main_keyboard()
                )
            except:
                pass
                
    except Exception as e:
        print(f"Error in force_end_current_chat: {e}")

async def process_queued_buyer(client: Client, seller_id: int, buyer_info: dict):
    """Process the next buyer from queue"""
    try:
        # This would trigger the normal deal acceptance flow
        # For now, just notify both parties
        buyer_id = buyer_info['buyer_id']
        group_id = buyer_info['group_id']
        
        # Get group details
        groups = await fetch_group_listings()
        group_info = None
        for group in groups:
            if group.get('group_id') == group_id:
                group_info = group
                break
        
        if not group_info:
            try:
                await client.send_message(
                    buyer_id,
                    "❌ **Group No Longer Available**\n\n"
                    "The group you were waiting for is no longer listed for sale."
                )
            except:
                pass
            return
        
        # Generate new anonymous IDs
        import string
        import random
        
        def generate_anonymous_id():
            chars = string.ascii_uppercase + string.digits
            return ''.join(random.choices(chars, k=10))
        
        anonymous_buyer_id = generate_anonymous_id()
        anonymous_seller_id = generate_anonymous_id()
        
        # Get buyer's rating
        from database import get_user_rating
        buyer_rating_info = await get_user_rating(buyer_id)
        
        # Format buyer reputation
        buyer_reputation_text = ""
        if buyer_rating_info['total_ratings'] > 0:
            buyer_stars = "⭐" * int(buyer_rating_info['average_rating'])
            trust_level = 'Excellent' if buyer_rating_info['average_rating'] >= 4.5 else \
                         'Good' if buyer_rating_info['average_rating'] >= 4.0 else \
                         'Fair' if buyer_rating_info['average_rating'] >= 3.0 else 'Poor'
            buyer_reputation_text = (
                f"**Buyer Reputation:**\n"
                f"• Rating: {buyer_rating_info['average_rating']:.1f}/5.0 {buyer_stars}\n"
                f"• Total Reviews: {buyer_rating_info['total_ratings']}\n"
                f"• Trust Level: {trust_level}\n\n"
            )
        else:
            buyer_reputation_text = (
                f"**Buyer Reputation:**\n"
                f"• New buyer - no reviews yet\n"
                f"• Trust Level: Unverified\n"
                f"• Proceed with caution\n\n"
            )
        
        # Create deal ID
        deal_id = f"{buyer_id}_{group_id}_{int(time.time())}"
        
        # Notify seller
        seller_notification = (
            f"⏭️ **Next Buyer from Queue**\n\n"
            f"**Anonymous Buyer ID:** `{anonymous_buyer_id}`\n\n"
            f"{buyer_reputation_text}"
            f"**Group Details:**\n"
            f"• Group Name: {group_info.get('name', 'N/A')}\n"
            f"• Price: {group_info.get('price', 'N/A')}\n"
            f"• Members: {group_info.get('members', 'N/A')}\n\n"
            f"🔒 **Privacy Protection:** Both parties remain anonymous until deal completion.\n\n"
            f"Please review this buyer's interest and choose your response:"
        )
        
        seller_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Accept Deal", callback_data=f"seller_accept_{deal_id}"),
                InlineKeyboardButton("❌ Reject Deal", callback_data=f"seller_reject_{deal_id}")
            ]
        ])
        
        try:
            await client.send_message(seller_id, seller_notification, reply_markup=seller_keyboard)
        except:
            return
        
        # Notify buyer
        try:
            await client.send_message(
                buyer_id,
                f"🎉 **Your Turn!**\n\n"
                f"**Anonymous Seller ID:** `{anonymous_seller_id}`\n\n"
                f"The seller is now reviewing your interest in:\n"
                f"**{group_info.get('name', 'N/A')}** - {group_info.get('price', 'N/A')}\n\n"
                f"You'll be notified of their decision soon."
            )
        except:
            pass
        
        # Store deal info
        deal_info = {
            'buyer_id': buyer_id,
            'buyer_name': anonymous_buyer_id,
            'buyer_username': 'Anonymous',
            'buyer_note': '',  # No note for queued buyers
            'seller_id': seller_id,
            'group_id': group_id,
            'group_name': group_info.get('name', 'N/A'),
            'price': group_info.get('price', 'N/A'),
            'anonymous_buyer_id': anonymous_buyer_id,
            'anonymous_seller_id': anonymous_seller_id
        }
        
        if not hasattr(client, 'pending_deals'):
            client.pending_deals = {}
        client.pending_deals[deal_id] = deal_info
        
    except Exception as e:
        print(f"Error in process_queued_buyer: {e}")