from Modules import StoreDB
from datetime import datetime
from pytz import timezone

async def add_group_listing(group_data: dict):
    """Add a new group listing to the database"""
    try:
        if 'status' not in group_data:
            group_data['status'] = 'active'
            
        seller_id = group_data.get('seller_id')
        if seller_id:
            # Update user statistics in MongoDB
            user_stats = await StoreDB.user_stats.find_one({"user_id": seller_id})
            if not user_stats:
                await StoreDB.user_stats.insert_one({
                    "user_id": seller_id,
                    "groups_listed": 1,
                    "groups_sold": 0,
                    "groups_bought": 0,
                    "total_deals": 0,
                    "member_since": group_data.get('created_at', 'Unknown')
                })
            else:
                await StoreDB.user_stats.update_one(
                    {"user_id": seller_id},
                    {"$inc": {"groups_listed": 1}}
                )
        
        # Add to MongoDB
        await StoreDB.listings.insert_one(group_data)
        
        print(f"Successfully added group listing: {group_data.get('name', 'Unknown')} by user {seller_id}")
        return True
        
    except Exception as e:
        print(f"Error adding group listing: {e}")
        return False

async def fetch_group_listings():
    """Fetch all active group listings from database"""
    try:
        print("Fetching all group listings")
        
        # Filter out sold groups and removed listings
        query = {
            "status": {"$ne": "sold"}, 
            "removed_from_listings": {"$ne": True}
        }
        
        listings = await StoreDB.listings.find(query).to_list(length=100)
        
        print(f"Found {len(listings)} active group listings")
        return listings
        
    except Exception as e:
        print(f"Error fetching group listings: {e}")
        return []

async def fetch_user_groups(user_id):
    """Fetch all groups listed by a specific user"""
    try:
        print(f"Fetching groups for user {user_id}")
        
        query = {
            "seller_id": user_id,
            "status": {"$ne": "sold"}
        }
        
        user_groups = await StoreDB.listings.find(query).to_list(length=100)
        
        print(f"Found {len(user_groups)} groups for user {user_id}")
        return user_groups
        
    except Exception as e:
        print(f"Error fetching user groups: {e}")
        return []

async def check_group_exists(group_id):
    """Check if a group already exists in listings"""
    try:
        print(f"Checking if group {group_id} exists in listings")
        
        query = {
            "group_id": group_id,
            "status": {"$ne": "sold"}
        }
        
        group = await StoreDB.listings.find_one(query)
        
        if group:
            print(f"Group {group_id} already exists in listings")
        else:
            print(f"Group {group_id} not found in listings")
            
        return group
        
    except Exception as e:
        print(f"Error checking group exists: {e}")
        return None

async def update_user_activity(user_id, activity_type="general"):
    """Update user's last activity timestamp"""
    try:
        india_tz = timezone('Asia/Kolkata')
        current_time = datetime.now(india_tz).strftime('%d-%b-%Y %I:%M %p')
        
        await StoreDB.user_activities.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "last_activity": current_time,
                    "last_activity_type": activity_type
                },
                "$setOnInsert": {
                    "first_seen": current_time,
                    "user_id": user_id
                }
            },
            upsert=True
        )
        
        print(f"User {user_id} activity updated: {activity_type} at {current_time}")
        return True
        
    except Exception as e:
        print(f"Error updating user activity: {e}")
        return False

async def update_deal_statistics(user_id, deal_type):
    """Update user's deal statistics (sold/bought counts)"""
    try:
        # Initialize user stats if not exists
        user_stats = await StoreDB.user_stats.find_one({"user_id": user_id})
        if not user_stats:
            india_tz = timezone('Asia/Kolkata')
            current_time = datetime.now(india_tz).strftime('%d-%b-%Y %I:%M %p')
            
            await StoreDB.user_stats.insert_one({
                "user_id": user_id,
                "groups_listed": 0,
                "groups_sold": 0,
                "groups_bought": 0,
                "total_deals": 0,
                "member_since": current_time
            })
        
        # Update the specific deal type counter
        update = {"$inc": {"total_deals": 1}}
        if deal_type == 'sold':
            update["$inc"]["groups_sold"] = 1
        elif deal_type == 'bought':
            update["$inc"]["groups_bought"] = 1
        
        await StoreDB.user_stats.update_one(
            {"user_id": user_id},
            update
        )
        
        print(f"Updated {deal_type} statistics for user {user_id}")
        return True
        
    except Exception as e:
        print(f"Error updating deal statistics: {e}")
        return False

