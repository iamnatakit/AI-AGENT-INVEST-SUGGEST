class NewsMacroAgent:
    @property
    def instructions(self):
        return "คุณวิเคราะห์แนวโน้มเศรษฐกิจมหภาค อัตราดอกเบี้ย และข่าวการเงิน อธิบายผลกระทบต่อตลาดโดยรวมเป็นภาษาไทย ตอบเป็นภาษาไทยเสมอ ไม่แนะนำสินทรัพย์ใดเป็นการเฉพาะเจาะจง"
        
    def run(self, user_message: str, **kwargs) -> dict:
        return {"agent": "NewsMacroAgent", "status": "success", "response": f"Macro analysis regarding: {user_message}"}
