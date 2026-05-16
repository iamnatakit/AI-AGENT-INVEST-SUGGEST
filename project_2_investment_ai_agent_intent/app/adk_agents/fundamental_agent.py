class FundamentalAgent:
    @property
    def instructions(self):
        return "คุณวิเคราะห์ตัวชี้วัดพื้นฐาน เช่น P/E ratio, EPS, งบดุล สรุปสุขภาพทางการเงินของบริษัทเป็นข้อเท็จจริงเป็นภาษาไทย ตอบเป็นภาษาไทยเสมอ"
        
    def run(self, user_message: str, ticker: str = None, **kwargs) -> dict:
        return {"agent": "FundamentalAgent", "status": "success", "ticker": ticker, "response": f"Fundamental analysis for {ticker}"}
