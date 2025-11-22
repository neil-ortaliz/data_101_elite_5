# Pokémon TCG Analytics Dashboard - User Guide

## Welcome! 🎴

This dashboard helps you track Pokémon card prices, manage your collection, and make smart buying/selling decisions.

---

## Getting Started

### What You'll See

The dashboard has 3 main sections:

1. **Market View** - See all cards and price trends
2. **Portfolio View** - Manage your personal collection  
3. **Portfolio Picker** - Select cards to add to your portfolio

---

## Market View

### Overview Metrics

At the top, you'll see 4 summary cards:

- **Total Market Value**: Combined value of all tracked cards
- **24h Change**: How much the market moved today
- **Best Performing Set**: Which set gained the most value
- **Active Listings**: How many cards are currently for sale

### Filters

Use these to find specific cards:

- **Search bar**: Type card name
- **Set dropdown**: Filter by Pokémon set
- **Rarity dropdown**: Filter by rarity type
- Click "Clear Filters" to reset

### Time Period Selection

Use the dropdown to change the time period for viewing data:
- 24 Hours
- 7 Days
- 1 Month
- 3 Months
- 1 Year

### Set Performance Chart

Shows which Pokémon sets have had the biggest price changes recently.

- **Green bars** = Price went up ↑
- **Red bars** = Price went down ↓

### Top Movers Table

Shows cards with biggest price changes.

- **Blue numbers** = Price went up ↑
- **Orange numbers** = Price went down ↓

**How to use:**
1. Click column headers to sort
2. Use "Gainers/Losers" toggle to filter
3. View top 20 cards with largest price movements

---

## Portfolio View

### Your Portfolio Summary

Top section shows your personal stats:

- **Total Portfolio Value**: What your collection is worth now
- **Total Gain/Loss**: How much you've made/lost
- **Number of Cards**: How many cards you own
- **Average Card Value**: Average worth per card

### Portfolio Performance Charts

View detailed visualizations of your portfolio:
- **Portfolio Performance vs Market**: Compare your returns to overall market
- **Collection Breakdown by Set**: See which sets dominate your collection
- **Grade Distribution**: Compare your card grades to market averages

### Risk Indicators

Three badges show your portfolio health:

- **Diversity Score**
  - **Green (High)**: Well-diversified across multiple sets
  - **Yellow (Medium)**: Some concentration
  - **Red (Low)**: Heavy concentration risk

- **Volatility Rating**
  - **Green (Low/Stable)**: Stable prices expected
  - **Yellow (Medium/Moderate)**: Some price fluctuations expected
  - **Red (High)**: High price volatility expected

- **Market Exposure**
  - **Green (Low)**: Low concentration in any single card
  - **Yellow (Medium)**: Moderate concentration
  - **Red (High)**: High concentration risk

Hover over the info icon (ⓘ) next to each badge for detailed explanations.

### Holdings Table

Detailed list of all your cards:

- **Card Name**: Name of the card
- **Set**: Which set it's from
- **Qty**: How many you own
- **Buy Price**: What you paid originally
- **Current Price**: What it's worth now
- **Gain/Loss**: Total profit or loss (in dollars)
- **%**: Percentage gain or loss

**How to use:**
1. Click "➕ Add Card to Portfolio" to add new cards
2. Click column headers to sort by any field
3. Blue numbers show gains, orange shows losses
4. Shows up to 25 cards per page

---

## Card View

### Card Details Header

When viewing a specific card, you'll see:

**Left Side:**
- Large card image (hover to zoom)

