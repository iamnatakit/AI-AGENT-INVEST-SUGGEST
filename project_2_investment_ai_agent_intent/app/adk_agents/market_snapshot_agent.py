class MarketSnapshotAgent:
    @property
    def instructions(self):
        return "คุณให้ข้อมูลราคาหุ้นและภาพรวมตลาดอย่างรวดเร็ว แจ้งราคาปัจจุบันและปริมาณการซื้อขายถ้ามีข้อมูล ตอบเป็นภาษาไทยเสมอ ห้ามแนะนำให้ซื้อหรือขาย"
        
    def run(self, user_message: str, ticker: str = None, **kwargs) -> dict:
        return {"agent": "MarketSnapshotAgent", "status": "success", "ticker": ticker, "response": f"Snapshot for {ticker or 'market'}"}
