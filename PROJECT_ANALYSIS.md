# 🎵 Spotify Vibe Classifier - Comprehensive Technical Documentation

## 1. Project Overview
The "Spotify Vibe Classifier" is a machine learning project designed to categorize songs into one of four distinct "vibes" (Party, Workout, Sleep, or Study) by analyzing their acoustic features. The project encompasses an end-to-end data science lifecycle, featuring an automated web scraping pipeline built with Selenium, custom data preprocessing, explorative analyses, and a soft-voting ensemble model. Moreover, the project is capable of real-time predictive inference where users can submit a song title, after which the application autonomously scrapes the song's characteristics and produces a vibe prediction.

## 2. Problem Statement
**Goal:** Automate the categorization of music to facilitate appropriate playlist curation without the need for manual listening.

Music evokes different emotional and physical responses, yet manually labeling thousands of tracks for a particular activity (e.g., studying vs. working out) is a tedious process. This project solves that by defining empirical boundaries for subjective song "vibes" using quantifiable acoustic characteristics, ultimately automating mood-based musical classification.

## 3. Dataset Description
* **Raw Data (`party.txt`, `workout.txt`, `sleep.txt`, `study.txt`):** Curated text lists of song titles and artists serving as seed queries.
* **Scraped Data (`final_dataset.csv`):** The output from the Tunebat scraping engine containing roughly ~700 rows of uncleaned, raw metrics.
* **Processed Data (`cleaned_dataset.csv`):** The final analytical dataset containing valid numerical features without erroneous measurements.
* **Target Variable:** `Vibe` (Categorical: 'Party', 'Workout', 'Sleep', 'Study').
* **Features:**
    * `Energy` (Integer 0-100): The intensity and activity level of the track.
    * `Danceability` (Integer 0-100): Suitability of the track for dancing.
    * `Happiness` (Integer 0-100): The musical positiveness (valence) conveyed by a track.
    * `Loudness` (Float, dB): The overall loudness of a track in decibels (typically negative values).
