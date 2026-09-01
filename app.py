import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from PIL import Image

# 1. ページ基本設定
st.set_page_config(
    page_title="MyFP 資産運用＆NISAダッシュボード", 
    page_icon="💼", 
    layout="wide"
)

# ==========================================
# 🔒 2. パスワード保護ロジック
# ==========================================
def check_password():
    def password_entered():
        # 👇 パスワードはお好みの値に変更してください
        if st.session_state["password"] == "3027":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 MyFP 資産管理ダッシュボード")
        st.text_input("パスワードを入力してください", type="password", on_change=password_entered, key="password")
        st.info("※認証後に専属FP分析とポートフォリオ画面が表示されます。")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 MyFP 資産管理ダッシュボード")
        st.text_input("パスワードを入力してください", type="password", on_change=password_entered, key="password")
        st.error("パスワードが正しくありません")
        return False
    else:
        return True

if not check_password():
    st.stop()

# ==========================================
# 📊 3. メインダッシュボード
# ==========================================
st.title("💼 専属FP 資産運用ダッシュボード")
st.caption("PayPay証券 NISA × 自社持株会 × 銀行口座 統合ポートフォリオ管理")

# --- サイドバー：データ入力＆OCR補助 ---
st.sidebar.header("📝 最新データ入力・更新")

with st.sidebar.expander("📷 PayPay証券 スクショ確認 / 記録", expanded=False):
    uploaded_file = st.file_uploader("PayPay証券の画面スクショをアップロード", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="アップロード画像", use_column_width=True)
        st.info("💡 画面の数値を下の入力欄に反映してください。")

st.sidebar.subheader("📈 PayPay証券 (NISA)")
nisa_gold = st.sidebar.number_input("三菱UFJ 純金ファンド (円)", value=120000, step=5000)
nisa_sp500 = st.sidebar.number_input("eMAXIS Slim 米国株式(S&P500) (円)", value=120000, step=5000)
nisa_balance = st.sidebar.number_input("eMAXIS Slim バランス(8資産) (円)", value=60000, step=5000)
nisa_toyota = st.sidebar.number_input("トヨタ自動車株 (円)", value=50000, step=5000)
nisa_nvda = st.sidebar.number_input("エヌビディア株 (円)", value=50000, step=5000)

st.sidebar.subheader("🏢 自社持株会")
stock_holding = st.sidebar.number_input("自社持株会 評価額 (円)", value=100000, step=5000)

st.sidebar.subheader("🏦 銀行預金 (生活防衛資金)")
bank_smbc = st.sidebar.number_input("三井住友銀行 (円)", value=300000, step=10000)
bank_yucho = st.sidebar.number_input("ゆうちょ銀行 (円)", value=150000, step=10000)

# --- 計算処理 ---
nisa_stocks = nisa_toyota + nisa_nvda
nisa_total = nisa_gold + nisa_sp500 + nisa_balance + nisa_stocks
bank_total = bank_smbc + bank_yucho
total_assets = bank_total + nisa_total + stock_holding

gold_ratio = (nisa_gold / nisa_total * 100) if nisa_total > 0 else 0

# --- KPIカード表示 ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("総純資産", f"{total_assets:,.0f} 円")
col2.metric("NISA総額", f"{nisa_total:,.0f} 円")
col3.metric("純金比率 (守りの盾)", f"{gold_ratio:.1f} %", delta=f"{gold_ratio - 30:.1f}% (目安: 30%)")
col4.metric("目標200万円まで", f"{max(0, 2000000 - nisa_total):,.0f} 円")

# --- マイルストーン・達成バッジ ---
badges = []
if nisa_total >= 250000:
    badges.append("🥉 25万円突破（スタートダッシュ達成）")
if nisa_total >= 500000:
    badges.append("🥈 50万円突破（資産形成の基礎固め）")
if nisa_total >= 1000000:
    badges.append("🥇 100万円突破（複利の加速期）")
if nisa_total >= 2000000:
    badges.append("👑 200万円達成（大台到達！）")

if badges:
    st.success(" **獲得済みマイルストーン:** " + " ｜ ".join(badges))

st.markdown("---")

# --- タブ構成 ---
tab1, tab2, tab3 = st.tabs(["📊 資産配分＆FP分析", "⚖️ 純金リバランス診断", "🔮 将来シミュレーション"])