async def get_user_statistics(user_id):
    """Get comprehensive user statistics including sold groups"""
    try:
        # Get stored statistics or create default
        stored_stats = await StoreDB.user_stats.find_one({"user_id": user_id}) or {}
        
        # Count current active listings
        current_listings = await StoreDB.listings.count_documents({
            "seller_id": user_id,
            "status": {"$ne": "sold"}
        })
        
        # Count all sold listings by this user
        sold_listings = await StoreDB.listings.count_documents({
            "seller_id": user_id,
            "status": "sold"
        })
        
        # Count groups bought by this user
        bought_listings = await StoreDB.listings.count_documents({
            "buyer_id": user_id,
            "status": "sold"
        })
        
        # Calculate total deals
        total_deals = sold_listings + bought_listings
        
        # Calculate success rates
        total_listed = current_listings + sold_listings
        sell_success_rate = f"{(sold_listings / total_listed * 100):.1f}%" if total_listed > 0 else "0%"
        buy_success_rate = f"{(bought_listings / total_deals * 100):.1f}%" if total_deals > 0 else "0%"
        
        # Calculate earnings and spending (placeholder values)
        total_earnings = f"${sold_listings * 8}"
        total_spent = f"${bought_listings * 8}"
        
        stats = {
            'groups_listed': current_listings,
            'groups_sold': sold_listings,
            'groups_bought': bought_listings,
            'total_deals': total_deals,
            'total_earnings': total_earnings,
            'total_spent': total_spent,
            'deals_initiated': stored_stats.get('deals_initiated', 0),
            'sell_success_rate': sell_success_rate,
            'buy_success_rate': buy_success_rate,
            'member_since': stored_stats.get('member_since', 'Unknown'),
            'last_activity': stored_stats.get('last_activity', 'Unknown'),
            'user_rating': stored_stats.get('user_rating', 'N/A')
        }
        
        print(f"Statistics for user {user_id}: {current_listings} active, {sold_listings} sold, {bought_listings} bought")
        return stats
        
    except Exception as e:
        print(f"Error getting user statistics: {e}")
        return {
            'groups_listed': 0,
            'groups_sold': 0,
            'groups_bought': 0,
            'total_deals': 0,
            'total_earnings': '$0',
            'total_spent': '$0',
            'deals_initiated': 0,
            'sell_success_rate': '0%',
            'buy_success_rate': '0%',
            'member_since': 'Unknown',
            'last_activity': 'Unknown',
            'user_rating': 'N/A'
        }

async def mark_group_as_sold(group_id, buyer_id=None):
    """Mark a group as sold and update statistics"""
    try:
        india_tz = timezone('Asia/Kolkata')
        current_time = datetime.now(india_tz).strftime('%d-%b-%Y %I:%M %p')
        
        update = {
            "$set": {
                "status": "sold",
                "sold_at": current_time
            }
        }
        
        if buyer_id:
            update["$set"]["buyer_id"] = buyer_id
        
        result = await StoreDB.listings.update_one(
            {"group_id": group_id},
            update
        )
        
        if result.modified_count > 0:
            print(f"Group {group_id} marked as sold" + (f" to buyer {buyer_id}" if buyer_id else ""))
            return True
        
        print(f"Group {group_id} not found in storage")
        return False
        
    except Exception as e:
        print(f"Error marking group as sold: {e}")
        return False

