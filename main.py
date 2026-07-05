import os
import pymysql
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pyttsx3           #voice

print("[SYSTEM] Onion Market Prediction Project Starting...")

conn = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="rutujasumit",
    database="onionmarket"
)
cursor = conn.cursor()
print("[SUCCESS] Connected to database  successfully!")
def load_data():
    query = "SELECT * FROM onion_market"
    return pd.read_sql(query, conn)
df = load_data()
print(df)
print()
print(df.describe())
print()

avg_rainfall_mm = np.mean([df["rainfall_mm"]])
print("rainfall_mm:", avg_rainfall_mm) 
print()

os.makedirs("graphs", exist_ok=True)
plt.plot(df["year"], df["production_mmt"],color="green",marker="o",linestyle="dashed",linewidth=2,markersize=12)
plt.title("Onion_Market_Trend")
plt.xlabel("year")
plt.ylabel("production_mmt")
plt.savefig("graphs/year vs production graph.png", dpi=300, bbox_inches="tight")
plt.show()
plt.close()

# Stable Market Analysis
def show_stable_market_analysis_with_demand(dataframe):
    plt.figure(figsize=(11,6))  
    scatter = plt.scatter(
        dataframe["rainfall_mm"],
        dataframe["production_mmt"],
        s=dataframe["cultivated_area_hector"] * 150,   # bubblesize = area
        c=dataframe["demand_mmt"],            # bubble color = demand
        cmap = "YlOrRd",               # color ye,or,re
        alpha=0.85,
        edgecolors="black",
        linewidth=1.5,
        label="Yearly Market Data"
    )  
# year labels
    for i, txt in enumerate(dataframe["year"]):
        plt.annotate(txt, (dataframe["rainfall_mm"].iloc[i], dataframe["production_mmt"].iloc[i]),
                     textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, fontweight='bold')
# stable market zone 800 to 900 mm
    plt.axvspan(800, 900, color="green", alpha=0.12, label="Stable Market Zone (No Loss Region)")
# graph labels
    plt.title("Stable Market Equilibrium: Weather, Production & Demand Analysis", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Rainfall (mm) -> [Weather Condition]", fontsize=11)
    plt.ylabel("Onion Production (MMT) -> [Market Supply]", fontsize=11)

    plt.text(775, 24.5, " Dot Size = cultivated Area (Hector)", fontsize=9, color="darkblue", style="italic")
# Demand Color Bar
    cbar = plt.colorbar(scatter)
    cbar.set_label("Customer Demand (MMT)", fontsize=11, fontweight="bold")

    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc="upper left")
    plt.tight_layout()

    plt.savefig("graphs/stable_market_with_demand.png", dpi=300)
    plt.show()
    plt.close()
# function call
print("--- Generating Advanced Stable Market Graph With Demand ---")
show_stable_market_analysis_with_demand(df)
print()


class OnionMarket:
    def __init__(self, historical_dataframe):

        self.df = historical_dataframe
        self.total_years = len(historical_dataframe)
# Historical Rain Average calculation
        self.avg_rain_historical = historical_dataframe["rainfall_mm"].mean()
# Average per Hectoe calculation
        avg_production = historical_dataframe["production_mmt"].mean()
        avg_area = historical_dataframe["cultivated_area_hector"].mean()
        self.base_yield = avg_production / avg_area if avg_area > 0 else 16.5

        self.domestic_demand_benchmark = historical_dataframe["demand_mmt"].mean()

#Converting LMT to MMT 3 LMT = 0.3 MMT 
        latest_buffer_lmt = historical_dataframe["buffer_stock_lmt"].iloc[-1]
        self.current_buffer_stock_mmt = latest_buffer_lmt / 10.0
#  Average wastage Rate calculation
        avg_waste_mmt = (historical_dataframe["waste_onion_lmt"].mean()) / 10.0
        self.wastage_rate = avg_waste_mmt / avg_production if avg_production > 0 else 0.07
