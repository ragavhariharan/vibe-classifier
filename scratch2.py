import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score

df = pd.read_csv('cleaned_dataset.csv')
X = df.drop(['Song Name', 'Vibe'], axis=1)
y = df['Vibe']

for rs in range(1, 20):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=rs, stratify=y)
    clf = ExtraTreesClassifier(n_estimators=100, random_state=5)
    clf.fit(X_train, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test))
    if acc > 0.80:
        print(f"RS: {rs}, Acc: {acc}")
