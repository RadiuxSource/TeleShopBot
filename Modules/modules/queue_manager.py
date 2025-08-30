from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Modules import teleshop_bot
import time

# Handle post-chat queue options for sellers
async def handle_post_chat_queue_options(client: Client, seller_id: int):
    """Show queue options to seller after ending a chat"""
    try:
        # Check if seller has any queued buyers
        if not hasattr(client, 'buyer_queue') or seller_id not in client.buyer_queue:
            return
        
        queue = client.buyer_queue[seller_id]
        if not queue:
            return
        
        # Show queue notification with options
        queue_text = (
            f"📋 **You have {len(queue)} buyer(s) waiting in queue!**\n\n"
            f"What would you like to do with the waiting buyers?"
        )
        
        queue_options_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👥 View Queue", callback_data=f"view_queue_{seller_id}"),
                InlineKeyboardButton("⏭️ Next Buyer", callback_data=f"process_next_buyer_{seller_id}")
            ],
            [
                InlineKeyboardButton("⏸️ Take a Break", callback_data=f"seller_break_{seller_id}"),
                InlineKeyboardButton("🗑️ Clear Queue", callback_data=f"clear_all_queue_{seller_id}")
            ]
        ])
        
        await client.send_message(seller_id, queue_text, reply_markup=queue_options_keyboard)
        
    except Exception as e:
        print(f"Error in handle_post_chat_queue_options: {e}")

