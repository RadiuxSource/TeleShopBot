#!/usr/bin/env python3
"""
TeleShopBot Premium Plugin
Handles premium features and subscription
"""

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import Settings
from Modules import teleshop_bot

# ============================================
# PREMIUM INFORMATION AND FEATURES
# ============================================

async def show_premium_info(client: Client, message: Message, edit: bool = True):
    """
    Display premium features and benefits
    """
    try:
        premium_message = f"""
✨ **Upgrade to Premium**

Unlock exclusive features and benefits with TeleShopBot Premium!

**🎯 Premium Benefits:**
• 🏆 **Priority Support** - Get priority in buying and selling matters
• 🔒 **Free Escrow Support** - No escrow fees on transactions
• ⭐ **Featured Listings** - Your assets get highlighted placement
• 💰 **No Extra Commissions** - Keep more of your earnings
• 🔔 **High-Rate Group Notifications** - Get alerts for premium opportunities
• 📊 **Advanced Analytics** - Detailed insights on your performance
• 🎨 **Custom Profile Badge** - Show your premium status
• 🚀 **Early Access** - Be first to try new features

**💳 Pricing:**
• **Monthly:** ₹{Settings.PREMIUM_PRICE_INR}/month (${Settings.PREMIUM_PRICE_USD})
• **Yearly:** ₹{Settings.PREMIUM_PRICE_INR * 10}/year (${Settings.PREMIUM_PRICE_USD * 10}) - Save 17%!

**🔥 Limited Time Offer:**
Get 50% OFF your first month! Use code: **WELCOME50**

**Why Choose Premium?**
• Trusted by 10,000+ users
• 99.9% uptime guarantee  
• 24/7 premium support
• Money-back guarantee

Ready to upgrade your experience?
"""
        
        premium_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"💳 Buy Premium (₹{Settings.PREMIUM_PRICE_INR}/month)", callback_data="premium_buy_monthly"),
            ],
            [
                InlineKeyboardButton(f"💰 Buy Yearly (Save 17%!)", callback_data="premium_buy_yearly"),
            ],
            [
                InlineKeyboardButton("📋 Learn More", callback_data="premium_learn_more"),
                InlineKeyboardButton("❓ Premium FAQ", callback_data="premium_faq")
            ],
            [
                InlineKeyboardButton("💬 Contact Sales", url=Settings.SUPPORT_CHAT),
                InlineKeyboardButton("👑 Premium Support", callback_data="premium_support")
            ],
            [
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")
            ]
        ])
        
        if edit:
            await message.edit_text(
                premium_message,
                reply_markup=premium_keyboard,
                disable_web_page_preview=True
            )
        else:
            await message.reply_text(
                premium_message,
                reply_markup=premium_keyboard,
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"❌ Error showing premium info: {e}")

