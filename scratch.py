import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

df = pd.read_csv('cleaned_dataset.csv')

# FE
df['Intensity'] = df['Energy'] * df['Danceability']
df['Vocal_Proxy'] = df['Loudness'] / (df['Energy'] + 0.001)
df['Depression_Score'] = (100 - df['Happiness']) * (100 - df['Energy'])
df['Energy_Loud_Ratio'] = df['Energy'] / (abs(df['Loudness']) + 0.01)

X = df.drop(['Song Name', 'Vibe'], axis=1)
y = df['Vibe']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

model = Pipeline([
    ('scaler', StandardScaler()),
    ('poly', PolynomialFeatures(degree=3, include_bias=False)),
    ('clf', HistGradientBoostingClassifier(random_state=42, max_iter=300, l2_regularization=0.1))
])

model.fit(X_train, y_train)
preds = model.predict(X_test)
print("Accuracy poly HGB:", accuracy_score(y_test, preds))

clf2 = Pipeline([
    ('scaler', StandardScaler()),
    ('poly', PolynomialFeatures(degree=2, include_bias=False)),
    ('clf', ExtraTreesClassifier(n_estimators=400, random_state=42, max_depth=None))
])
clf2.fit(X_train, y_train)
print("Accuracy poly ET:", accuracy_score(y_test, clf2.predict(X_test)))

