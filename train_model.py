import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 1. Load Data
df = pd.read_csv('cleaned_dataset.csv')

# 2. Feature Engineering
df['Intensity'] = df['Energy'] * df['Danceability']
df['Vocal_Proxy'] = df['Loudness'] / (df['Energy'] + 0.001)
df['Depression_Score'] = (100 - df['Happiness']) * (100 - df['Energy'])

# 3. Prepare Inputs
X = df.drop(['Song Name', 'Vibe'], axis=1)
y = df['Vibe']

# 4. Scaling (Required for SVM)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 5. Split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training 'The Committee' on {len(X_train)} songs...")

# 6. Define the 3 Experts
clf1 = RandomForestClassifier(n_estimators=100, random_state=42)
clf2 = GradientBoostingClassifier(n_estimators=100, random_state=42)
clf3 = SVC(probability=True, random_state=42) # SVM

# 7. Create the Voting Classifier (Hard Vote)
# They will vote. Majority wins.
eclf = VotingClassifier(estimators=[
    ('rf', clf1), ('gb', clf2), ('svm', clf3)], voting='soft')

eclf.fit(X_train, y_train)

# 8. Evaluate
predictions = eclf.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("\n" + "="*30)
print(f"🎯 Voting Model Accuracy: {accuracy * 100:.2f}%")
print("="*30)

print("\nDetailed Report:")
print(classification_report(y_test, predictions))

# 9. Save
joblib.dump(eclf, 'spotify_vibe_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("💾 Voting Model saved!")