async def show_premium_learn_more(client: Client, message: Message):
    """
    Show detailed premium features
    """
    try:
        learn_more_message = """
📋 **Premium Features Detailed**

**🏆 Priority Support:**
• Dedicated premium support team
• Response within 1 hour (vs 24 hours for free)
• Direct line to senior support agents
• Phone support available

**🔒 Free Escrow Support:**
• Save $0.5 per transaction 
• Risk-free buying and selling
• Professional mediation service
• Dispute resolution priority

**⭐ Featured Listings:**
• 3x more visibility for your assets
• Highlighted in search results  
• Premium badge on listings
• Mobile app promotion

**💰 No Extra Commissions:**
• 0% platform commission (vs 2% for free)
• Keep 100% of your earnings
• No hidden fees
• Transparent pricing

**🔔 High-Rate Group Notifications:**
• Exclusive access to premium groups
• Early alerts for high-value assets
• Curated opportunities
• Investment-grade assets

**📊 Advanced Analytics:**
• Revenue tracking dashboard
• Market trend analysis
• Performance insights
• Export capabilities

**🎨 Custom Profile Badge:**
• Premium crown on your profile
• Increased buyer trust
• Higher conversion rates
• Professional appearance

**🚀 Early Access:**
• Beta features before public release
• Input on new feature development
• Exclusive premium community
• Monthly premium webinars
"""
        
        back_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💳 Subscribe Now (₹{Settings.PREMIUM_PRICE_INR}/month)", callback_data="premium_buy_monthly")],
            [InlineKeyboardButton("🔙 Back to Premium", callback_data="main_premium")]
        ])
        
        await message.edit_text(
            learn_more_message,
            reply_markup=back_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error showing learn more: {e}")

async def show_premium_faq(client: Client, message: Message):
    """
    Show premium FAQ
    """
    try:
        faq_message = """
❓ **Premium FAQ**

**Q: How does premium billing work?**
A: You're billed monthly/yearly. Cancel anytime - no contracts!

**Q: Can I cancel my subscription?**
A: Yes! Cancel anytime from your profile settings. No cancellation fees.

**Q: Do I get a refund if I cancel?**
A: Yes, we offer prorated refunds within 30 days of purchase.

**Q: What payment methods do you accept?**
A: We accept UPI, cards, net banking, wallets, and crypto payments.

**Q: Is my payment information secure?**
A: Yes, we use industry-standard encryption and never store card details.

**Q: Can I upgrade from monthly to yearly?**
A: Yes! Contact support and we'll help you switch plans.

**Q: Do premium features work immediately?**
A: Yes! Premium features are activated instantly after payment.

**Q: Can I use premium features on multiple devices?**
A: Yes, your premium account works across all devices where you're logged in.

**Q: What happens if I don't renew?**
A: You'll keep access until your current period ends, then switch to free features.

**Q: Do you offer premium for teams/businesses?**
A: Yes! Contact our sales team for enterprise plans and bulk discounts.

**Q: Is there a free trial?**
A: We offer 50% off your first month instead of a trial period.

**Q: How do I get premium support?**
A: Premium users get access to our priority support channel with faster response times.
"""
        
        faq_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Still Have Questions?", url=Settings.SUPPORT_CHAT)],
            [InlineKeyboardButton(f"💳 Get Premium Now", callback_data="premium_buy_monthly")],
            [InlineKeyboardButton("🔙 Back to Premium", callback_data="main_premium")]
        ])
        
        await message.edit_text(
            faq_message,
            reply_markup=faq_keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"❌ Error showing premium FAQ: {e}")