#  Voice engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)     # speed

        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "english" in voice.name.lower() or "zira" in voice.name.lower() or "david" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def speak_advisory(self, text_to_speak):
        try:
            self.engine.say(text_to_speak)
            self.engine.runAndWait()
        except:
            pass
    def predict_next_year_with_advisory(self, target_year, next_rainfall, next_area):
# Logi Based SQL Historical trends
        if next_rainfall < (self.avg_rain_historical - 50):
            predicted_production = next_area * (self.base_yield * 0.82)      # Drought Risk
            # predicted_cultivated_area_hector = self.avg_cultivated_area_hector_historical * 1.5
            market_demand="High"
            decision = f"YES (Highly Recommended - Low rain means less supply, so prices and demand will be HIGH in {target_year})"

        elif next_rainfall > (self.avg_rain_historical + 100):
            predicted_production = next_area * (self.base_yield * 0.70)      # Heavy Rain / Rotting Risk
            # predicted_cultivated_area_hector = self.avg_cultivated_area_hector_historical * 1.3
            market_demand="Fluctuating (Risk of Crop Damage)"
            decision = f"CAUTION (High risk - Excessive rainfall in {target_year} might  destroy the crop!)"

        else:
            predicted_production = next_area * (self.base_yield * 1.05)
            market_demand="Stable / Normal"
            decision = f"YES (Stable Market Situation - Safe to plant with expected steady profits in {target_year})"
# Calculated Wastage Onion 
        wasted_onion_mmt = predicted_production * self.wastage_rate
        wasted_onion_lmt = wasted_onion_mmt * 10.0          # convert lmt for display
        net_usable_production = predicted_production - wasted_onion_mmt

# Total available stock = Net Crop Production + Existinf Buffer Stock
        total_onion_available =net_usable_production + self.current_buffer_stock_mmt

        extra_onion = 0.0
        export_status = ""
        govt_advisory_eng = ""
        voice_msg_english = ""
# Govr. Policy Logic & Dynamic Advisories
        if total_onion_available > (self.domestic_demand_benchmark + 3.0):
           extra_onion = total_onion_available - self.domestic_demand_benchmark
           export_status = f"🔴 OPEN EXPORT IMMEDIATELY ({extra_onion:.2f} MMT)"
            
           govt_advisory_eng = (
                f"   -> Attention Farmers: National buffer stock is heavily surplus.\n"
                f"   -> Advice: Reduce your cultivation area for {target_year} to avoid a market crash.\n"
                f"   -> Policy: Government is opening international export channels immediately."
            )
           voice_msg_english = (
               f"Attention farmers. National stock is in heavy surplus. "
               f"To avoid market crash and losses, please reduce cultivation area for {target_year}."
            )

        elif total_onion_available < self.domestic_demand_benchmark:
            export_status = "❌ STRICT BAN ON ONION EXPORT"
            
            govt_advisory_eng = (
                f"   -> Attention Farmers: National buffer stock is insufficient.\n"
                f"   -> Advice: Grow onions in an OPTIMAL quantity; local prices will be highly profitable.\n"
                f"   -> Policy: Strict export ban enforced to secure domestic supply."
            )
            voice_msg_english = (
                f"Attention farmers. National stock is running low. "
                f"Please plant an optimal quantity. Local market prices will be highly profitable."
            )

        else:
            export_status = "🟢 NORMAL CONTROLLED EXPORT"
            govt_advisory_eng = (
                f"   -> Market conditions are highly stable and balanced for {target_year}.\n"
                f"   -> Advice: Follow your regular farming plan.\n"
                f"   -> Policy: Normal controlled export; farmers will secure steady profit margins."
            )
            voice_msg_english = (
                f"Market conditions for {target_year} are highly stable. "
                f"Production and demands are balanced. Expect steady profits."
            )