async def remove_group_from_listings(group_id):
    """Mark group as sold but keep record for statistics"""
    try:
        india_tz = timezone('Asia/Kolkata')
        current_time = datetime.now(india_tz).strftime('%d-%b-%Y %I:%M %p')
        
        # Get the group to find seller_id
        group = await StoreDB.listings.find_one({"group_id": group_id})
        
        if group:
            # Mark as sold but keep the record
            await StoreDB.listings.update_one(
                {"group_id": group_id},
                {
                    "$set": {
                        "status": "sold",
                        "sold_at": current_time,
                        "removed_from_listings": True
                    }
                }
            )
            
            # Update seller's statistics
            seller_id = group.get('seller_id')
            if seller_id:
                await StoreDB.user_stats.update_one(
                    {"user_id": seller_id},
                    {"$inc": {"groups_listed": -1}}
                )
            
            print(f"Group {group_id} marked as sold and removed from buyer listings")
            return True
        
        print(f"Group {group_id} not found in listings storage")
        return False
        
    except Exception as e:
        print(f"Error removing group from listings: {e}")
        return False

async def get_user_deals_count(user_id):
    """Get count of deals initiated by user (for buying statistics)"""
    try:
        # This would require a deals collection - implement with MongoDB
        count = await StoreDB.deals.count_documents({"buyer_id": user_id})
        return count
        
    except Exception as e:
        print(f"Error getting user deals count: {e}")
        return 0

async def get_user_premium_status(user_id):
    """Get user's premium subscription status"""
    try:
        premium = await StoreDB.premium_subscriptions.find_one({"user_id": user_id, "status": "active"})
        
        if premium:
            return {
                'is_premium': True,
                'expires_at': premium.get('expires_at'),
                'auto_renew': premium.get('auto_renew', False),
                'subscription_type': premium.get('subscription_type', 'premium')
            }
        
        return {
            'is_premium': False,
            'expires_at': None,
            'auto_renew': False,
            'subscription_type': 'free'
        }
        
    except Exception as e:
        print(f"Error getting premium status: {e}")
        return {'is_premium': False, 'expires_at': None, 'auto_renew': False, 'subscription_type': 'free'}

async def activate_premium_subscription(user_id, duration_days=30):
    """Activate premium subscription for a user"""
    try:
        from datetime import datetime, timedelta
        
        india_tz = timezone('Asia/Kolkata')
        now = datetime.now(india_tz)
        expires_at = now + timedelta(days=duration_days)
        
        subscription_data = {
            "user_id": user_id,
            "status": "active",
            "subscribed_at": now,
            "expires_at": expires_at,
            "duration_days": duration_days,
            "auto_renew": False,
            "payment_method": "telegram_stars"
        }
        
        await StoreDB.premium_subscriptions.update_one(
            {"user_id": user_id},
            {"$set": subscription_data},
            upsert=True
        )
        
        print(f"Premium subscription activated for user {user_id} until {expires_at}")
        return True
        
    except Exception as e:
        print(f"Error activating premium subscription: {e}")
        return False

def get_premium_expiry_date():
    """Get formatted premium expiry date (30 days from now)"""
    from datetime import datetime, timedelta
    
    india_tz = timezone('Asia/Kolkata')
    expiry = datetime.now(india_tz) + timedelta(days=30)
    return expiry.strftime('%d-%b-%Y %I:%M %p')

async def add_user_rating(user_id, rating):
    """Add a rating for a user"""
    try:
        india_tz = timezone('Asia/Kolkata')
        current_time = datetime.now(india_tz).strftime('%d-%b-%Y %I:%M %p')
        
        await StoreDB.user_ratings.insert_one({
            "user_id": user_id,
            "rating": rating,
            "timestamp": current_time
        })
        
        print(f"Rating {rating}/5 added for user {user_id} at {current_time}")
        return True
        
    except Exception as e:
        print(f"Error adding user rating: {e}")
        return False