async def handle_premium_purchase(client: Client, callback_query: CallbackQuery, plan: str):
    """
    Handle premium subscription purchase
    """
    try:
        user_id = callback_query.from_user.id
        
        if plan == "monthly":
            price_inr = Settings.PREMIUM_PRICE_INR
            price_usd = Settings.PREMIUM_PRICE_USD
            duration = "1 month"
        else:  # yearly
            price_inr = Settings.PREMIUM_PRICE_INR * 10
            price_usd = Settings.PREMIUM_PRICE_USD * 10
            duration = "1 year"
        
        purchase_message = f"""
💳 **Premium Subscription Checkout**

**Selected Plan:** {plan.title()} Premium
**Duration:** {duration}
**Price:** ₹{price_inr} (${price_usd})

🚧 **Payment Integration Coming Soon!**

We're currently integrating payment processors:
• Razorpay (UPI, Cards, Net Banking)
• Stripe (International cards)
• PayPal (Global payments)
• Crypto payments (Bitcoin, Ethereum, USDT)

**For now, you can upgrade manually:**

1. Contact our support team
2. Make payment via your preferred method
3. Get instant premium activation
4. Enjoy all premium benefits!

**💰 Payment Methods Available:**
• UPI: teleshopbot@upi
• Bank Transfer: Contact for details
• PayPal: support@teleshopbot.com
• Crypto: Contact for wallet address

**🎉 Special Offer:**
Mention code **EARLY50** for 50% off your first month!
"""
        
        purchase_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Contact for Payment", url=Settings.SUPPORT_CHAT)],
            [InlineKeyboardButton("📋 Payment Instructions", callback_data="premium_payment_help")],
            [InlineKeyboardButton("🔙 Back to Premium", callback_data="main_premium")]
        ])
        
        await callback_query.message.edit_text(
            purchase_message,
            reply_markup=purchase_keyboard,
            disable_web_page_preview=True
        )
        
        # Notify admins about premium interest
        if Settings.LOG_GROUP:
            admin_message = f"""
💰 **Premium Subscription Interest**

**User:** {user_id}
**Plan:** {plan.title()}
**Price:** ₹{price_inr} (${price_usd})

User is interested in premium subscription. Follow up for manual processing.
"""
            try:
                await teleshop_bot.send_message(Settings.LOG_GROUP, admin_message)
            except Exception as e:
                print(f"⚠️ Could not notify admins: {e}")
        
    except Exception as e:
        print(f"❌ Error handling premium purchase: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# ============================================
# CALLBACK QUERY HANDLERS
# ============================================

@teleshop_bot.on_callback_query(filters.regex("^premium_"))
async def premium_callback_handler(client: Client, callback_query: CallbackQuery):
    """
    Handle premium-related callback queries
    """
    try:
        data = callback_query.data
        message = callback_query.message
        await callback_query.answer()
        
        if data == "premium_learn_more":
            await show_premium_learn_more(client, message)
            
        elif data == "premium_faq":
            await show_premium_faq(client, message)
            
        elif data == "premium_buy_monthly":
            await handle_premium_purchase(client, callback_query, "monthly")
            
        elif data == "premium_buy_yearly":
            await handle_premium_purchase(client, callback_query, "yearly")
            
        elif data == "premium_support":
            support_message = """
👑 **Premium Support**

Get dedicated premium support with:
• Priority response (within 1 hour)
• Direct access to senior agents
• Phone support available
• Dedicated premium support channel

**Contact Premium Support:**
• Telegram: @TeleShopBotPremium
• Email: premium@teleshopbot.com
• Phone: +1-xxx-xxx-xxxx

**Not premium yet?**
Upgrade now to get instant access to premium support!
"""
            
            support_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📞 Premium Support Chat", url="https://t.me/TeleShopBotPremium")],
                [InlineKeyboardButton("📧 Email Support", url="mailto:premium@teleshopbot.com")],
                [InlineKeyboardButton(f"✨ Upgrade to Premium", callback_data="premium_buy_monthly")],
                [InlineKeyboardButton("🔙 Back", callback_data="main_premium")]
            ])
            
            await message.edit_text(
                support_message,
                reply_markup=support_keyboard,
                disable_web_page_preview=True
            )
            
        elif data == "premium_payment_help":
            payment_help_message = """
💳 **Premium Payment Instructions**

**Step 1: Contact Support**
• Send message: "I want to upgrade to Premium"
• Mention your preferred payment method
• Include promo code if you have one

**Step 2: Payment**
Choose your preferred method:

**🇮🇳 For Indian Users:**
• UPI: teleshopbot@paytm
• PhonePe: 9876543210
• Google Pay: 9876543210
• Bank Transfer: Account details provided

**🌐 For International Users:**
• PayPal: support@teleshopbot.com
• Bank Transfer: SWIFT details provided
• Crypto: Wallet address provided

**Step 3: Confirmation**
• Send payment screenshot
• Mention your User ID: `{callback_query.from_user.id}`
• Premium activated within 10 minutes!

**💰 Current Prices:**
• Monthly: ₹{Settings.PREMIUM_PRICE_INR} (${Settings.PREMIUM_PRICE_USD})
• Yearly: ₹{Settings.PREMIUM_PRICE_INR * 10} (${Settings.PREMIUM_PRICE_USD * 10})

**🎉 Promo Code: EARLY50**
Get 50% off your first month!
"""
            
            back_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Start Payment Process", url=Settings.SUPPORT_CHAT)],
                [InlineKeyboardButton("🔙 Back", callback_data="main_premium")]
            ])
            
            await message.edit_text(
                payment_help_message,
                reply_markup=back_keyboard,
                disable_web_page_preview=True
            )
            
    except Exception as e:
        print(f"❌ Error in premium callback handler: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

# ============================================
# EXPORT FUNCTIONS
# ============================================

__all__ = [
    "show_premium_info",
    "show_premium_learn_more",
    "show_premium_faq",
    "handle_premium_purchase"
]
