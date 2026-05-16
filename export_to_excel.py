import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = 'investment_chatbot.db'
OUTPUT_FILE = f'investment_billing_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

def export_to_excel():
    print("กำลังเชื่อมต่อฐานข้อมูล...")
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Query ข้อมูลตาราง Billing Ledger
        billing_query = "SELECT * FROM billing_ledger ORDER BY created_at DESC"
        df_billing = pd.read_sql_query(billing_query, conn)
        
        # Query ข้อมูลตาราง Usage Logs
        usage_query = "SELECT * FROM usage_logs ORDER BY created_at DESC"
        df_usage = pd.read_sql_query(usage_query, conn)
        
        conn.close()
        
        print("กำลังส่งออกข้อมูลลงไฟล์ Excel...")
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            df_billing.to_excel(writer, sheet_name='Billing Ledger', index=False)
            df_usage.to_excel(writer, sheet_name='Usage Logs', index=False)
            
        print(f"✅ ส่งออกสำเร็จ! ไฟล์ถูกบันทึกไว้ที่: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")
        print("ลองตรวจสอบว่าติดตั้ง pandas และ openpyxl หรือยัง (pip install pandas openpyxl)")

if __name__ == "__main__":
    export_to_excel()
