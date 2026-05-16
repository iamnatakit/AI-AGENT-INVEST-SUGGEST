class PortfolioRiskAgent:
    @property
    def instructions(self):
        return "คุณวิเคราะห์การจัดสรรพอร์ตโฟลิโอและความเสี่ยง ระบุความเสี่ยงจากการกระจุกตัวและแนะนำการกระจายการลงทุน ตอบเป็นภาษาไทยเสมอ ต้องมีโปรไฟล์ความเสี่ยงก่อนให้คำแนะนำเฉพาะบุคคล"
        
    def run(self, user_message: str, risk_profile_present: bool = False, **kwargs) -> dict:
        if not risk_profile_present:
            return {"agent": "PortfolioRiskAgent", "status": "requires_action", "response": "Before I provide a personalized portfolio recommendation, please confirm your investment risk profile (e.g., conservative, moderate, aggressive)."}
        return {"agent": "PortfolioRiskAgent", "status": "success", "response": "Portfolio risk analysis provided based on your profile."}
