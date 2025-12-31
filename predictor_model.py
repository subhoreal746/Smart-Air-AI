import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Load the cleaned data
df = pd.read_csv("cleaned_air_data.csv")

# 2. Features (X) and Target (y)
# We want the AI to look at the current voltage and how fast it's changing
X = df[['gas_voltage', 'voltage_change']]
y = df['is_spike']

# 3. Split into Training and Testing sets
# This keeps some data aside to 'test' the AI later
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Create and Train the Model (The Brain)
print("🧠 Training the AI model...")
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 5. Check Accuracy
accuracy = model.score(X_test, y_test)
print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")

# 6. Save the model to a file
joblib.dump(model, "air_quality_model.pkl")
print("💾 Model saved as 'air_quality_model.pkl'")
