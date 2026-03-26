import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from exchanges.fetcher import fetch_ohlcv
from algorithms.sma import SMACrossover
from algorithms.rsi import RSIMomentum
from algorithms.macd import MACDCrossover
from simulator.engine import SimulatorEngine

# Page Settings
st.set_page_config(page_title="Crypto Quant Simulator - created by JSH", page_icon="📈", layout="wide")

# Custom Title and CSS for better aesthetics
st.markdown("""
<style>
.main-title {
    font-size: 3rem;
    font-weight: 700;
    color: #1f77b4;
    margin-bottom: 0px;
}
.sub-title {
    font-size: 1.2rem;
    color: #666;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📈 Crypto Quant Simulator - created by JSH</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">가상자산 퀀트 알고리즘 백테스트 및 시뮬레이션 플랫폼</div>', unsafe_allow_html=True)

# -------------------- SIDEBAR SETTINGS -------------------- #
st.sidebar.header("⚙️ 시뮬레이션 설정 (Settings)")

# 1. Exchange Selection
exchange_choice = st.sidebar.selectbox(
    "1. 거래소 선택 (Exchange)",
    ("upbit", "bithumb", "coinone")
)

# 2. Coin Symbol Selection
# By default ccxt uses BTC/KRW for korean exchanges. Will parse automatically.
coin_symbol = st.sidebar.text_input("2. 가상자산 티커 (Coin Ticker)", value="BTC/KRW", help="예: BTC/KRW, ETH/KRW")

# 3. Strategy Selection
strategy_name = st.sidebar.selectbox(
    "3. 퀀트 알고리즘 선택 (Algorithm)",
    ("SMA Crossover (단순이동평균)", "RSI Momentum (상대강도지수)", "MACD Crossover (이동평균수렴확산)")
)

# 4. Strategy Parameters
st.sidebar.subheader("알고리즘 파라미터")
if strategy_name == "SMA Crossover (단순이동평균)":
    sma_short = st.sidebar.slider("단기 이동평균 (Short Window)", min_value=5, max_value=50, value=10, step=1)
    sma_long = st.sidebar.slider("장기 이동평균 (Long Window)", min_value=20, max_value=200, value=50, step=5)
elif strategy_name == "RSI Momentum (상대강도지수)":
    rsi_period = st.sidebar.slider("RSI 기간 (Period)", min_value=5, max_value=30, value=14, step=1)
    rsi_overbought = st.sidebar.slider("RSI 과매수 (Overbought)", min_value=60, max_value=90, value=70, step=1)
    rsi_oversold = st.sidebar.slider("RSI 과매도 (Oversold)", min_value=10, max_value=40, value=30, step=1)
elif strategy_name == "MACD Crossover (이동평균수렴확산)":
    macd_fast = st.sidebar.slider("단기 EMA (Fast)", min_value=5, max_value=20, value=12, step=1)
    macd_slow = st.sidebar.slider("장기 EMA (Slow)", min_value=20, max_value=40, value=26, step=1)
    macd_signal = st.sidebar.slider("시그널 (Signal)", min_value=5, max_value=15, value=9, step=1)

# 5. Execute button
run_simulation = st.sidebar.button("🚀 시뮬레이션 실행", type="primary", use_container_width=True)

# -------------------- MAIN LOGIC -------------------- #
if run_simulation:
    with st.spinner(f"{exchange_choice.upper()} 거래소에서 {coin_symbol} 데이터 조회 중..."):
        # Fetch Data
        df = fetch_ohlcv(exchange_choice, coin_symbol, timeframe='1d', limit=365)
        
    if df.empty:
        st.error(f"데이터를 불러오지 못했습니다. {exchange_choice} 환경에서 {coin_symbol} 티커가 유효한지 확인하세요. (일부 API 제한 또는 상장폐지 티커)")
    else:
        st.success("데이터 로드 및 시뮬레이션 완료!")
        
        # Instantiate Strategy Algorithm
        if strategy_name == "SMA Crossover (단순이동평균)":
            strategy = SMACrossover(short_window=sma_short, long_window=sma_long)
        elif strategy_name == "RSI Momentum (상대강도지수)":
            strategy = RSIMomentum(period=rsi_period, overbought=rsi_overbought, oversold=rsi_oversold)
        elif strategy_name == "MACD Crossover (이동평균수렴확산)":
            strategy = MACDCrossover(fast_period=macd_fast, slow_period=macd_slow, signal_period=macd_signal)
        
        # Apply Strategy
        df_with_signal = strategy.generate_signals(df)
        df_with_signal.dropna(inplace=True) # remove NaN from rolling windows
        
        # Run Simulator
        simulator = SimulatorEngine(data=df_with_signal, initial_capital=10000000) # 10M KRW
        result_df = simulator.run()
        summary = simulator.get_summary()
        
        # -------------------- DASHBOARD METRICS -------------------- #
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("단순 누적 수익률 (시장 기준)", f"{summary.get('Total Market Return (%)', 0)} %")
        col2.metric("퀀트 전략 수익률 (전략 기준)", f"{summary.get('Total Strategy Return (%)', 0)} %")
        col3.metric("최대 낙폭 (Max Drawdown)", f"{summary.get('Max Drawdown (%)', 0)} %")
        col4.metric("시뮬레이션 후 보유금액", f"₩ {summary.get('Final Portfolio Value', 0):,.0f}")
        
        # -------------------- CHARTS (PLOTLY) -------------------- #
        st.markdown("### 📊 자산 성장률 비교 차트 (Asset Growth Comparison)")
        fig = go.Figure()
        
        # Market Portfolio line
        fig.add_trace(go.Scatter(
            x=result_df.index,
            y=result_df['market_cum_return'] * 100,
            mode='lines',
            name='시장 수익률 (존버)',
            line=dict(color='gray', dash='dot')
        ))
        
        # Strategy Portfolio line
        fig.add_trace(go.Scatter(
            x=result_df.index,
            y=result_df['strategy_cum_return'] * 100,
            mode='lines',
            name=f'{strategy.name} 전략 수익률',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            xaxis_title="날짜 (Date)",
            yaxis_title="수익률 Growth (%)",
            height=400,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # -------------------- DATA TABLE -------------------- #
        st.markdown("### 📋 세부 트레이딩 데이터 및 시그널 로그")
        # Displaying different columns based on the active strategy
        base_cols = ['open', 'close', 'signal', 'market_return', 'strategy_return']
        if strategy_name == "SMA Crossover (단순이동평균)":
            extra_cols = ['sma_short', 'sma_long']
        elif strategy_name == "RSI Momentum (상대강도지수)":
            extra_cols = ['rsi']
        elif strategy_name == "MACD Crossover (이동평균수렴확산)":
            extra_cols = ['macd', 'macd_signal']
            
        display_cols = ['open', 'close'] + extra_cols + ['signal', 'market_return', 'strategy_return']
        
        display_df = result_df[display_cols].copy()
        # Formatting for readability
        display_cols_formatting = {
            'market_return': "{:.2f}%",
            'strategy_return': "{:.2f}%"
        }
        for col, fmt in display_cols_formatting.items():
            if col in display_df.columns:
                display_df[col] = display_df[col] * 100
        st.dataframe(display_df.tail(30), use_container_width=True, height=250)
else:
    st.info("👈 좌측 사이드바에서 거래소, 코인 종류 및 알고리즘을 선택한 뒤 [시뮬레이션 실행]을 클릭하세요.")
    st.markdown("""
        ### 사용 안내
        1. **데이터 소스**: ccxt 라이브러리를 통해 실시간으로 선택한 거래소(Upbit, Bithumb, Coinone)의 1일봉 데이터를 수집합니다.
        2. **알고리즘 시스템**: 추가적인 `.py` 전략 파일을 개발하여 `/algorithms` 폴더에 넣으면 확장 가능합니다. 기본 제공되는 것은 2개의 단순이동평균(SMA) 선이 교차할 때 매수/매도하는 퀀트 스크립트입니다.
        3. **비용**: 본 시스템은 Python의 Streamlit 오픈소스로 개발되어 추가 인프라 구축이나 데이터수집 유로화 없이 구축 및 배포가 가능합니다.
    """)
