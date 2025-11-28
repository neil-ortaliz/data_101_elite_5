# Pokémon TCG Dashboard

A comprehensive interactive dashboard built with **Dash** and **Plotly** to track, analyze, and visualize Pokémon Trading Card Game (TCG) market data and personal card collections.

## Features

### Views

1. **Market View**
   - Treats Pokémon card sets like a stock market.
   - Displays **top movers** for both sets and individual cards.
   - Interactive charts for price trends and performance.

2. **Portfolio View**
   - Shows all cards in your collection.
   - Visualizes **distribution of sets**, ROI, and card statistics.
   - Provides insights into your collection performance.

3. **Card View**
   - Focuses on a single card, showing market trends.
   - Compares **ungraded vs graded cards**.
   - ROI analysis with bar charts to determine if grading is worth it.

4. **Catalogue Page**
   - Allows you to select and log cards in your collection.
   - Supports input of quantity and date collected

## Data

- **Sources:** Market data and portfolio data are taken from the Pokemon Price Tracker API.
- **Card Grades:** Supports tracking of ungraded and graded cards with price and ROI metrics.


## Installation
1. Clone the repository:
```bash
git clone https://github.com/neil-ortaliz/data_101_elite_5/
cd data_101_elite_5
cd pokemon_tcg_dashboard 
```
2. Ensure your current directory is the `pokemon_tcg_dashboard`
3. Setup a virtual environment (Optional but Recommended)
```bash
python -m venv venv
```
To activate it:
macOS/Linux
```bash
source venv/bin/activate
```

Windows
```bash
venv\Scripts\activate
```
4. Install dependencies
```bash
pip install -r requirements.txt
```
5. Run the code `python app.py` in your terminal
6. Open your browser and go to:
```bash
http://127.0.0.1:8050/
```
   
