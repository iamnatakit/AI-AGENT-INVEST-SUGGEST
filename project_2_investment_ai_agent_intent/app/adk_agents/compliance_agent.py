class ComplianceAgent:
    @property
    def instructions(self):
        return "คุณตรวจสอบข้อความทุกชิ้นก่อนส่งออก ตรวจให้แน่ใจว่าไม่มีวลีห้าม และมีคำเตือนความเสี่ยงแนบท้าย ตอบเป็นภาษาไทยเสมอ"
        
    def run(self, draft_response: str, **kwargs) -> dict:
        disclaimer = "\n\n⚠️ คำเตือน: การลงทุนมีความเสี่ยง ผู้ลงทุนอาจได้รับเงินคืนน้อยกว่าเงินลงทุนเริ่มต้น ข้อมูลนี้จัดทำขึ้นเพื่อการศึกษาเท่านั้น ไม่ถือเป็นคำแนะนำทางการเงิน"
        
        # Rule-based compliance logic
        violations = []
        lower_draft = draft_response.lower()
        if "buy now" in lower_draft or "sell now" in lower_draft or "profit guaranteed" in lower_draft:
            violations.append("Used prohibited phrase")
            
        clean_response = draft_response
        if violations:
            clean_response = "[REDACTED FOR COMPLIANCE] " + draft_response
            
        if "⚠️ คำเตือน:" not in clean_response and "DISCLAIMER:" not in clean_response:
            clean_response += disclaimer
            
        return {
            "agent": "ComplianceAgent", 
            "status": "compliant" if not violations else "violation_fixed",
            "violations": violations,
            "final_response": clean_response
        }
