#!/usr/bin/env python3
"""
Verify ClinicLite database and provide sample queries for testing.
DataEngineer verification suite following Context7 principles.
"""

import sqlite3
from datetime import datetime, timedelta
import json

DB_PATH = "/Users/addzmaestro/coding projects/Claude system/workspace/data/cliniclite.db"

def run_query(conn, description, query):
    """Execute a query and print results."""
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"\n{description}")
    print("-" * 60)
    
    if cursor.description:
        headers = [desc[0] for desc in cursor.description]
        print(" | ".join(headers))
        print("-" * 60)
        
        for row in results[:10]:  # Show first 10 rows
            print(" | ".join(str(val) for val in row))
        
        if len(results) > 10:
            print(f"... and {len(results) - 10} more rows")
    
    print(f"Total rows: {len(results)}")
    return results

def test_critical_queries(conn):
    """Test queries critical for ClinicLite functionality."""
    
    print("\n" + "="*60)
    print("CRITICAL QUERIES FOR CLINICLITE TESTING")
    print("="*60)
    
    # 1. Upcoming appointments needing SMS reminders
    run_query(conn, 
        "1. UPCOMING APPOINTMENTS (Next 3 Days) - SMS Reminder Candidates",
        """
        SELECT 
            a.appointment_id,
            p.first_name || ' ' || p.last_name as patient_name,
            p.phone_e164,
            p.preferred_lang,
            a.next_visit_date,
            a.appointment_time,
            a.visit_type,
            a.risk_score,
            c.name as clinic_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN clinics c ON a.clinic_id = c.clinic_id
        WHERE a.next_visit_date BETWEEN DATE('now') AND DATE('now', '+3 days')
        AND a.status = 'scheduled'
        ORDER BY a.next_visit_date, a.appointment_time
        """)
    
    # 2. High-risk missed appointments
    run_query(conn,
        "2. HIGH-RISK MISSED APPOINTMENTS (Past 7 Days)",
        """
        SELECT 
            a.appointment_id,
            p.first_name || ' ' || p.last_name as patient_name,
            p.phone_e164,
            p.chronic_conditions,
            a.next_visit_date as missed_date,
            a.visit_type,
            a.risk_score,
            ROUND(julianday('now') - julianday(a.next_visit_date)) as days_overdue
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.next_visit_date < DATE('now')
        AND a.status = 'missed'
        AND a.risk_score > 0.7
        ORDER BY a.risk_score DESC, days_overdue DESC
        """)
    
    # 3. Low stock items requiring immediate attention
    run_query(conn,
        "3. CRITICAL LOW STOCK ITEMS",
        """
        SELECT 
            s.stock_id,
            c.name as clinic_name,
            s.item_name,
            s.on_hand_qty,
            s.reorder_level,
            s.unit,
            CASE 
                WHEN s.on_hand_qty = 0 THEN 'OUT OF STOCK'
                WHEN s.on_hand_qty < s.reorder_level * 0.5 THEN 'CRITICAL'
                ELSE 'LOW'
            END as urgency
        FROM stock_items s
        JOIN clinics c ON s.clinic_id = c.clinic_id
        WHERE s.on_hand_qty < s.reorder_level
        ORDER BY 
            CASE 
                WHEN s.on_hand_qty = 0 THEN 1
                WHEN s.on_hand_qty < s.reorder_level * 0.5 THEN 2
                ELSE 3
            END,
            s.on_hand_qty ASC
        """)
    
    # 4. Patients by language for SMS batching
    run_query(conn,
        "4. LANGUAGE DISTRIBUTION FOR SMS BATCHING",
        """
        SELECT 
            p.preferred_lang,
            COUNT(*) as patient_count,
            COUNT(DISTINCT a.appointment_id) as upcoming_appointments
        FROM patients p
        LEFT JOIN appointments a ON p.patient_id = a.patient_id
            AND a.next_visit_date >= DATE('now')
            AND a.status = 'scheduled'
        GROUP BY p.preferred_lang
        """)
    
    # 5. Daily appointment load
    run_query(conn,
        "5. DAILY APPOINTMENT LOAD (Next 7 Days)",
        """
        SELECT 
            next_visit_date,
            COUNT(*) as total_appointments,
            SUM(CASE WHEN risk_score > 0.7 THEN 1 ELSE 0 END) as high_risk_count,
            ROUND(AVG(risk_score), 3) as avg_risk_score
        FROM appointments
        WHERE next_visit_date BETWEEN DATE('now') AND DATE('now', '+7 days')
        AND status = 'scheduled'
        GROUP BY next_visit_date
        ORDER BY next_visit_date
        """)
    
    # 6. Waitlist priorities
    run_query(conn,
        "6. WAITLIST - HIGH PRIORITY PATIENTS",
        """
        SELECT 
            w.waitlist_id,
            p.first_name || ' ' || p.last_name as patient_name,
            p.phone_e164,
            w.visit_type,
            w.priority,
            w.requested_date,
            w.notes
        FROM waitlist w
        JOIN patients p ON w.patient_id = p.patient_id
        WHERE w.status = 'pending'
        AND w.priority <= 2
        ORDER BY w.priority, w.requested_date
        """)
    
    # 7. SMS queue status
    run_query(conn,
        "7. SMS OUTBOX - PENDING MESSAGES",
        """
        SELECT 
            message_id,
            message_type,
            language,
            scheduled_for,
            SUBSTR(message_text, 1, 50) || '...' as message_preview,
            attempts
        FROM messages_outbox
        WHERE status = 'pending'
        AND scheduled_for <= DATETIME('now', '+24 hours')
        ORDER BY scheduled_for
        """)
    
    # 8. Clinic utilization
    run_query(conn,
        "8. CLINIC UTILIZATION SUMMARY",
        """
        SELECT 
            c.name as clinic_name,
            COUNT(DISTINCT p.patient_id) as total_patients,
            COUNT(DISTINCT a.appointment_id) as total_appointments,
            COUNT(DISTINCT CASE WHEN a.status = 'missed' THEN a.appointment_id END) as missed_appointments,
            COUNT(DISTINCT s.stock_id) as stock_items,
            COUNT(DISTINCT CASE WHEN s.on_hand_qty < s.reorder_level THEN s.stock_id END) as low_stock_items
        FROM clinics c
        LEFT JOIN patients p ON c.clinic_id = p.clinic_id
        LEFT JOIN appointments a ON c.clinic_id = a.clinic_id
        LEFT JOIN stock_items s ON c.clinic_id = s.clinic_id
        GROUP BY c.clinic_id, c.name
        ORDER BY total_patients DESC
        """)

