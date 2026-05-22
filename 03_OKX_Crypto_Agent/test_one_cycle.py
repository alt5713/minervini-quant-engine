from okx_main_agent import AntigravityCryptoAgent

if __name__ == "__main__":
    agent = AntigravityCryptoAgent(symbol='BTC/USDT:USDT')
    print("--- OKX Crypto Agent 단일 사이클 테스트 실행 ---")
    agent.run_cycle()
    print("--- 테스트 완료 ---")