# ==========================================
# タブ1: 資産配分 & FP診断
# ==========================================
with tab1:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📊 NISAポートフォリオ配分")
        portfolio_df = pd.DataFrame({
            "資産クラス": [
                "三菱UFJ 純金ファンド (守り)", 
                "S&P500 (米国成長)", 
                "8資産均等 (手堅い分散)", 
                "トヨタ (国内優良)", 
                "エヌビディア (AI成長)"
            ],
            "評価額": [nisa_gold, nisa_sp500, nisa_balance, nisa_toyota, nisa_nvda]
        })
        fig_pie = px.pie(
            portfolio_df, 
            values="評価額", 
            names="資産クラス", 
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.subheader("💡 専属FPの診断コメント")
        if gold_ratio >= 35:
            st.info("🛡️ **【守り重視モード】** 純金比率が35%を超えており、相場急落に対する防御力は抜群です。株式市場の上昇を取りこぼさないよう、新規積立はS&P500や個別株へ少し厚めに配分しても良い水準です。")
        elif gold_ratio < 25:
            st.warning("⚠️ **【攻め重視モード】** 株式比率が高まり、金の比率が25%を下回っています。株価の急な調整局面で評価額のブレが大きくなる可能性があるため、金の積立比率を一時的に引き上げるリバランスが効果的です。")
        else:
            st.success("✅ **【黄金バランス】** 純金比率が約30%に保たれており、攻め（S&P500・エヌビディア）と守り（純金・8資産均等・トヨタ）が理想的な調和を描いています。現在の配分を継続しましょう。")

        st.markdown(f"""
        - **コア（土台）：** 純金ファンド ＋ S&P500 ＋ 8資産均等型 ＝ **{((nisa_gold + nisa_sp500 + nisa_balance) / nisa_total * 100):.1f}%**
        - **サテライト（成長）：** トヨタ ＋ エヌビディア ＝ **{((nisa_toyota + nisa_nvda) / nisa_total * 100):.1f}%**
        - **生活防衛資金（現預金）：** **{bank_total:,.0f} 円**（予期せぬ支出への備えも確保済み）
        """)

# ==========================================
# タブ2: 純金リバランス診断
# ==========================================
with tab2:
    st.subheader("⚖️ 純金（ゴールド）リバランス・シミュレーター")
    st.write("毎月の積立予算を設定すると、純金比率を目標値（デフォルト30%）へ近づけるための**最適な積立配分**を自動算出します。")

    col_reb1, col_reb2 = st.columns(2)
    with col_reb1:
        target_gold_ratio = st.slider("目標とする純金比率 (%)", min_value=15, max_value=45, value=30, step=5)
        monthly_budget = st.number_input("毎月の積立予算 (円)", value=20000, step=1000)

    # 推奨積立額の計算
    current_gold = nisa_gold
    target_gold_amount = (nisa_total + monthly_budget) * (target_gold_ratio / 100)
    ideal_gold_invest = max(0, min(monthly_budget, target_gold_amount - current_gold))
    ideal_other_invest = monthly_budget - ideal_gold_invest

    with col_reb2:
        st.markdown(f"#### 🎯 推奨積立配分（予算: {monthly_budget:,.0f}円）")
        st.metric("三菱UFJ 純金ファンド 推奨積立額", f"{ideal_gold_invest:,.0f} 円")
        st.metric("株式・バランスファンド 推奨積立額", f"{ideal_other_invest:,.0f} 円")

# ==========================================
# タブ3: 将来シミュレーション
# ==========================================
with tab3:
    st.subheader("🔮 段階的ステップアップ複利シミュレーター")
    st.write("現在から指定年数後に積立額を増額（例: 2万円 → 3.3万円）させた場合の成長曲線を試算します。")

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        current_monthly = st.number_input("現在の毎月積立額 (円)", value=20000, step=5000)
    with sim_col2:
        stepup_years = st.number_input("何年後に増額するか (年)", value=1, min_value=1, max_value=5, step=1)
        future_monthly = st.number_input("増額後の毎月積立額 (円)", value=33000, step=1000)
    with sim_col3:
        sim_return = st.slider("想定年利 (%)", min_value=3.0, max_value=8.0, value=6.0, step=0.5) / 100

    years_range = np.arange(0, 11)
    values = []

    current_val = nisa_total
    for y in years_range:
        if y == 0:
            values.append(current_val)
        else:
            monthly_payment = current_monthly if y <= stepup_years else future_monthly
            # 1年分の複利計算
            current_val = current_val * (1 + sim_return) + (monthly_payment * 12) * (((1 + sim_return) - 1) / sim_return if sim_return > 0 else 1)
            values.append(current_val)

    sim_df = pd.DataFrame({"経過年数 (年)": years_range, "予想資産額 (円)": values})

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=sim_df["経過年数 (年)"], 
        y=sim_df["予想資産額 (円)"], 
        mode='lines+markers', 
        name='資産推移予測', 
        line=dict(color='#00CC96', width=3)
    ))
    fig_line.add_hline(y=1000000, line_dash="dot", line_color="orange", annotation_text="100万円突破ライン")
    fig_line.add_hline(y=2000000, line_dash="dash", line_color="red", annotation_text="目標 200万円ライン")
    fig_line.update_layout(yaxis_title="NISA評価額 (円)", xaxis_title="年数後", hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)