def generate_test_csv_samples(conn):
    """Generate sample CSV data for upload testing."""
    
    print("\n" + "="*60)
    print("SAMPLE CSV DATA FOR UPLOAD TESTING")
    print("="*60)
    
    cursor = conn.cursor()
    
    # Generate sample appointments CSV
    cursor.execute("""
        SELECT 
            p.patient_id,
            p.first_name,
            p.last_name,
            p.phone_e164,
            a.next_visit_date,
            a.appointment_time,
            a.visit_type,
            p.preferred_lang
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        WHERE a.next_visit_date >= DATE('now')
        AND a.status = 'scheduled'
        LIMIT 5
    """)
    
    print("\nSample appointments.csv content:")
    print("patient_id,first_name,last_name,phone,appointment_date,appointment_time,visit_type,language")
    for row in cursor.fetchall():
        print(",".join(str(val) for val in row))
    
    # Generate sample stock CSV
    cursor.execute("""
        SELECT 
            c.clinic_id,
            c.name,
            s.item_name,
            s.on_hand_qty,
            s.reorder_level,
            s.unit
        FROM stock_items s
        JOIN clinics c ON s.clinic_id = c.clinic_id
        WHERE s.on_hand_qty < s.reorder_level
        LIMIT 5
    """)
    
    print("\nSample stock.csv content:")
    print("clinic_id,clinic_name,item_name,quantity,reorder_level,unit")
    for row in cursor.fetchall():
        print(",".join(str(val) for val in row))

def performance_benchmarks(conn):
    """Test query performance for key operations."""
    
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARKS")
    print("="*60)
    
    import time
    
    queries = [
        ("Fetch 1000 appointments", 
         "SELECT * FROM appointments LIMIT 1000"),
        ("Complex join for dashboard",
         """SELECT a.*, p.*, c.* FROM appointments a 
            JOIN patients p ON a.patient_id = p.patient_id 
            JOIN clinics c ON a.clinic_id = c.clinic_id 
            WHERE a.next_visit_date >= DATE('now') LIMIT 100"""),
        ("Aggregate risk analysis",
         """SELECT risk_score, COUNT(*) FROM appointments 
            GROUP BY ROUND(risk_score, 1)"""),
        ("Stock alert generation",
         """SELECT * FROM stock_items 
            WHERE on_hand_qty < reorder_level""")
    ]
    
    for description, query in queries:
        cursor = conn.cursor()
        start = time.time()
        cursor.execute(query)
        results = cursor.fetchall()
        elapsed = (time.time() - start) * 1000
        print(f"{description}: {len(results)} rows in {elapsed:.2f}ms")

def main():
    """Main execution."""
    print("ClinicLite Database Verification Suite")
    print("="*60)
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Run critical queries
        test_critical_queries(conn)
        
        # Generate CSV samples
        generate_test_csv_samples(conn)
        
        # Performance benchmarks
        performance_benchmarks(conn)
        
        print("\n" + "="*60)
        print("DATABASE VERIFICATION COMPLETE")
        print("All systems ready for comprehensive testing!")
        print("="*60)
        
    except Exception as e:
        print(f"ERROR: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()