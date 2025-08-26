# 🛍️ TeleShopBot - Digital Asset Marketplace

A comprehensive Telegram bot built with **Pyrogram** for buying and selling Telegram Groups, Channels, Bots, and other digital assets. Features professional UI, premium subscriptions, escrow services, and admin management tools.

## 🚀 Features

### 🛒 **Core Marketplace Features**
- **Buy Assets**: Browse and purchase Telegram Groups, Channels, Bots, and other digital assets
- **Sell Assets**: List your digital assets with custom pricing and descriptions
- **Asset Categories**: Groups, Channels, Bots, and Custom Assets
- **Year/Month Filtering**: Filter assets by creation date for better discovery
- **Sample Asset Database**: Pre-loaded with sample listings for demonstration

### 💰 **Premium Features**
- **Multiple Subscription Plans**: Monthly (₹199/$3) and Yearly (₹1999/$29) options
- **Enhanced Listing Features**: Priority placement, featured listings, advanced analytics
- **Commission Benefits**: Reduced marketplace fees for premium users
- **Priority Support**: Faster response times and dedicated assistance
- **Advanced Search Filters**: More precise asset discovery tools

### 🔐 **Escrow Services**
- **Secure Transactions**: Protected buying and selling with escrow protection
- **Multiple Options**: Direct sales or marketplace escrow services
- **Transaction History**: Complete record of all purchases and sales
- **Dispute Resolution**: Professional handling of transaction disputes

### 👤 **User Management**
- **Profile Dashboard**: Comprehensive user statistics and account management
- **Transaction History**: View all past purchases and sales
- **Listing Management**: Manage active and sold asset listings
- **Account Settings**: Customize preferences and privacy settings

### ⚙️ **Settings & Preferences**
- **Multi-Language Support**: English and Hindi (more coming soon)
- **Notification Controls**: Customize alerts and updates
- **Privacy Settings**: Control profile visibility and contact preferences
- **Display Preferences**: Customize bot interface and experience

### 🛡️ **Admin Panel**
- **Bot Statistics**: Comprehensive analytics dashboard
- **User Management**: Moderate users and handle reports
- **Listing Management**: Review and manage asset listings
- **Broadcast System**: Send announcements to all users
- **Financial Reports**: Track revenue and commission earnings

## 🏗️ **Project Structure**

```
TeleShopBot/
├── main.py                    # Bot entry point and startup
├── config.py                  # Configuration and settings
├── database.py                # MongoDB database operations
├── requirements.txt           # Python dependencies
├── Dockerfile                # Docker containerization
├── Procfile                  # Heroku deployment
├── runtime.txt               # Python runtime version
├── LICENSE                   # MIT License
├── README.md                 # This file
│
├── Modules/                  # Bot modules and plugins
│   ├── __init__.py          # Bot initialization
│   └── plugins/             # Feature plugins
│       ├── __init__.py      # Plugin initialization
│       ├── start.py         # Welcome and main menu
│       ├── buy.py           # Asset purchasing workflow
│       ├── sell.py          # Asset selling workflow
│       ├── profile.py       # User profile management
│       ├── premium.py       # Premium subscription system
│       ├── settings.py      # User preferences
│       └── admin.py         # Admin panel and tools
│
└── database/                # Legacy database files
    ├── __init__.py         # Database package init
    ├── users.py           # User data management
    ├── chats.py           # Chat management
    └── userStats.py       # User statistics
```

## 🔧 **Installation & Setup**

