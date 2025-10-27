# main para el dashboard

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="NBA Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("nba_all_elo.csv")
    return df

nba_data = load_data()

# Título del dashboard
st.title("NBA Dashboard - Análisis de Temporadas")

# Barra lateral
with st.sidebar:
    st.header("Filtros")
    
    year_list = sorted(nba_data['year_id'].unique().tolist())
    selected_year = st.selectbox(
        'Seleccionar año:',
        year_list,
        index=len(year_list)-1
    )
    
    teams_in_year = sorted(nba_data[nba_data['year_id'] == selected_year]['team_id'].unique().tolist())
    selected_team = st.selectbox(
        'Seleccionar equipo:',
        teams_in_year,
        index=0
    )
    
    game_type = st.pills(
        "Tipo de juegos:",
        options=["Temporada Regular", "Playoffs", "Ambos"],
        default="Ambos"
    )

def filter_data(df, year, team, game_type):
    filtered = df[(df['year_id'] == year) & (df['team_id'] == team)].copy()
    
    if game_type == "Temporada Regular":
        filtered = filtered[filtered['is_playoffs'] == 0]
    elif game_type == "Playoffs":
        filtered = filtered[filtered['is_playoffs'] == 1]
    
    return filtered

filtered_data = filter_data(nba_data, selected_year, selected_team, game_type)

filtered_data = filtered_data.sort_values('date_game')

filtered_data['wins_cumsum'] = (filtered_data['game_result'] == 'W').cumsum()
filtered_data['losses_cumsum'] = (filtered_data['game_result'] == 'L').cumsum()

total_wins = (filtered_data['game_result'] == 'W').sum()
total_losses = (filtered_data['game_result'] == 'L').sum()
total_games = len(filtered_data)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Acumulado de Victorias y Derrotas - {selected_team} ({selected_year})")
    
    if len(filtered_data) > 0:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        game_numbers = range(1, len(filtered_data) + 1)
        
        ax.plot(game_numbers, filtered_data['wins_cumsum'], 
                'g-', linewidth=2, label='Victorias', marker='o', markersize=3)
        ax.plot(game_numbers, filtered_data['losses_cumsum'], 
                'r-', linewidth=2, label='Derrotas', marker='o', markersize=3)
        
        ax.set_xlabel('Número de Juego', fontsize=12)
        ax.set_ylabel('Juegos Acumulados', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_title(f'Temporada {selected_year} - {game_type}', fontsize=13)
        
        st.pyplot(fig)
        plt.close()
    else:
        st.warning("No hay datos disponibles para la selección actual.")

with col2:
    st.subheader(f"Distribución de Resultados")
    
    if total_games > 0:
        fig, ax = plt.subplots(figsize=(8, 8))
        
        sizes = [total_wins, total_losses]
        labels = [f'Victorias\n({total_wins})', f'Derrotas\n({total_losses})']
        colors = ['#2ecc71', '#e74c3c']
        explode = (0.05, 0.05)
        
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90, textprops={'fontsize': 12})
        ax.axis('equal')
        
        st.pyplot(fig)
        plt.close()
        
        st.metric("Total de Juegos", total_games)
        if total_games > 0:
            win_percentage = (total_wins / total_games) * 100
            st.metric("Porcentaje de Victorias", f"{win_percentage:.1f}%")
    else:
        st.warning("No hay datos disponibles para la selección actual.")