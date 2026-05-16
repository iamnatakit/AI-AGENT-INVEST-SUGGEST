class FinanceEducationAgent:
    @property
    def instructions(self):
        return "คุณคือผู้เชี่ยวชาญด้านการให้ความรู้ทางการเงิน อธิบายแนวคิดทางการเงินอย่างเรียบง่ายและชัดเจนเป็นภาษาไทย ตอบเป็นภาษาไทยเสมอ ไม่ให้คำแนะนำการลงทุนเฉพาะเจาะจง"
        
    def run(self, user_message: str, **kwargs) -> dict:
        return {"agent": "FinanceEducationAgent", "status": "success", "response": f"Educational breakdown for: {user_message}"}
