import streamlit as st
import plotly.graph_objects as go
import psycopg2
import pandas as pd

# ==========================================
# 資料庫連線
# ==========================================
@st.cache_data
def get_data(query):
    conn = psycopg2.connect(
        host="localhost", port=5432,
        database="lck_bp", user="lck_user", password="lck123456"
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ==========================================
# 頁面設定
# ==========================================
st.set_page_config(
    page_title="LCK BP 分析系統",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 LCK 2024 BP 分析系統")

# ==========================================
# 載入資料
# ==========================================
df_stats = get_data("SELECT * FROM public_mart.fact_player_stats")
df_winrate = get_data("SELECT * FROM public_mart.fact_bp_score")

# ==========================================
# 計算各指標的聯盟平均（用來當基準線）
# ==========================================
league_avg = df_stats.groupby('role').agg(
    avg_kda=('avg_kda', 'mean'),
    avg_ka=('avg_ka', 'mean'),
    dpm=('dpm', 'mean'),
    avg_damage_share=('avg_damage_share', 'mean'),
    avg_cspm=('avg_cspm', 'mean'),
    egpm=('egpm', 'mean'),
    avg_deaths=('avg_deaths', 'mean'),
    win_rate_pct=('win_rate_pct', 'mean')
).reset_index()

# ==========================================
# Tab 頁面
# ==========================================
tab1, tab2, tab3 = st.tabs(["選手雷達圖", "英雄勝率排行", "版本權重趨勢"])

# ==========================================
# Tab 1：選手雷達圖
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("篩選條件")

        # 選手選擇
        all_players = sorted(df_stats['player_name'].unique())
        selected_players = st.multiselect(
            "選擇選手（最多3位）",
            all_players,
            default=['Faker', 'Chovy'] if 'Faker' in all_players else all_players[:2],
            max_selections=3
        )

        # 版本選擇
        all_patches = sorted(df_stats['patch_version'].unique())
        selected_patches = st.multiselect(
            "選擇版本",
            all_patches,
            default=all_patches
        )

        # 藍紅方
        selected_side = st.selectbox(
            "藍紅方",
            ["全部", "Blue", "Red"]
        )

    with col2:
        if not selected_players:
            st.warning("請選擇至少一位選手")
        else:
            # 篩選資料
            df_filtered = df_stats[
                df_stats['player_name'].isin(selected_players) &
                df_stats['patch_version'].isin(selected_patches)
            ]

            if selected_side != "全部":
                df_filtered = df_filtered[df_filtered['side'] == selected_side]

            # 聚合選手數據
            player_agg = df_filtered.groupby('player_name').agg(
                avg_kda=('avg_kda', 'mean'),
                avg_ka=('avg_ka', 'mean'),
                dpm=('dpm', 'mean'),
                avg_damage_share=('avg_damage_share', 'mean'),
                avg_cspm=('avg_cspm', 'mean'),
                egpm=('egpm', 'mean'),
                avg_deaths=('avg_deaths', 'mean'),
                win_rate_pct=('win_rate_pct', 'mean'),
                games_played=('games_played', 'sum'),
                role=('role', 'first')
            ).reset_index()

            # 雷達圖指標
            categories = ['KDA', '場均K+A', '分均傷害', '傷害占比', '分均補刀', '分均經濟', '生存能力', '勝率%']

            fig = go.Figure()

            colors = ['#E63946', '#457B9D', '#2A9D8F']

            for i, (_, player) in enumerate(player_agg.iterrows()):
                # 取得同路線的聯盟平均
                role = player['role']
                avg_row = league_avg[league_avg['role'] == role]

                if not avg_row.empty:
                    avg = avg_row.iloc[0]

                    # 標準化（選手數據 / 聯盟平均 * 50）
                    values = [
                        min(player['avg_kda'] / max(avg['avg_kda'], 0.1) * 50, 100),
                        min(player['avg_ka'] / max(avg['avg_ka'], 0.1) * 50, 100),
                        min(player['dpm'] / max(avg['dpm'], 0.1) * 50, 100),
                        min(player['avg_damage_share'] / max(avg['avg_damage_share'], 0.1) * 50, 100),
                        min(player['avg_cspm'] / max(avg['avg_cspm'], 0.1) * 50, 100),
                        min(player['egpm'] / max(avg['egpm'], 0.1) * 50, 100),
                        min((1 / max(player['avg_deaths'], 0.1)) / (1 / max(avg['avg_deaths'], 0.1)) * 50, 100),
                        min(player['win_rate_pct'] / max(avg['win_rate_pct'], 0.1) * 50, 100),
                    ]
                else:
                    values = [50] * 8

                values_closed = values + [values[0]]
                categories_closed = categories + [categories[0]]

                fig.add_trace(go.Scatterpolar(
                    r=values_closed,
                    theta=categories_closed,
                    fill='toself',
                    name=f"{player['player_name']} ({int(player['games_played'])}場)",
                    line=dict(color=colors[i % len(colors)], width=2),
                    fillcolor=colors[i % len(colors)],
                    opacity=0.3
                ))

            # 加上聯盟平均基準線
            fig.add_trace(go.Scatterpolar(
                r=[50] * 9,
                theta=categories + [categories[0]],
                name='聯盟平均',
                line=dict(color='gray', width=1, dash='dash'),
                fill=None
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                showlegend=True,
                title="選手數據雷達圖（相對聯盟平均，50分=平均水準）",
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # 顯示原始數據表
            st.subheader("原始數據")
            display_cols = ['player_name', 'games_played', 'avg_kda', 'avg_ka',
                           'dpm', 'avg_damage_share', 'avg_cspm', 'egpm',
                           'avg_deaths', 'win_rate_pct']
            st.dataframe(
                player_agg[display_cols].round(2),
                hide_index=True
            )

# ==========================================
# Tab 2：英雄勝率排行
# ==========================================
with tab2:
    col1, col2 = st.columns([1, 3])

    with col1:
        st.subheader("篩選條件")
        all_roles = sorted(df_winrate['role'].unique())
        selected_role = st.selectbox("路線", ["全部"] + all_roles)
        min_games = st.slider("最少出場場次", 1, 50, 10)

    with col2:
        df_wr = df_winrate.copy()
        if selected_role != "全部":
            df_wr = df_wr[df_wr['role'] == selected_role]
        df_wr = df_wr[df_wr['total_games'] >= min_games]
        df_wr = df_wr.sort_values('weighted_win_rate', ascending=True).tail(20)

        fig2 = go.Figure(go.Bar(
            x=df_wr['weighted_win_rate'],
            y=df_wr['champion_name'] + ' (' + df_wr['role'] + ')',
            orientation='h',
            marker=dict(
                color=df_wr['weighted_win_rate'],
                colorscale='RdYlGn',
                showscale=True
            ),
            text=df_wr['weighted_win_rate'].astype(str) + '%',
            textposition='outside'
        ))

        fig2.update_layout(
            title=f"英雄加權勝率 Top 20（出場 >= {min_games} 場）",
            xaxis_title="加權勝率 %",
            height=600
        )

        st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# Tab 3：版本權重趨勢
# ==========================================
with tab3:
    df_patch = get_data("""
        SELECT patch_version, patch_weight, recency_rank
        FROM public_mart.fact_patch_weights
        ORDER BY first_seen
    """)

    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=df_patch['patch_version'],
        y=df_patch['patch_weight'],
        mode='lines+markers+text',
        text=df_patch['patch_weight'].astype(str),
        textposition='top center',
        line=dict(color='#457B9D', width=2),
        marker=dict(size=10)
    ))

    fig3.update_layout(
        title="版本權重衰減趨勢",
        xaxis_title="版本",
        yaxis_title="權重",
        yaxis=dict(range=[0, 1.2]),
        height=400
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.info("💡 最新版本權重為 1.0，越舊的版本權重越低，確保分析以最新版本數據為主。")