* **Data Sources:** Real-time extraction from [Tunebat.com](https://tunebat.com/) directly from the DOM using Selenium.
* **Data Issues:** Occasional parsing failures producing `0,0,0,0` metrics or empty values (due to bot-protection or search mismatch), duplicate entries, and string-formatted numeric data (`" dB"` suffix) requiring structural cleaning. 

## 4. Data Preprocessing Pipeline
Implemented in `clean_data.py`. 

* **Cleaning:** 
  - Removes entirely erroneous rows where `Energy` equals exactly 0 (indicating the scraper failed to find legitimate stats).
  - Handles missing entries by dropping rows that contain `NaN` values.
* **Formatting/Parsing:** Strips the `" dB"` suffix from the `Loudness` column and strictly enforces numeric type casting using `pd.to_numeric()`.
* **Deduplication:** Filters out redundant song rows keeping only unique matches subset over the `Song Name` column.
* **Feature Engineering:** (Conducted downstream in `train_model.py` and `eda_report.py`)
  - `Intensity` = `Energy * Danceability`
  - `Vocal_Proxy` = `Loudness / (Energy + 0.001)` (A heuristic estimating vocal prominence).
  - `Depression_Score` = `(100 - Happiness) * (100 - Energy)`
* **Scaling:** `StandardScaler` from scikit-learn standardizes features (mean=0, variance=1) enabling distance-based algorithms like SVM to process feature sets correctly. 
* **Libraries:** `pandas` for dataframe manipulation, `scikit-learn` for scaling matrices.

## 5. EDA Insights
Exploratory Data Analysis is executed via `eda_report.py` and visually rendered via `visualize_data.py`.

* **Descriptive Stats (`summary_statistics.csv`):** Establishes the bounds and distributions of song parameters.
* **Correlation Analysis (`correlation_heatmap.png`):** Generates a Pearson correlation matrix allowing the team to identify feature multicollinearity.
* **Visual Diagnostics (`energy_boxplot.png`, `vocal_proxy_boxplot.png`):** Boxplots empirically validate that 'Party' and 'Workout' subsets display statistically significant deviations in Energy compared to 'Sleep' and 'Study' sets.
* **3D Virtualization (`vibe_graph.html`):** An interactive Plotly 3D scatter plot plots Energy vs. Loudness vs. Danceability. It maps discrete clusters where different vibes structurally occupy different coordinate quadrants in the "Vibe Universe".

## 6. Models Used
Implemented within `train_model.py`.

* **Model Type:** Multi-Class Classification.
* **Ensemble Strategy:** A 'Soft' Voting Classifier (`VotingClassifier`). It aggregates the predicted probabilities from three distinct "Expert" algorithms and averages them to declare a majority outcome.
* **Base Algorithms:**
  1. **Random Forest Classifier (`n_estimators=100`):** Combines multiple decision trees. Chosen to navigate complex, non-linear feature relationships and reduce variance.
  2. **Gradient Boosting Classifier (`n_estimators=100`):** Iteratively builds sequential trees to correct previous errors. Chosen for high predictive accuracy by reducing bias.
  3. **Support Vector Classifier (`probability=True`):** Constructs hyperplanes in higher-dimensional space. Chosen to effectively isolate distinct boundaries between overlapping genres.

## 7. Training & Evaluation
* **Validation Strategy:** Hold-out validation splitting using `train_test_split()`. Uses an 80/20 train/test split.
* **Stratification:** Utilizes `stratify=y` to guarantee proportional representation of all four vibes in both training and test data segments, protecting against severe class imbalance.
* **Metrics:** Utilizes `accuracy_score` combined with a detailed `classification_report` (Precision, Recall, F1-Score support).
* **Generalization Check:** The usage of a heterogeneous voting ensemble inherently mitigates overfitting risk by neutralizing individual model biases.

## 8. Prediction Pipeline
> [!NOTE]
> The prediction architecture allows both manual feature insertions and automated natural language track name interpretation via web extraction.

* **Flow:** The prediction process flows sequentially through `predict_realtime.py` (automated web querying) or `predict_vibe.py` (manual input).
* **Execution (Real-Time):** 
  1. **Input** -> User prompts string query in CLI.
  2. **Processing** -> Selenium browser invisibly executes, queries Tunebat, mitigates popups, scrapes the 4 core audio characteristics, and terminates.
  3. **Preprocessing** -> Feature engineering functions construct `Intensity`, `Vocal_Proxy`, and `Depression_Score`. Data flows into the pickled `scaler.transform()`.
  4. **Model** -> Vectors feed forward through `model.predict()` and `model.predict_proba()`.
  5. **Output** -> Results format on the CLI explicitly outlining percentage confidences per categorical vibe.
* **Deployment Readiness:** Currently operating natively as a local localized console utility representing a POC pipeline. It lacks web-routing protocols.

## 9. Folder & File Structure
* **`README.md`**: Project overview, installation steps, and structure scope.
* **`scraper_setup.py`**: Localized POC (proof-of-concept) configuration script isolating the fundamental DOM scraping targets explicitly for tuning locators.
* **`scraper_final.py`**: The fully-featured automated web scraper encompassing element-waits, cookie handling, and auto-saves to CSV.
* **`party.txt`,  `workout.txt`,  `sleep.txt`,  `study.txt`**: Dictionary seed sets comprising song titles and respective artists mappings.
* **`sanitize_sources.py`**: A utility payload executing deletion routines targeting duplicate text query strings within the seed files.
* **`final_dataset.csv`**: Raw compilation of scraped values.
* **`clean_data.py`**: Pandas pipeline resolving mismatched datatypes, dropping zeros and stripping noise strings.
* **`cleaned_dataset.csv`**: Master schema dataframe curated for algorithmic ingress.
* **`eda_report.py`**: Engine generating plots highlighting descriptive mathematical metrics utilizing seaborn maps.
* **`summary_statistics.csv`**: Quantitative boundary metrics representing column values.
* **`correlation_heatmap.png`, `energy_boxplot.png`, `vocal_proxy_boxplot.png`**: Visual analytic artifacts defining density relationships.
* **`visualize_data.py`**: Script invoking Plotly to generate 3d data environments.
* **`vibe_graph.html`**: Compiled interactable plot mapping coordinate metrics of songs.
* **`train_model.py`**: Main orchestrator triggering feature manipulations, executing SVM/Forest/Boosting training, and managing artifact dumps `.pkl`.
* **`spotify_vibe_model.pkl`**: Target serialized binary maintaining operational weights for inference logic.
* **`scaler.pkl`**: Encoded structure to ensure continuous feature mean/variance alignment.
* **`predict_vibe.py`**: Offline interface enforcing user metric ingestion purely predicting results over hardcoded integer injections.
* **`predict_realtime.py`**: Dynamic interface connecting real-time Chrome DOM abstraction capabilities straight into the ML engine.

## 10. Tech Stack
* **Language:** Python 3.x
* **Data Sourcing:** `selenium`
* **Data Processing:** `pandas`, `numpy`
* **Machine Learning:** `scikit-learn`
* **Visualization:** `plotly`, `matplotlib`, `seaborn`
* **Object Serialization:** `joblib`

## 11. Results & Metrics
* The usage of the `VotingClassifier` guarantees structural stability across prediction tasks. 
* By executing the `classification_report`, the pipeline evaluates independent label classifications (Precision) over comprehensive recall coverage across sub-genres.
* Feature augmentations (`Vocal_Proxy`, `Depression_Score`) directly increase the algorithmic separation allowing complex margins to distinguish overlapping acoustic patterns better safely.

## 12. Limitations
> [!WARNING]
> Web-scraping solutions via Selenium introduce severe maintenance constraints. If Tunebat natively updates HTML/CSS identifiers, the pipeline completely halts natively requiring manual regex mappings and code updates.

* **Performance Constraints:** Launching Chromium iteratively for every generic prediction loop intrinsically bottlenecks UX, causing 5–15 seconds of execution overhead purely due to browser instantiations.
* **Initial Bias:** Operating exclusively from 4 statically defined query files dictates the model only inherits the limited variability provided in those text blocks initially without automated continuous growth strategies.

## 13. Improvement Suggestions
> [!TIP]
> Prioritize replacing Selenium extraction with formal APIs to instantly multiply platform efficiency and reliability.

* **API Interfacing:** Migrate entirely away from automated scraping methodologies toward authorized interactions utilizing `Spotipy` (Spotify Official API's `audio_features` endpoint). This eliminates wait times, CAPTCHA blockage, and DOM instabilities permanently.
* **Architecture Modernization:** Decouple prediction logic exclusively from the console exposing operations via `FastAPI`. This provides standard HTTP REST payload handling ensuring client interfaces (mobile, web) can reliably interact cross-platform cleanly.
* **Systematic Tuning:** Incorporate rigorous Hyperparameter testing methodologies systematically utilizing Cross-Validation iterations to refine base estimator values effectively avoiding bias mapping natively manually implemented.
* **Expanded Neural Inputs:** Feed textual lyrics metadata natively processed through NLP Transformers appending semantics directly adjoining the mathematical parameters representing dual-layered emotion recognition paradigms.