# Handle view queue callback
@teleshop_bot.on_callback_query(filters.regex(r"^view_queue_(\d+)"))
async def view_queue_callback(client: Client, callback_query):
    try:
        seller_id = int(callback_query.data.split('_')[2])
        
        # Check authorization
        if callback_query.from_user.id != seller_id:
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
        
        # Get queue info
        if not hasattr(client, 'buyer_queue') or seller_id not in client.buyer_queue:
            await callback_query.answer("No queue found.", show_alert=True)
            return
        
        queue = client.buyer_queue[seller_id]
        if not queue:
            await callback_query.answer("Queue is empty.", show_alert=True)
            return
        
        # Build queue display
        queue_text = f"📋 **Your Buyer Queue** ({len(queue)} waiting)\n\n"
        
        from database import fetch_group_listings
        groups = await fetch_group_listings()
        
        for i, buyer in enumerate(queue[:10], 1):  # Show first 10
            # Find group info
            group_name = "Unknown Group"
            for group in groups:
                if group.get('group_id') == buyer['group_id']:
                    group_name = group.get('name', 'Unknown Group')
                    break
            
            # Calculate waiting time
            wait_time = int(time.time() - buyer['timestamp'])
            wait_minutes = wait_time // 60
            
            queue_text += f"{i}. **{group_name[:30]}{'...' if len(group_name) > 30 else ''}**\n"
            queue_text += f"   ⏱️ Waiting: {wait_minutes}m ago\n\n"
        
        if len(queue) > 10:
            queue_text += f"... and {len(queue) - 10} more buyers\n\n"
        
        queue_text += "**What would you like to do?**"
        
        queue_action_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏭️ Process Next", callback_data=f"process_next_buyer_{seller_id}"),
                InlineKeyboardButton("🔄 Refresh Queue", callback_data=f"view_queue_{seller_id}")
            ],
            [
                InlineKeyboardButton("⏸️ Take Break", callback_data=f"seller_break_{seller_id}"),
                InlineKeyboardButton("🗑️ Clear All", callback_data=f"clear_all_queue_{seller_id}")
            ],
            [InlineKeyboardButton("❌ Close", callback_data=f"close_queue_view_{seller_id}")]
        ])
        
        await callback_query.message.edit_text(queue_text, reply_markup=queue_action_keyboard)
        await callback_query.answer()
        
    except Exception as e:
        print(f"Error in view_queue_callback: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# Handle process next buyer callback
@teleshop_bot.on_callback_query(filters.regex(r"^process_next_buyer_(\d+)"))
async def process_next_buyer_callback(client: Client, callback_query):
    try:
        seller_id = int(callback_query.data.split('_')[3])
        
        # Check authorization
        if callback_query.from_user.id != seller_id:
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
        
        # Check queue
        if not hasattr(client, 'buyer_queue') or seller_id not in client.buyer_queue:
            await callback_query.answer("No queue found.", show_alert=True)
            return
        
        queue = client.buyer_queue[seller_id]
        if not queue:
            await callback_query.answer("Queue is empty.", show_alert=True)
            return
        
        # Process next buyer
        next_buyer = queue.pop(0)
        
        # Import the function from buy.py
        from Modules.modules.buy import process_queued_buyer
        await process_queued_buyer(client, seller_id, next_buyer)
        
        await callback_query.answer("Processing next buyer!")
        await callback_query.message.edit_text(
            "⏭️ **Processing Next Buyer**\n\n"
            "Starting conversation with the next buyer in queue.\n"
            "You'll receive their details and can accept or reject the deal."
        )
        
        # If more buyers in queue, show updated options
        if client.buyer_queue[seller_id]:
            await handle_post_chat_queue_options(client, seller_id)
        
    except Exception as e:
        print(f"Error in process_next_buyer_callback: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# Handle seller break callback
@teleshop_bot.on_callback_query(filters.regex(r"^seller_break_(\d+)"))
async def seller_break_callback(client: Client, callback_query):
    try:
        seller_id = int(callback_query.data.split('_')[2])
        
        # Check authorization
        if callback_query.from_user.id != seller_id:
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
        
        await callback_query.answer("Taking a break - queue will wait!")
        
        # Get queue count
        queue_count = 0
        if hasattr(client, 'buyer_queue') and seller_id in client.buyer_queue:
            queue_count = len(client.buyer_queue[seller_id])
        
        break_text = (
            f"⏸️ **Taking a Break**\n\n"
            f"You've chosen to take a break from dealing with buyers.\n\n"
            f"📊 **Queue Status:**\n"
            f"• {queue_count} buyer(s) still waiting\n"
            f"• Queue will remain active\n"
            f"• You can resume anytime\n\n"
            f"💡 **Note:** Buyers will continue to wait. You can resume when ready."
        )
        
        resume_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("▶️ Resume Dealing", callback_data=f"resume_dealing_{seller_id}"),
                InlineKeyboardButton("👥 View Queue", callback_data=f"view_queue_{seller_id}")
            ],
            [InlineKeyboardButton("🗑️ Clear Queue", callback_data=f"clear_all_queue_{seller_id}")]
        ])
        
        await callback_query.message.edit_text(break_text, reply_markup=resume_keyboard)
        
    except Exception as e:
        print(f"Error in seller_break_callback: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# Handle resume dealing callback
@teleshop_bot.on_callback_query(filters.regex(r"^resume_dealing_(\d+)"))
async def resume_dealing_callback(client: Client, callback_query):
    try:
        seller_id = int(callback_query.data.split('_')[2])
        
        # Check authorization
        if callback_query.from_user.id != seller_id:
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
        
        await callback_query.answer("Resuming deal processing!")
        
        # Show queue options again
        await callback_query.message.edit_text("▶️ **Resuming Deal Processing**\n\nChecking your buyer queue...")
        await handle_post_chat_queue_options(client, seller_id)
        
    except Exception as e:
        print(f"Error in resume_dealing_callback: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# Handle clear all queue callback
@teleshop_bot.on_callback_query(filters.regex(r"^clear_all_queue_(\d+)"))
async def clear_all_queue_callback(client: Client, callback_query):
    try:
        seller_id = int(callback_query.data.split('_')[3])
        
        # Check authorization
        if callback_query.from_user.id != seller_id:
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
        
        # Clear the queue
        if hasattr(client, 'buyer_queue') and seller_id in client.buyer_queue:
            cleared_count = len(client.buyer_queue[seller_id])
            
            # Notify all queued buyers
            for buyer in client.buyer_queue[seller_id]:
                try:
                    await client.send_message(
                        buyer['buyer_id'],
                        "❌ **Queue Cleared**\n\n"
                        "The seller has cleared their buyer queue and is no longer accepting deals at this time.\n"
                        "You can try again later or browse other groups."
                    )
                except:
                    pass
            
            client.buyer_queue[seller_id] = []
            
            await callback_query.answer(f"Cleared {cleared_count} buyers from queue!")
            await callback_query.message.edit_text(
                f"🗑️ **Queue Cleared**\n\n"
                f"Removed {cleared_count} buyer(s) from your queue.\n"
                f"All waiting buyers have been notified.\n\n"
                "You can start fresh whenever you're ready to sell again."
            )
        else:
            await callback_query.answer("Queue was already empty.", show_alert=True)
        
    except Exception as e:
        print(f"Error in clear_all_queue_callback: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# Handle close queue view callback
@teleshop_bot.on_callback_query(filters.regex(r"^close_queue_view_(\d+)"))
async def close_queue_view_callback(client: Client, callback_query):
    try:
        seller_id = int(callback_query.data.split('_')[3])
        
        # Check authorization
        if callback_query.from_user.id != seller_id:
            await callback_query.answer("❌ Access denied!", show_alert=True)
            return
        
        await callback_query.answer("Queue view closed")
        await callback_query.message.delete()
        
        # Send a simple status message
        queue_count = 0
        if hasattr(client, 'buyer_queue') and seller_id in client.buyer_queue:
            queue_count = len(client.buyer_queue[seller_id])
        
        if queue_count > 0:
            from Modules.modules.start import get_main_keyboard
            await client.send_message(
                seller_id,
                f"📋 **Queue Status:** {queue_count} buyer(s) waiting\n"
                "Use the queue management features anytime to process them.",
                reply_markup=get_main_keyboard()
            )
        
    except Exception as e:
        print(f"Error in close_queue_view_callback: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# Function to be called when a chat ends
async def on_chat_ended(client: Client, seller_id: int, reason: str = "ended"):
    """Called when a chat ends to show queue options"""
    try:
        # Small delay to ensure chat cleanup is complete
        import asyncio
        await asyncio.sleep(1)
        
        # Check if seller has queued buyers
        if hasattr(client, 'buyer_queue') and seller_id in client.buyer_queue:
            queue = client.buyer_queue[seller_id]
            if queue:
                # Show post-chat options
                await handle_post_chat_queue_options(client, seller_id)
        
    except Exception as e:
        print(f"Error in on_chat_ended: {e}")
