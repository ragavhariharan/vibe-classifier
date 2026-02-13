# 🎵Vibe Classifier

A Machine Learning project that classifies songs into **Party, Workout, Sleep, or Study** based on their audio features.

## 🚀 Features
* **Custom Scraper:** Built with Selenium to gather real-time data from Tunebat.
* **Smart Classifier:** Uses a **Voting Ensemble** (Random Forest + Gradient Boosting + SVM) for improved accuracy.
* **Real-Time Prediction:** Enter any song name, and the AI predicts the vibe instantly.
* **Interactive Visuals:** 3D Scatter plot of the "Vibe Universe."

## 🛠️ Installation

1. **Clone the repo:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/spotify-vibe-classifier.git](https://github.com/YOUR_USERNAME/spotify-vibe-classifier.git)
   cd spotify-vibe-classifier

2. **Install dependencies:**
    pip install pandas scikit-learn selenium plotly seaborn matplotlib

## 🏃‍♂️ Usage

**To predict a song's vibe:**
    python predict_realtime.py

**To visualize the data:**
    python visualize_data.py

## 📊 Project Structure

    - scraper_final.py: The robust web scraper with popup handling.

    - train_model.py: Trains the Voting Classifier.

    - eda_report.py: Generates statistical reports and heatmaps.

    - predict_realtime.py: The main application interface.

## 🔮 Future Improvements
    Add lyrics analysis (NLP) to distinguish between sad pop songs and happy acoustic tracks.

    Increase dataset size to 2000+ songs for better generalization.
