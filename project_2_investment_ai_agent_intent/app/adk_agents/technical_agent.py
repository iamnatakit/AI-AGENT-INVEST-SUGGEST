class TechnicalAgent:
    @property
    def instructions(self):
        return "คุณวิเคราะห์ตัวชี้วัดทางเทคนิค เช่น RSI, MACD, เส้นค่าเฉลี่ยเคลื่อนที่ อธิบายรูปแบบกราฟอย่างตรงไปตรงมาเป็นภาษาไทย ตอบเป็นภาษาไทยเสมอ ห้ามทำนายราคาในอนาคตอย่างแน่นอน"
        
    def run(self, user_message: str, ticker: str = None, **kwargs) -> dict:
        return {"agent": "TechnicalAgent", "status": "success", "ticker": ticker, "response": f"Technical analysis for {ticker}"}
