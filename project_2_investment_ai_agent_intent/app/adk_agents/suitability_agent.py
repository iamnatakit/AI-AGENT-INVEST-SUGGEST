class SuitabilityAgent:
    @property
    def instructions(self):
        return "คุณประเมินความเหมาะสมของผู้ลงทุนตามอายุ รายได้ และเป้าหมายที่ระบุ ตอบเป็นภาษาไทยเสมอ หากข้อมูลไม่ครบให้ถามเพิ่มเติม"
        
    def run(self, user_message: str, **kwargs) -> dict:
        return {"agent": "SuitabilityAgent", "status": "success", "response": "Suitability assessment complete."}