**Right Side:**
- **Card Name**: Full card name
- **Set Badge**: Which set it's from
- **Rarity Badge**: Card rarity
- **Card Number**: Position in the set (e.g., #125/197)
- **Current Market Price**: Large, prominent price display
- **Quick Stats**:
  - PSA 10 Price: Value if graded perfect
  - Ungraded Price: Raw card value
  - Total Listings: How many are for sale
  - Market Trend: Current price direction

### Action Buttons

Three buttons let you take action:

1. **➕ Add to Portfolio** (Green)
   - Adds this card to your personal collection
   
2. **🔔 Set Price Alert** (Yellow, outlined)
   - Get notified when price hits your target
   
3. **📤 Share Card** (Blue, outlined)
   - Share card details with friends

### Charts and Analysis

Below the header, you'll find:
- Price history charts
- Grading analysis
- ROI calculations
- Market comparisons

*(Note: These sections are populated by other team members' work)*

---

## Portfolio Picker

### Selecting Cards

1. Browse the grid of Pokémon cards
2. Use filters to narrow down by Set or Rarity
3. Use search bar to find specific cards
4. Click a card to select it (blue border appears)
5. Selected cards are automatically added to your portfolio
6. Click "Clear Selected Cards" to deselect all

### Pagination

- Use "Prev" and "Next" buttons to browse pages
- Shows 100 cards per page
- Page counter shows current page (e.g., "Page 1 / 27")

### Filters

- **Filter by Set**: Choose one or multiple sets
- **Filter by Rarity**: Choose one or multiple rarities
- **Search**: Type any text to search across all card details

---

## Common Questions (FAQ)

**Q: How often do prices update?**  
A: Prices update every 24 hours at midnight.

**Q: Where does the data come from?**  
A: We aggregate data from eBay, TCGPlayer, and major Pokémon card stores.

**Q: Can I export my portfolio?**  
A: Portfolio export functionality is currently in development.

**Q: What does "PSA 10" mean?**  
A: PSA is a grading company. PSA 10 is a perfect condition card - the highest grade possible.

**Q: How do I delete a card from my portfolio?**  
A: Currently this feature is being developed by the team. For now, you can track which cards to remove manually.

**Q: Why are some features not working?**  
A: Some interactive features (like callbacks for filters and buttons) require additional development work from other team members.

**Q: What's the difference between "Owned Cards" and "Portfolio" tabs?**  
A: "Owned Cards" shows the visual grid of cards you've selected. "Portfolio" shows detailed analytics and performance metrics.

---

## Troubleshooting

### Filters not working
- Make sure you've selected valid options
- Try clicking "Clear Filters" and starting over
- Refresh the page (F5 or Cmd+R)
- Note: Some filter functionality requires callbacks that may still be in development

### Charts not loading
- Try a different browser (Chrome recommended)
- Clear browser cache
- Disable browser extensions that might block content
- Check your internet connection

### Cards not appearing in Portfolio Picker
- Check your filter settings - you may have filtered out all cards
- Make sure you're connected to the internet
- Try refreshing the page
- Clear the search box

### Risk badges not showing tooltips
- Make sure you're hovering directly over the ⓘ symbol
- Try a different browser
- Some older browsers may not support tooltips

### Tables not sorting
- Click directly on the column header text
- Wait a moment for the sort to process
- Try refreshing if sorting seems stuck

---

## Tips for Success

1. **Track regularly**: Check your portfolio weekly to stay updated on value changes
2. **Use filters**: Save time by filtering to what matters most to you
3. **Monitor trends**: Watch the Top Movers table for buying/selling opportunities
4. **Diversify**: Don't put all your money in one card or set - spread risk
5. **Research first**: Use the Market View data to research before buying
6. **Set alerts**: Use price alerts to catch good deals (when feature is available)
7. **Check risk indicators**: Regularly review your portfolio's risk analysis
8. **Compare grades**: Look at PSA 10 prices to decide if grading is worth it

---

## Understanding the Data

### Price Data
- **Current Price**: Latest market price based on recent sales
- **24h Change**: Price movement in last 24 hours
- **7d Change**: Price movement in last 7 days
- **PSA 10 Price**: Average price for professionally graded perfect cards
- **Ungraded Price**: Average price for raw (ungraded) cards

### Portfolio Metrics
- **Total Portfolio Value**: Sum of current prices for all your cards
- **Original Cost Basis**: Total amount you paid for all cards
- **Unrealized Gain/Loss**: Profit/loss if you sold everything today
- **30-Day Change**: How much your portfolio value changed this month

### Risk Metrics
- **Diversity Score**: Measures how spread out your collection is
- **Volatility Rating**: Measures expected price fluctuation
- **Market Exposure**: Measures concentration risk in single cards

---

## Color Guide

Throughout the dashboard, we use consistent colors:

- **Blue (#1E90FF)**: Positive changes, gains, upward trends
- **Orange (#FF8C00)**: Negative changes, losses, downward trends
- **Gray (#808080)**: Neutral or no change
- **Green**: Success actions, good risk levels, stable metrics
- **Yellow**: Warning, moderate risk, caution needed
- **Red**: Danger, high risk, urgent attention needed

---

## For Team Members: Adding Documentation

If you're a team member working on other features, add your documentation sections here:

### [SECTION NAME] - Member X

[Add your feature documentation here following the format above]

**Example structure:**
- What the feature does
- How to use it
- Common issues
- Tips

---

## Technical Notes

### Browser Compatibility
- **Recommended**: Chrome, Firefox, Safari (latest versions)
- **Mobile**: Responsive design works on phones and tablets
- **Not supported**: Internet Explorer

### Data Update Schedule
- Market prices: Updated daily at 12:00 AM UTC
- Set performance: Updated daily
- Portfolio values: Calculated in real-time based on latest prices

### Privacy & Data
- Portfolio data is stored in your browser session
- No personal data is collected or stored on servers
- Clear your browser data to reset your portfolio

---

## Need Help?

📧 Email: support@pokemontcgdashboard.com  
💬 Discord: [Join our community]  
📚 More guides: [Visit our help center]  
🐛 Report bugs: [GitHub Issues]

---

## Version History

- **v1.0** - Initial release with Market View, Portfolio View, and Portfolio Picker
  - Member 1: UI/Layout Components ✅
  - Member 2: Data Processing (in progress)
  - Member 3: Charts & Visualizations (in progress)
  - Member 4: Advanced Features (in progress)
  - Member 5: Callbacks & Testing (in progress)

---

**Happy collecting! Gotta Price 'Em All! 🎴💰**