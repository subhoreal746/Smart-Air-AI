import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib


df = pd.read_csv("cleaned_air_data.csv")


X = df[['gas_voltage', 'voltage_change']]
y = df['is_spike']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


print("🧠 Training the AI model...")
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)


accuracy = model.score(X_test, y_test)
print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")


joblib.dump(model, "air_quality_model.pkl")
print("💾 Model saved as 'air_quality_model.pkl'")
