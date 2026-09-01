import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="MyFP 資産管理ダッシュボード", layout="wide")

st.title("💼 資産管理 & NISAポートフォリオ ダッシュボード")

# --- サイドバー：月次データ入力 ---
st.sidebar.header("📝 最新データ入力（月末更新）")

st.sidebar.subheader("🏦 銀行預金")
bank_smbc = st.sidebar.number_input("三井住友銀行 (円)", value=300000, step=10000)
bank_yucho = st.sidebar.number_input("ゆうちょ銀行 (円)", value=150000, step=10000)

st.sidebar.subheader("📈 PayPay証券 (NISA)")
nisa_gold = st.sidebar.number_input("三菱UFJ 純金ファンド (円)", value=139500, step=5000)
nisa_sp500 = st.sidebar.number_input("eMAXIS Slim 米国株式 (円)", value=120000, step=5000)
nisa_balance = st.sidebar.number_input("eMAXIS Slim 8資産均等 (円)", value=59000, step=5000)
nisa_stocks = st.sidebar.number_input("個別株 (トヨタ/NVDA/GOOGL) (円)", value=80066, step=5000)

st.sidebar.subheader("🏢 自社持株会")
stock_holding = st.sidebar.number_input("持株会 評価額 (円)", value=100000, step=5000)

# --- 計算ロジック ---
nisa_total = nisa_gold + nisa_sp500 + nisa_balance + nisa_stocks
bank_total = bank_smbc + bank_yucho
total_assets = bank_total + nisa_total + stock_holding

gold_ratio = (nisa_gold / nisa_total * 100) if nisa_total > 0 else 0

# --- メイン画面：KPIカード ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("総資産", f"{total_assets:,.0f} 円")
col2.metric("NISA資産額", f"{nisa_total:,.0f} 円")
col3.metric("純金比率 (NISA内)", f"{gold_ratio:.1f} %", delta=f"{gold_ratio - 30:.1f}% (目標30%)")
col4.metric("目標200万円まで", f"{max(0, 2000000 - nisa_total):,.0f} 円")

# ゴールド比率アラート
if gold_ratio > 35:
    st.info("🛡️ **純金比率：高め（守り重視）** — 相場下落へのクッションが十分に効いています。")
elif gold_ratio < 25:
    st.warning("⚠️ **純金比率：低め** — 株式比率が高まっています。リスク許容度に応じて金の買い増しを検討してください。")
else:
    st.success("✅ **純金比率：理想水準（約30%）** — 攻守のバランスが完璧に保たれています。")

st.markdown("---")

# --- グラフエリア ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 ポートフォリオ配分 (NISA)")
    portfolio_df = pd.DataFrame({
        "資産クラス": ["三菱UFJ 純金ファンド", "S&P500", "8資産均等型", "個別株 (米ハイテク・トヨタ)"],
        "評価額": [nisa_gold, nisa_sp500, nisa_balance, nisa_stocks]
    })
    fig_pie = px.pie(
        portfolio_df, 
        values="評価額", 
        names="資産クラス", 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("📈 目標200万円 到達シミュレーション")
    monthly_invest = st.slider("今後の毎月積立額 (円)", min_value=10000, max_value=50000, value=20000, step=1000)
    annual_return = st.slider("想定年利 (%)", min_value=3.0, max_value=8.0, value=6.0, step=0.5) / 100

    # 10年分の予測計算
    years = np.arange(0, 11)
    future_values = []
    for y in years:
        # 元本複利 + 積立複利計算
        fv = (nisa_total * ((1 + annual_return) ** y) + 
              (monthly_invest * 12) * (((1 + annual_return) ** y - 1) / annual_return)) if annual_return > 0 else nisa_total + (monthly_invest * 12 * y)
        future_values.append(fv)

    sim_df = pd.DataFrame({"経過年数 (年)": years, "予想資産額 (円)": future_values})
    
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Scatter(x=sim_df["経過年数 (年)"], y=sim_df["予想資産額 (円)"], mode='lines+markers', name='資産推移予測', line=dict(color='#2ECC71', width=3)))
    fig_sim.add_hline(y=2000000, line_dash="dash", line_color="red", annotation_text="目標 200万円")
    fig_sim.update_layout(yaxis_title="総資産評価額 (円)", xaxis_title="年数後", hovermode="x unified")
    st.plotly_chart(fig_sim, use_container_width=True)
