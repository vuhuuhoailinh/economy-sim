import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from simulation.monte_carlo_sim import run_monte_carlo_simulation

def render_monte_carlo_tab():
    if st.session_state.config is None:
        st.warning("⚠️ Please save configuration in Macro Economy tab first!")
    else:
        cfg = st.session_state.config
        tuning_cfg = st.session_state.tuning
        st.header("Monte Carlo Simulation")
        
        num_players = st.number_input("Number of Simulated Players", 1, 5000, 1000, help="Số lượng người chơi ảo sẽ được tạo ra để mô phỏng. Càng nhiều người chơi, kết quả và biểu đồ càng hội tụ sát thực tế, nhưng máy sẽ mất nhiều thời gian tính toán hơn.")
            
        if st.button("Run Monte Carlo Simulation", type="primary"):
            with st.spinner("Simulating journeys..."):
                balance_matrix, p0_flat_log, max_levels = run_monte_carlo_simulation(cfg, tuning_cfg, num_players)
                
                # Plot
                mean_balance = np.mean(balance_matrix, axis=0)
                p25 = np.percentile(balance_matrix, 25, axis=0)
                p75 = np.percentile(balance_matrix, 75, axis=0)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=list(range(max_levels+1)), y=mean_balance, mode='lines', name='Avg Balance', line=dict(color='blue', width=3)))
                fig.add_trace(go.Scatter(x=list(range(max_levels+1)), y=p75, mode='lines', name='75th Percentile', line=dict(color='lightblue', width=1, dash='dash')))
                fig.add_trace(go.Scatter(x=list(range(max_levels+1)), y=p25, mode='lines', name='25th Percentile', line=dict(color='lightblue', width=1, dash='dash'), fill='tonexty'))
                fig.add_trace(go.Scatter(x=list(range(max_levels+1)), y=balance_matrix[0, :], mode='lines', name='Player #1', line=dict(color='orange', width=2)))
                
                fig.update_layout(title=f"Net Coin Balance over {max_levels} Levels ({num_players} Players)", xaxis_title="Level Played", yaxis_title="Coin Balance")
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("Level-by-Level Log (Player #1)")
                st.dataframe(pd.DataFrame(p0_flat_log), use_container_width=True)