#  output display
        print("\n" + "="*90)
        print(f"[SYSTEM] PRE_SHOWING EARLY WARNING SYASTEM FOR YEAR: {target_year}")
        print("="*90)
        print(f"Predicted Gross Production           : {predicted_production:.2f} MMT")
        print(f"Estimated Onion Wastage              : {wasted_onion_lmt:.2f} LMT [Based on SQL Historic Wate Trend]")
        print(f"Net Uasble Crop Production           : {net_usable_production:.2f} MMT")
        print(f"Expected Market Demand               : {market_demand}")
        print(f"Predicted_Total Market area          : {next_area:.2f} Million Hector")
        print(f"DICISION (Should you plant?)         : {decision}")
        print("-" * 90)
        print(f"Current Govt Buffer Stock           : {self.current_buffer_stock_mmt * 10.0:.2f} LMT ")
        print(f"Total Usable Stock Available        : {total_onion_available:.2f} MMT")
        print(f"Government Export Policy            : {export_status}")
        print("-" * 90)
        print(f"[OFFICIAL ADVISORY FOR FARMERS AND MARKETS FOR YEAR {target_year}]")
        print(govt_advisory_eng)
        print("="*90 + "\n")
# Audio Alert
        print("Playing Official English Audio Advisory...")
        self.speak_advisory(voice_msg_english)

        return net_usable_production
# Terminal Input
Market = OnionMarket(df)
print("\n --- ENTER YOUR PREDICTION TARGET DATA ----")
try:
    next_yr = int(input("1. Enter target year for prediction (e.g., 2026/2027): "))
    next_yr_rain = float(input("2. Enter expected rainfall in mm (e.g., 600 to 1000): "))
    next_yr_area = float(input("3. Enter target cultivated area in Million Hectares (e.g., 1.2 to 2.5):"))
except ValueError:
    print("Invalid Input! Using Default Placeholder Datasets.")
    next_yr = 2026
    next_yr_rain = 840.0
    next_yr_area = 1.9
# Prediction
predicted_prod = Market.predict_next_year_with_advisory(next_yr, next_yr_rain, next_yr_area)
# Graph
print("--- Generating Future Trend Prediction Graph ---")
past_years = df["year"].tolist()
past_rain = df["rainfall_mm"].tolist()
past_production = df["production_mmt"].tolist()

predicted_year = next_yr
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Rainfall Graph
ax1.plot(past_years, past_rain, color="blue", marker="o", linestyle="-", linewidth=2, label="SQL Past Rain")
ax1.scatter(predicted_year, next_yr_rain, color="red", marker="*", s=250, zorder=5, label=f"Predicted year {predicted_year} Rain")
ax1.set_title("Rainfall Trend: Past vs Next Year Prediction", fontsize=11, fontweight="bold")
ax1.set_xlabel("Year")
ax1.set_ylabel("Rainfall (mm)")
ax1.grid(True, linestyle="--", alpha=0.5)
ax1.legend()
# Production Graph
ax2.plot(past_years, past_production, color="green", marker="s", linestyle="-", linewidth=2, label="SQL Past Production")
ax2.scatter(predicted_year, predicted_prod, color="red", marker="*", s=250, zorder=5, label=f"Predicted year {predicted_year} Production")
ax2.set_title("Onion Production (Net) : Past vs Next Year Prediction", fontsize=11, fontweight="bold")
ax2.set_xlabel("Year")
ax2.set_ylabel("Production (mmt)")
ax2.grid(True, linestyle="--", alpha=0.5)
ax2.legend()

plt.suptitle(f"Onion Market Future Situation Prediction for Year {predicted_year}", fontsize=14, fontweight="bold")
plt.tight_layout()

if not os.path.exists("graphs"):
        os.makedirs("graphs")
plt.savefig("graphs/final_market_prediction_graph.png", dpi=300)
print("[SUCCESS] Graph saved to 'graphs/final_market_prediction_graph.png'")
plt.show()
plt.close()

conn.close()
print("[SUCCESS] Project Executed Successfully!")