async def get_user_rating(user_id):
    """Get user's average rating and total ratings with improved display"""
    try:
        user_ratings = await StoreDB.user_ratings.find({"user_id": user_id}).to_list(length=100)
        
        if not user_ratings:
            return {
                'average_rating': 0.0,
                'total_ratings': 0,
                'rating_display': "No ratings yet"
            }
        
        # Calculate average
        total_ratings = len(user_ratings)
        total_score = sum(r['rating'] for r in user_ratings)
        average_rating = total_score / total_ratings
        
        return {
            'average_rating': average_rating,
            'total_ratings': total_ratings,
            'rating_display': f"({average_rating:.1f}/5.0) - {total_ratings} reviews"
        }
        
    except Exception as e:
        print(f"Error getting user rating: {e}")
        return {
            'average_rating': 0.0,
            'total_ratings': 0,
            'rating_display': "No ratings yet"
        }

async def get_premium_usage_stats(user_id):
    """Get premium usage statistics for a user"""
    try:
        stats = await StoreDB.premium_usage.find_one({"user_id": user_id}) or {
            'priority_views': 0,
            'extra_deals': 0,
            'reports_generated': 0,
            'features_used': 0,
            'extra_revenue': '₹0',
            'time_saved': '0 hours',
            'roi': '0%'
        }
        
        return stats
        
    except Exception as e:
        print(f"Error getting premium usage stats: {e}")
        return {
            'priority_views': 0,
            'extra_deals': 0,
            'reports_generated': 0,
            'features_used': 0,
            'extra_revenue': '₹0',
            'time_saved': '0 hours',
            'roi': '0%'
        }