### **Prerequisites**
- Python 3.8+
- MongoDB (optional, bot works with sample data)
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Telegram API ID and Hash from [my.telegram.org](https://my.telegram.org)

### **Environment Setup**

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd TeleShopBot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file in the project root:
   ```env
   # Required Bot Settings
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token

   # Optional Database Settings
   MONGO_URI=mongodb://localhost:27017/
   DB_NAME=teleshopbot

   # Optional Admin Settings
   ADMIN_IDS=123456789,987654321
   LOG_GROUP=-100123456789

   # Optional Payment Settings (for future implementation)
   STRIPE_SECRET_KEY=your_stripe_key
   PAYPAL_CLIENT_ID=your_paypal_id
   RAZORPAY_KEY=your_razorpay_key
   ```

4. **Run the Bot**
   ```bash
   python main.py
   ```

## 🐳 **Docker Deployment**

### **Build and Run**
```bash
# Build the image
docker build -t teleshopbot .

# Run the container
docker run -d --name teleshopbot \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  teleshopbot
```

### **Docker Compose**
```yaml
version: '3.8'
services:
  bot:
    build: .
    env_file: .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - mongo

  mongo:
    image: mongo:latest
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

## ☁️ **Cloud Deployment**

### **Heroku Deployment**
1. Create a new Heroku app
2. Set environment variables in Heroku dashboard
3. Connect to GitHub repository
4. Deploy the `main` branch

### **Railway Deployment**
1. Connect Railway to your GitHub repository
2. Set environment variables
3. Deploy automatically on push

### **VPS Deployment**
1. Set up a VPS with Python 3.8+
2. Clone repository and install dependencies
3. Use PM2 or systemd for process management

## 📋 **Bot Commands**

### **User Commands**
- `/start` - Start the bot and show main menu
- `/help` - Get help and instructions
- `/profile` - View your profile and statistics
- `/buy` - Browse and buy assets
- `/sell` - List assets for sale
- `/premium` - View premium subscription options
- `/settings` - Configure bot preferences
- `/support` - Get help and support
- `/cancel` - Cancel current operation

### **Admin Commands** (Admin only)
- `/admin` - Access admin panel
- `/stats` - View bot statistics
- `/broadcast <message>` - Send message to all users

## 🎨 **User Interface**

The bot features a professional interface with:
- **Inline Keyboards**: Easy navigation with buttons
- **Rich Text Formatting**: Professional message styling
- **Progress Indicators**: Visual feedback for operations
- **Error Handling**: Graceful error messages and recovery
- **Multi-Language Support**: English and Hindi interfaces

## 🔒 **Security Features**

- **Input Validation**: All user inputs are validated and sanitized
- **Admin Protection**: Sensitive commands restricted to admins only
- **Escrow Services**: Secure transaction handling
- **Error Logging**: Comprehensive logging for security monitoring
- **Rate Limiting**: Protection against spam and abuse

## 🗄️ **Database Schema**

### **Users Collection**
```javascript
{
  user_id: Number,
  first_name: String,
  username: String,
  joined_date: Date,
  is_premium: Boolean,
  premium_expiry: Date,
  language: String,
  notifications_enabled: Boolean,
  total_purchases: Number,
  total_sales: Number,
  total_spent: Number,
  total_earned: Number,
  is_banned: Boolean,
  ban_reason: String
}
```

### **Assets Collection**
```javascript
{
  asset_id: String,
  seller_id: Number,
  asset_type: String, // "Group", "Channel", "Bot", "Other"
  title: String,
  description: String,
  price: Number,
  created_year: Number,
  created_month: Number,
  created_date: Date,
  status: String, // "active", "sold", "inactive"
  views: Number,
  is_featured: Boolean
}
```

### **Transactions Collection**
```javascript
{
  transaction_id: String,
  buyer_id: Number,
  seller_id: Number,
  asset_id: String,
  amount: Number,
  commission: Number,
  escrow_used: Boolean,
  status: String, // "pending", "completed", "cancelled"
  created_date: Date,
  completed_date: Date
}
```

## 🔧 **Configuration Options**

### **Bot Settings** (`config.py`)
- **Basic Settings**: Bot name, username, tokens
- **Feature Flags**: Enable/disable specific features
- **Pricing Settings**: Commission rates, premium pricing
- **Asset Categories**: Supported asset types
- **Language Support**: Available interface languages

### **Database Settings**
- **MongoDB Connection**: Connection string and database name
- **Collection Names**: Customize collection names
- **Connection Pooling**: Database connection optimization

### **Payment Integration** (Future)
- **Stripe Integration**: Credit card payments
- **PayPal Integration**: PayPal payments
- **Cryptocurrency**: Bitcoin, Ethereum support
- **Regional Payment**: UPI, Paytm, PhonePe (India)

## 🚀 **Future Roadmap**

### **Phase 2 Features**
- [ ] Real payment gateway integration
- [ ] Advanced asset verification system
- [ ] Review and rating system for sellers
- [ ] Asset promotion and featured listings
- [ ] Detailed analytics dashboard
- [ ] API for third-party integrations

### **Phase 3 Features**
- [ ] Mobile app companion
- [ ] Web dashboard for asset management
- [ ] Advanced search and filtering
- [ ] Asset auction system
- [ ] Bulk operations for sellers
- [ ] Advanced fraud detection

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: Full documentation in code comments
- **Issues**: Report bugs via GitHub issues
- **Contact**: Reach out for support and questions
- **Updates**: Follow for feature updates and announcements

## ⚡ **Performance**

- **Async Operations**: Full async/await implementation
- **Database Optimization**: Efficient MongoDB queries
- **Memory Management**: Optimized resource usage
- **Error Recovery**: Graceful error handling and recovery
- **Scalability**: Designed for high user loads

---

**Built with ❤️ using Pyrogram and Python**

*Transform your digital asset trading experience with TeleShopBot!*
