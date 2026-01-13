import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="EPL Points Tracker",
    page_icon="⚽",
    layout="wide"
)

# Title and description
st.title("⚽ EPL Cumulative Points Progression")
st.markdown("""
Upload your EPL season CSV file to visualize and compare team performances throughout the season.
The CSV should contain columns: HomeTeam, AwayTeam, FTHG (Full Time Home Goals), FTAG (Full Time Away Goals)
""")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

def process_team_points(data):
    """Process match data and calculate cumulative points for each team"""
    teams = data['HomeTeam'].unique()
    team_lists = {team: [0] for team in teams}
    
    for row in data.itertuples():
        home = row.HomeTeam
        away = row.AwayTeam
        
        if row.FTHG > row.FTAG:
            team_lists[home].append(team_lists[home][-1] + 3)
            team_lists[away].append(team_lists[away][-1] + 0)
        elif row.FTHG < row.FTAG:
            team_lists[home].append(team_lists[home][-1] + 0)
            team_lists[away].append(team_lists[away][-1] + 3)
        else:
            team_lists[home].append(team_lists[home][-1] + 1)
            team_lists[away].append(team_lists[away][-1] + 1)
    
    return team_lists, teams

def create_comparison_chart(team_lists, match_day, team1, team2, color1, color2):
    """Create a matplotlib chart comparing two teams' cumulative points"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(match_day, team_lists[team1], color=color1, linewidth=2.5, 
            label=team1, marker='o', markersize=4)
    ax.plot(match_day, team_lists[team2], color=color2, linewidth=2.5, 
            label=team2, marker='s', markersize=4)
    
    ax.set_xlabel("Gameweek", fontsize=12, fontweight='bold')
    ax.set_ylabel("Points", fontsize=12, fontweight='bold')
    ax.set_title(f"Cumulative Points Progression: {team1} vs {team2}",
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xticks(match_day)
    ax.grid(True, axis="y", color="#E0E0E0", linestyle='--', alpha=0.7)
    ax.grid(False, axis="x")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.margins(x=0, y=0.02)
    ax.legend(frameon=False, loc='upper left', fontsize=11)
    plt.tight_layout()
    
    return fig

if uploaded_file is not None:
    try:
        # Read the CSV file
        data = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
        
        # Validate required columns
        required_cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
        if not all(col in data.columns for col in required_cols):
            st.error(f"❌ CSV must contain columns: {', '.join(required_cols)}")
        else:
            # Show preview
            with st.expander("📊 Preview Dataset"):
                st.dataframe(data.head(10))
            
            # Process data
            team_lists, teams = process_team_points(data)
            max_gameweek = max(len(points) for points in team_lists.values()) - 1
            match_day = list(range(0, max_gameweek + 1))
            
            # Team Selection
            st.markdown("---")
            st.subheader("🎯 Select Teams to Compare")
            
            col1, col2 = st.columns(2)
            
            with col1:
                team1 = st.selectbox("Select Team 1", options=sorted(teams), index=0)
                color1 = st.color_picker("Pick a color for Team 1", "#6CABDD")
            
            with col2:
                team2 = st.selectbox("Select Team 2", options=sorted(teams), 
                                    index=1 if len(teams) > 1 else 0)
                color2 = st.color_picker("Pick a color for Team 2", "#DA291C")
            
            # Comparison Chart
            st.markdown("---")
            st.subheader("📈 Points Progression Chart")
            
            fig = create_comparison_chart(team_lists, match_day, team1, team2, color1, color2)
            st.pyplot(fig)
            
            # Statistics
            st.markdown("---")
            st.subheader("📊 Statistics Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(label=f"{team1} - Points", value=team_lists[team1][-1])
            
            with col2:
                st.metric(label=f"{team2} - Points", value=team_lists[team2][-1])
            
            with col3:
                difference = team_lists[team1][-1] - team_lists[team2][-1]
                st.metric(label="Point Difference", value=abs(difference),
                         delta=f"{team1} leads" if difference > 0 else f"{team2} leads")
            
            # Multi-Team Comparison
            st.markdown("---")
            st.subheader("🔄 Multi-Team Comparison")
            
            selected_teams = st.multiselect(
                "Select teams to compare (up to 6)",
                options=sorted(teams),
                default=[team1, team2] if team1 != team2 else [team1],
                max_selections=6
            )
            
            if len(selected_teams) > 0:
                # Default colors
                default_colors = ['#6CABDD', '#DA291C', '#FDB913', '#034694', '#7A263A', '#1B458F']
                
                # Color selection for each team
                st.markdown("#### Choose colors for each team")
                team_colors = {}
                
                # Create columns based on number of selected teams
                num_cols = min(len(selected_teams), 3)
                cols = st.columns(num_cols)
                
                for idx, team in enumerate(selected_teams):
                    with cols[idx % num_cols]:
                        team_colors[team] = st.color_picker(
                            f"{team}",
                            default_colors[idx % len(default_colors)],
                            key=f"multi_{team}"
                        )
                
                # Create the multi-team chart
                fig2, ax2 = plt.subplots(figsize=(12, 6))
                
                for team in selected_teams:
                    ax2.plot(match_day, team_lists[team], color=team_colors[team],
                            linewidth=2, label=team, marker='o', markersize=3)
                
                ax2.set_xlabel("Gameweek", fontsize=12, fontweight='bold')
                ax2.set_ylabel("Points", fontsize=12, fontweight='bold')
                ax2.set_title("Multi-Team Points Progression", fontsize=14, 
                             fontweight='bold', pad=20)
                ax2.set_xticks(match_day)
                ax2.grid(True, axis="y", color="#E0E0E0", linestyle='--', alpha=0.7)
                ax2.grid(False, axis="x")
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                ax2.margins(x=0, y=0.02)
                ax2.legend(frameon=False, loc='upper left', fontsize=10)
                plt.tight_layout()
                
                st.pyplot(fig2)
            
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

else:
    st.info("👆 Please upload a CSV file to get started")
    
    # Show example format
    st.markdown("### 📝 Expected CSV Format")
    example_data = pd.DataFrame({
        'HomeTeam': ['Liverpool', 'Man City', 'Arsenal'],
        'AwayTeam': ['Chelsea', 'Man United', 'Tottenham'],
        'FTHG': [2, 3, 1],
        'FTAG': [1, 1, 1]
    })
    st.dataframe(example_data)