async def mark_group_as_sold_with_buyer(group_id, buyer_id):
    """Mark a group as sold and record the buyer information"""
    try:
        india_tz = timezone('Asia/Kolkata')
        current_time = datetime.now(india_tz).strftime('%d-%b-%Y %I:%M %p')
        
        result = await StoreDB.listings.update_one(
            {"group_id": group_id},
            {
                "$set": {
                    "status": "sold",
                    "sold_at": current_time,
                    "buyer_id": buyer_id,
                    "removed_from_listings": True
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"Group {group_id} marked as sold to buyer {buyer_id}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error marking group as sold with buyer: {e}")
        return False

async def get_all_transactions():
    """Get all completed transactions for admin dashboard"""
    try:
        query = {
            "status": "sold",
            "buyer_id": {"$exists": True}
        }
        
        completed_deals = await StoreDB.listings.find(query).to_list(length=100)
        
        print(f"Found {len(completed_deals)} completed transactions")
        return completed_deals
        
    except Exception as e:
        print(f"Error getting all transactions: {e}")
        return []

async def get_user_purchase_history(user_id):
    """Get groups purchased by a user"""
    try:
        query = {
            "buyer_id": user_id,
            "status": "sold"
        }
        
        purchased_groups = await StoreDB.listings.find(query).to_list(length=100)
        return purchased_groups
        
    except Exception as e:
        print(f"Error getting user purchase history: {e}")
        return []

async def get_user_sales_history(user_id):
    """Get groups sold by a user"""
    try:
        query = {
            "seller_id": user_id,
            "status": "sold"
        }
        
        sold_groups = await StoreDB.listings.find(query).to_list(length=100)
        return sold_groups
        
    except Exception as e:
        print(f"Error getting user sales history: {e}")
        return []

async def get_user_settings(user_id):
    """Get user's settings with defaults"""
    try:
        settings = await StoreDB.user_settings.find_one({"user_id": user_id})
        
        # Return default settings if none exist
        if not settings:
            default_settings = {
                "user_id": user_id,
                "min_seller_rating": None,
                "max_price": None,
                "min_price": None,
                "creation_year_filter": None,
                "min_members": None,
                "sort_by": "default",
                "sort_order": "descending",
                "anonymous_mode": True,
                "notifications": True
            }
            # Create default settings in database
            await StoreDB.user_settings.insert_one(default_settings)
            return default_settings
        
        return settings
        
    except Exception as e:
        print(f"Error getting user settings: {e}")
        return {
            "user_id": user_id,
            "min_seller_rating": None,
            "max_price": None,
            "min_price": None,
            "creation_year_filter": None,
            "min_members": None,
            "sort_by": "default",
            "sort_order": "descending",
            "anonymous_mode": True,
            "notifications": True
        }

async def update_user_settings(user_id, settings_update):
    """Update user's settings"""
    try:
        await StoreDB.user_settings.update_one(
            {"user_id": user_id},
            {"$set": settings_update},
            upsert=True
        )
        
        print(f"Updated settings for user {user_id}: {settings_update}")
        return True
        
    except Exception as e:
        print(f"Error updating user settings: {e}")
        return False

async def fetch_filtered_group_listings(user_id):
    """Fetch group listings with user's filters and sorting applied"""
    try:
        print(f"Fetching filtered group listings for user {user_id}")
        
        # Get user settings
        user_settings = await get_user_settings(user_id)
        
        # Build MongoDB query based on filters
        query = {
            "status": {"$ne": "sold"}, 
            "removed_from_listings": {"$ne": True}
        }
        
        # Apply price filters
        price_conditions = {}
        if user_settings.get("min_price") is not None:
            price_conditions["$gte"] = user_settings["min_price"]
        if user_settings.get("max_price") is not None:
            price_conditions["$lte"] = user_settings["max_price"]
        
        if price_conditions:
            # Extract numeric value from price string (e.g., "$10" -> 10)
            query["$expr"] = {
                "$and": [
                    {"$gte": [{"$toInt": {"$substr": ["$price", 1, -1]}}, price_conditions.get("$gte", 0)]},
                    {"$lte": [{"$toInt": {"$substr": ["$price", 1, -1]}}, price_conditions.get("$lte", 9999)]}
                ]
            }
        
        # Apply member count filter
        if user_settings.get("min_members") is not None:
            query["actual_members"] = {"$gte": user_settings["min_members"]}
        
        # Apply creation year filter
        year_filter = user_settings.get("creation_year_filter")
        if year_filter:
            if year_filter == "2024":
                query["year"] = "2024"
            elif year_filter == "2023_2024":
                query["year"] = {"$in": ["2023", "2024"]}
            elif year_filter == "2022_2024":
                query["year"] = {"$in": ["2022", "2023", "2024"]}
            elif year_filter == "2020_2024":
                query["year"] = {"$in": ["2020", "2021", "2022", "2023", "2024"]}
            elif year_filter == "old":
                query["year"] = {"$in": ["2016", "2017", "2018", "2019"]}
        
        # Fetch listings
        listings = await StoreDB.listings.find(query).to_list(length=100)
        
        # Apply seller rating filter (requires separate rating lookup)
        min_rating = user_settings.get("min_seller_rating")
        if min_rating is not None and min_rating > 0:
            filtered_listings = []
            for listing in listings:
                seller_rating = await get_user_rating(listing["seller_id"])
                if seller_rating["total_ratings"] == 0 and min_rating <= 1:
                    # Include new sellers only if min rating is 1 or less
                    filtered_listings.append(listing)
                elif seller_rating["average_rating"] >= min_rating:
                    filtered_listings.append(listing)
            listings = filtered_listings
        
        # Apply sorting
        sort_by = user_settings.get("sort_by", "default")
        sort_order = user_settings.get("sort_order", "descending")
        
        if sort_by == "price":
            listings.sort(
                key=lambda x: int(x.get("price", "$0")[1:]),
                reverse=(sort_order == "descending")
            )
        elif sort_by == "members":
            listings.sort(
                key=lambda x: x.get("actual_members", 0),
                reverse=(sort_order == "descending")
            )
        elif sort_by == "rating":
            # Sort by seller rating (requires async rating lookup - simplified for now)
            pass  # Complex sorting, implement if needed
        elif sort_by == "date":
            listings.sort(
                key=lambda x: x.get("created_at", ""),
                reverse=(sort_order == "descending")
            )
        # Default sorting is newest first (no additional sorting needed)
        
        print(f"Found {len(listings)} filtered listings for user {user_id}")
        return listings
        
    except Exception as e:
        print(f"Error fetching filtered group listings: {e}")
        # Fallback to unfiltered listings
        return await fetch_group_listings()
