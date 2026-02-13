import pandas as pd
import plotly.express as px

# 1. Load your clean data
df = pd.read_csv('cleaned_dataset.csv')

# 2. Create the Interactive Graph
# We will plot Energy vs. Loudness vs. Danceability
fig = px.scatter_3d(df, 
                    x='Energy', 
                    y='Loudness', 
                    z='Danceability',
                    color='Vibe',                 # Color dots by Vibe
                    hover_name='Song Name',       # Show song name on hover
                    opacity=0.7,                  # Make dots slightly see-through
                    title='🎵 The Spotify Vibe Universe 🎵',
                    color_discrete_map={          # Custom Colors
                        'Party': '#ff00ff',   # Neon Pink
                        'Sleep': '#0000ff',   # Blue
                        'Study': '#00ff00',   # Green
                        'Workout': '#ff0000'  # Red
                    })

# 3. Save it as an HTML file (Webpage)
fig.write_html("vibe_graph.html")

print("✅ Graph generated! Open 'vibe_graph.html' in your browser.")