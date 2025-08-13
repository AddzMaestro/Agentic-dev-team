#!/usr/bin/env python3
"""
Populate ClinicLite database with comprehensive test data.
DataEngineer implementation following Context7 principles.
"""

import sqlite3
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import os

# Database path
DB_PATH = "/Users/addzmaestro/coding projects/Claude system/workspace/data/cliniclite.db"

# Botswana districts and clinic names
BOTSWANA_DISTRICTS = [
    "Gaborone", "Francistown", "Maun", "Kasane", "Serowe",
    "Palapye", "Kanye", "Molepolole", "Mahalapye", "Selibe Phikwe"
]

CLINIC_NAMES = [
    "Central Health Clinic", "District Primary Clinic", "Community Health Center",
    "Village Health Post", "Urban Health Clinic", "Rural Health Station",
    "Mobile Health Unit", "Maternal Health Center", "Family Care Clinic",
    "Primary Care Center"
]

# Medical visit types
VISIT_TYPES = [
    "ARV Refill", "TB Treatment", "Antenatal Care", "Postnatal Care",
    "Child Immunization", "Diabetes Checkup", "Hypertension Review",
    "General Consultation", "HIV Testing", "Family Planning"
]

# Stock items for clinics
STOCK_ITEMS = [
    ("Paracetamol 500mg", "tablets", 100, 500),
    ("Amoxicillin 250mg", "capsules", 50, 200),
    ("ARV - TDF/3TC/DTG", "tablets", 200, 1000),
    ("TB Medication - RHZE", "tablets", 100, 400),
    ("Insulin 100IU/ml", "vials", 20, 50),
    ("Metformin 500mg", "tablets", 100, 300),
    ("Amlodipine 5mg", "tablets", 80, 250),
    ("HIV Test Kits", "units", 50, 200),
    ("Pregnancy Test Kits", "units", 30, 100),
    ("Bandages 10cm", "rolls", 50, 150),
    ("Surgical Gloves", "boxes", 30, 100),
    ("Face Masks", "boxes", 40, 150),
    ("Hand Sanitizer 500ml", "bottles", 20, 80),
    ("Syringes 5ml", "units", 100, 500),
    ("Needles 21G", "units", 100, 500),
    ("Cotton Wool", "rolls", 30, 100),
    ("Iodine Solution", "bottles", 10, 30),
    ("Hydrocortisone Cream", "tubes", 20, 60),
    ("ORS Sachets", "units", 100, 400),
    ("Folic Acid 5mg", "tablets", 200, 800),
    ("Iron Tablets", "tablets", 150, 600),
    ("Vitamin A Capsules", "units", 100, 300),
    ("BCG Vaccine", "vials", 20, 50),
    ("Measles Vaccine", "vials", 20, 50),
    ("Polio Vaccine", "vials", 30, 80),
    ("Tetanus Vaccine", "vials", 25, 60),
    ("COVID-19 Vaccine", "vials", 50, 200),
    ("Antibiotic Eye Drops", "bottles", 20, 60),
    ("Cough Syrup", "bottles", 30, 100),
    ("Antimalarial Tablets", "tablets", 50, 200),
    ("Blood Pressure Monitor", "units", 2, 5),
    ("Thermometers", "units", 5, 15),
    ("Glucometer", "units", 3, 8),
    ("Test Strips - Glucose", "units", 100, 300),
    ("Wheelchair", "units", 1, 3),
    ("Crutches", "pairs", 2, 8),
    ("First Aid Kits", "units", 5, 15),
    ("Emergency Medications", "kits", 2, 5),
    ("Oxygen Masks", "units", 10, 30),
    ("IV Fluids - Saline", "bags", 30, 100),
    ("IV Giving Sets", "units", 30, 100),
    ("Catheter Sets", "units", 10, 30),
    ("Suture Materials", "packs", 20, 60),
    ("Local Anesthetic", "vials", 10, 30),
    ("Antibacterial Soap", "bottles", 20, 80),
    ("Examination Gloves", "boxes", 50, 200),
    ("Sterile Gauze", "packs", 40, 150),
    ("Medical Tape", "rolls", 30, 100),
    ("Antiseptic Wipes", "boxes", 20, 80),
    ("Emergency Blankets", "units", 5, 15)
]

# Setswana names for realistic data
FIRST_NAMES = [
    "Thabo", "Lerato", "Kagiso", "Dineo", "Mpho", "Kelebogile", "Tshepo", "Neo",
    "Refilwe", "Lebogang", "Tebogo", "Kefilwe", "Onkgopotse", "Boitumelo", "Kabelo",
    "Goitseone", "Kgomotso", "Oratile", "Tumelo", "Naledi", "Kitso", "Lorato",
    "Mothusi", "Keitumetse", "Bakang", "Olebogeng", "Tshegofatso", "Gofaone",
    "Mmapula", "Sesupo", "Bogolo", "Gaone", "Keabetswe", "Mogomotsi", "Thatayaone",
    "Bame", "Kealeboga", "Phenyo", "Amogelang", "Gorata", "Lefika", "Segametse",
    "Keorapetse", "Oteng", "Masego", "Kesego", "Ipeleng", "Unami", "Wame", "Onalenna"
]

LAST_NAMES = [
    "Mokoena", "Molefe", "Molapo", "Kgosana", "Tau", "Motsepe", "Sebego", "Phiri",
    "Khumalo", "Ndlovu", "Mogotsi", "Tshwene", "Kgomo", "Nkwe", "Phuti", "Moremi",
    "Khama", "Masire", "Mogae", "Seretse", "Bathoen", "Sechele", "Linchwe", "Kgari",
    "Tshekedi", "Dikgosi", "Matome", "Kopano", "Madikwe", "Lekgoa", "Montsho", "Gaborone",
    "Mophuting", "Ramotswa", "Tlokweng", "Lobatse", "Palapye", "Serowe", "Mahalapye",
    "Mochudi", "Kanye", "Molepolole", "Maun", "Kasane", "Francistown", "Selibe",
    "Letlhakane", "Orapa", "Jwaneng", "Sowa", "Rakops", "Tsabong"
]

def generate_phone_number():
    """Generate valid Botswana phone number in E.164 format."""
    # Botswana mobile prefixes: 71, 72, 73, 74, 75, 76, 77
    prefix = random.choice(['71', '72', '73', '74', '75', '76', '77'])
    number = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"+267{prefix}{number}"

def generate_uuid():
    """Generate unique identifier."""
    return str(uuid.uuid4())

def create_missing_tables(conn):
    """Create missing tables for comprehensive testing."""
    cursor = conn.cursor()
    
    # Create waitlist table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waitlist (
            waitlist_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            clinic_id TEXT NOT NULL,
            visit_type TEXT NOT NULL,
            priority INTEGER CHECK(priority BETWEEN 1 AND 5),
            requested_date DATE,
            notes TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
        )
    """)
    
    # Create messages_outbox table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages_outbox (
            message_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            phone_e164 TEXT NOT NULL,
            message_text TEXT NOT NULL,
            language TEXT CHECK(language IN ('EN', 'TSW')),
            message_type TEXT,
            scheduled_for TIMESTAMP,
            status TEXT DEFAULT 'pending',
            attempts INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_at TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)
    
    # Add risk-related columns to existing tables if missing
    cursor.execute("""
        PRAGMA table_info(patients)
    """)
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'age' not in columns:
        cursor.execute("ALTER TABLE patients ADD COLUMN age INTEGER")
    if 'gender' not in columns:
        cursor.execute("ALTER TABLE patients ADD COLUMN gender TEXT CHECK(gender IN ('M', 'F', 'O'))")
    if 'chronic_conditions' not in columns:
        cursor.execute("ALTER TABLE patients ADD COLUMN chronic_conditions TEXT")
    if 'last_visit_date' not in columns:
        cursor.execute("ALTER TABLE patients ADD COLUMN last_visit_date DATE")
    
    # Add risk_score and status to appointments if missing
    cursor.execute("""
        PRAGMA table_info(appointments)
    """)
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'risk_score' not in columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN risk_score REAL DEFAULT 0.5")
    if 'status' not in columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN status TEXT DEFAULT 'scheduled'")
    if 'appointment_time' not in columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN appointment_time TIME")
    
    conn.commit()

def populate_clinics(conn):
    """Populate clinics table with 10 clinics."""
    cursor = conn.cursor()
    
    # Clear existing clinics if less than 10
    cursor.execute("SELECT COUNT(*) FROM clinics")
    if cursor.fetchone()[0] < 10:
        cursor.execute("DELETE FROM clinics")
        
        clinic_ids = []
        for i in range(10):
            clinic_id = f"CLINIC-{str(uuid.uuid4())[:8]}"
            name = f"{CLINIC_NAMES[i]} {BOTSWANA_DISTRICTS[i]}"
            district = BOTSWANA_DISTRICTS[i]
            
            cursor.execute("""
                INSERT INTO clinics (clinic_id, name, district)
                VALUES (?, ?, ?)
            """, (clinic_id, name, district))
            clinic_ids.append(clinic_id)
        
        conn.commit()
        return clinic_ids
    else:
        cursor.execute("SELECT clinic_id FROM clinics")
        return [row[0] for row in cursor.fetchall()]

def populate_patients(conn, clinic_ids):
    """Populate patients table with 150+ patients."""
    cursor = conn.cursor()
    
    # Clear existing patients if less than 100
    cursor.execute("SELECT COUNT(*) FROM patients")
    if cursor.fetchone()[0] < 100:
        cursor.execute("DELETE FROM patients")
        
        patient_ids = []
        chronic_conditions_list = [
            "Diabetes", "Hypertension", "HIV", "TB", "Asthma",
            "Heart Disease", "Kidney Disease", "Cancer", "Epilepsy", None
        ]
        
        for i in range(150):
            patient_id = f"PAT-{str(uuid.uuid4())[:8]}"
            clinic_id = random.choice(clinic_ids)
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            phone = generate_phone_number()
            lang = random.choice(['EN', 'TSW'])
            age = random.randint(1, 85)
            gender = random.choice(['M', 'F'])
            chronic = random.choice(chronic_conditions_list)
            last_visit = (datetime.now() - timedelta(days=random.randint(1, 180))).date()
            
            cursor.execute("""
                INSERT INTO patients (patient_id, clinic_id, first_name, last_name, 
                                    phone_e164, preferred_lang, age, gender, 
                                    chronic_conditions, last_visit_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (patient_id, clinic_id, first_name, last_name, phone, lang,
                  age, gender, chronic, last_visit))
            patient_ids.append(patient_id)
        
        conn.commit()
        return patient_ids
    else:
        cursor.execute("SELECT patient_id FROM patients")
        return [row[0] for row in cursor.fetchall()]

def populate_appointments(conn, patient_ids, clinic_ids):
    """Populate appointments with 500+ records with varied statuses and risk scores."""
    cursor = conn.cursor()
    
    # Clear existing appointments if less than 500
    cursor.execute("SELECT COUNT(*) FROM appointments")
    if cursor.fetchone()[0] < 500:
        cursor.execute("DELETE FROM appointments")
        
        statuses = ['scheduled', 'completed', 'missed', 'cancelled']
        status_weights = [0.4, 0.3, 0.2, 0.1]  # 40% scheduled, 30% completed, etc.
        
        for i in range(600):
            appointment_id = f"APPT-{str(uuid.uuid4())[:8]}"
            patient_id = random.choice(patient_ids)
            
            # Get patient's clinic
            cursor.execute("SELECT clinic_id FROM patients WHERE patient_id = ?", (patient_id,))
            clinic_id = cursor.fetchone()[0]
            
            visit_type = random.choice(VISIT_TYPES)
            
            # Generate dates: past 30 days to next 30 days
            days_offset = random.randint(-30, 30)
            visit_date = (datetime.now() + timedelta(days=days_offset)).date()
            
            # Generate appointment time (clinic hours: 8:00 - 17:00)
            hour = random.randint(8, 16)
            minute = random.choice([0, 15, 30, 45])
            appointment_time = f"{hour:02d}:{minute:02d}:00"
            
            # Determine status based on date
            if visit_date < datetime.now().date():
                # Past appointments
                status = random.choices(['completed', 'missed', 'cancelled'], 
                                       weights=[0.6, 0.3, 0.1])[0]
            elif visit_date == datetime.now().date():
                # Today's appointments
                status = random.choices(['scheduled', 'completed'], weights=[0.5, 0.5])[0]
            else:
                # Future appointments
                status = random.choices(['scheduled', 'cancelled'], weights=[0.9, 0.1])[0]
            
            # Generate risk score: 30% high (>0.7), 50% medium (0.3-0.7), 20% low (<0.3)
            risk_category = random.choices(['high', 'medium', 'low'], weights=[0.3, 0.5, 0.2])[0]
            if risk_category == 'high':
                risk_score = round(random.uniform(0.7, 1.0), 3)
            elif risk_category == 'medium':
                risk_score = round(random.uniform(0.3, 0.7), 3)
            else:
                risk_score = round(random.uniform(0.0, 0.3), 3)
            
            cursor.execute("""
                INSERT INTO appointments (appointment_id, patient_id, clinic_id, 
                                        visit_type, next_visit_date, appointment_time,
                                        status, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (appointment_id, patient_id, clinic_id, visit_type, visit_date,
                  appointment_time, status, risk_score))
        
        conn.commit()

def populate_stock_items(conn, clinic_ids):
    """Populate stock items with 50+ items, 20% below reorder level."""
    cursor = conn.cursor()
    
    # Clear existing stock items if less than 50
    cursor.execute("SELECT COUNT(*) FROM stock_items")
    if cursor.fetchone()[0] < 50:
        cursor.execute("DELETE FROM stock_items")
        
        for clinic_id in clinic_ids:
            # Each clinic gets a subset of stock items
            clinic_items = random.sample(STOCK_ITEMS, k=random.randint(30, 45))
            
            for item_name, unit, reorder_level, max_qty in clinic_items:
                stock_id = f"STOCK-{str(uuid.uuid4())[:8]}"
                
                # 20% chance of being below reorder level
                if random.random() < 0.2:
                    # Low stock
                    on_hand_qty = random.randint(0, reorder_level - 1)
                else:
                    # Normal stock
                    on_hand_qty = random.randint(reorder_level, max_qty)
                
                cursor.execute("""
                    INSERT INTO stock_items (stock_id, clinic_id, item_name, 
                                           on_hand_qty, reorder_level, unit)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (stock_id, clinic_id, item_name, on_hand_qty, reorder_level, unit))
        
        conn.commit()

def populate_waitlist(conn, patient_ids, clinic_ids):
    """Populate waitlist with 20+ entries."""
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM waitlist")
    if cursor.fetchone()[0] < 20:
        cursor.execute("DELETE FROM waitlist")
        
        for i in range(25):
            waitlist_id = f"WAIT-{str(uuid.uuid4())[:8]}"
            patient_id = random.choice(patient_ids)
            
            # Get patient's clinic
            cursor.execute("SELECT clinic_id FROM patients WHERE patient_id = ?", (patient_id,))
            clinic_id = cursor.fetchone()[0]
            
            visit_type = random.choice(VISIT_TYPES)
            priority = random.randint(1, 5)
            requested_date = (datetime.now() + timedelta(days=random.randint(1, 14))).date()
            notes = f"Patient requested appointment for {visit_type}"
            status = random.choice(['pending', 'scheduled', 'cancelled'])
            
            cursor.execute("""
                INSERT INTO waitlist (waitlist_id, patient_id, clinic_id, visit_type,
                                    priority, requested_date, notes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (waitlist_id, patient_id, clinic_id, visit_type, priority,
                  requested_date, notes, status))
        
        conn.commit()

def populate_messages_outbox(conn, patient_ids):
    """Populate messages outbox with sample SMS reminders."""
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM messages_outbox")
    if cursor.fetchone()[0] < 50:
        cursor.execute("DELETE FROM messages_outbox")
        
        message_templates = {
            'EN': [
                "Reminder: Your {visit_type} appointment is on {date} at {time}. Reply CONFIRM or CANCEL.",
                "You have missed your {visit_type} appointment. Please call the clinic to reschedule.",
                "Your medication refill is due on {date}. Visit the clinic between 8:00-17:00."
            ],
            'TSW': [
                "Kgakololo: Kopano ya gago ya {visit_type} ke ka {date} ka {time}. Araba CONFIRM kgotsa CANCEL.",
                "O fetilwe ke kopano ya gago ya {visit_type}. Ka kopo letsetsa kliniki go rulaganya sesha.",
                "Melemo ya gago e tshwanetse go tsewa ka {date}. Etela kliniki magareng ga 8:00-17:00."
            ]
        }
        
        for i in range(60):
            message_id = f"MSG-{str(uuid.uuid4())[:8]}"
            patient_id = random.choice(patient_ids)
            
            # Get patient details
            cursor.execute("""
                SELECT phone_e164, preferred_lang 
                FROM patients WHERE patient_id = ?
            """, (patient_id,))
            phone, lang = cursor.fetchone()
            
            visit_type = random.choice(VISIT_TYPES)
            date = (datetime.now() + timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d')
            time = f"{random.randint(8, 16):02d}:{random.choice(['00', '30'])}:00"
            
            template = random.choice(message_templates[lang])
            message_text = template.format(visit_type=visit_type, date=date, time=time)
            
            message_type = random.choice(['appointment_reminder', 'missed_appointment', 'medication_refill'])
            scheduled_for = datetime.now() + timedelta(hours=random.randint(1, 48))
            status = random.choice(['pending', 'sent', 'failed'])
            attempts = 0 if status == 'pending' else random.randint(1, 3)
            sent_at = datetime.now() if status == 'sent' else None
            
            cursor.execute("""
                INSERT INTO messages_outbox (message_id, patient_id, phone_e164, message_text,
                                           language, message_type, scheduled_for, status,
                                           attempts, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (message_id, patient_id, phone, message_text, lang, message_type,
                  scheduled_for, status, attempts, sent_at))
        
        conn.commit()

def verify_data_integrity(conn):
    """Verify data integrity and print summary statistics."""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("DATABASE POPULATION COMPLETE - DATA INTEGRITY REPORT")
    print("="*60)
    
    # Table counts
    tables = ['clinics', 'patients', 'appointments', 'stock_items', 'waitlist', 'messages_outbox']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table.upper()}: {count} records")
    
    print("\n" + "-"*60)
    print("APPOINTMENTS ANALYSIS")
    print("-"*60)
    
    # Appointment status distribution
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM appointments 
        GROUP BY status
    """)
    print("\nStatus Distribution:")
    for status, count in cursor.fetchall():
        print(f"  {status}: {count}")
    
    # Risk score distribution
    cursor.execute("""
        SELECT 
            CASE 
                WHEN risk_score > 0.7 THEN 'High Risk (>0.7)'
                WHEN risk_score >= 0.3 THEN 'Medium Risk (0.3-0.7)'
                ELSE 'Low Risk (<0.3)'
            END as risk_category,
            COUNT(*) as count,
            ROUND(AVG(risk_score), 3) as avg_score
        FROM appointments
        GROUP BY risk_category
    """)
    print("\nRisk Score Distribution:")
    for category, count, avg_score in cursor.fetchall():
        print(f"  {category}: {count} appointments (avg: {avg_score})")
    
    # Date distribution
    cursor.execute("""
        SELECT 
            CASE 
                WHEN next_visit_date < DATE('now') THEN 'Past'
                WHEN next_visit_date = DATE('now') THEN 'Today'
                ELSE 'Future'
            END as time_category,
            COUNT(*) as count
        FROM appointments
        GROUP BY time_category
    """)
    print("\nDate Distribution:")
    for category, count in cursor.fetchall():
        print(f"  {category}: {count}")
    
    print("\n" + "-"*60)
    print("STOCK ANALYSIS")
    print("-"*60)
    
    # Low stock items
    cursor.execute("""
        SELECT 
            COUNT(*) as total_items,
            SUM(CASE WHEN on_hand_qty < reorder_level THEN 1 ELSE 0 END) as low_stock_items,
            ROUND(100.0 * SUM(CASE WHEN on_hand_qty < reorder_level THEN 1 ELSE 0 END) / COUNT(*), 1) as low_stock_percentage
        FROM stock_items
    """)
    total, low, percentage = cursor.fetchone()
    print(f"Total Stock Items: {total}")
    print(f"Low Stock Items: {low} ({percentage}%)")
    
    # Critical stock (zero quantity)
    cursor.execute("""
        SELECT COUNT(*) FROM stock_items WHERE on_hand_qty = 0
    """)
    critical = cursor.fetchone()[0]
    print(f"Out of Stock Items: {critical}")
    
    print("\n" + "-"*60)
    print("PATIENT DEMOGRAPHICS")
    print("-"*60)
    
    # Language distribution
    cursor.execute("""
        SELECT preferred_lang, COUNT(*) as count 
        FROM patients 
        GROUP BY preferred_lang
    """)
    print("\nLanguage Preference:")
    for lang, count in cursor.fetchall():
        print(f"  {lang}: {count}")
    
    # Age distribution
    cursor.execute("""
        SELECT 
            CASE 
                WHEN age < 18 THEN 'Pediatric (<18)'
                WHEN age < 65 THEN 'Adult (18-64)'
                ELSE 'Elderly (65+)'
            END as age_group,
            COUNT(*) as count
        FROM patients
        GROUP BY age_group
    """)
    print("\nAge Distribution:")
    for group, count in cursor.fetchall():
        print(f"  {group}: {count}")
    
    # Chronic conditions
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN chronic_conditions IS NOT NULL THEN 1 ELSE 0 END) as with_conditions
        FROM patients
    """)
    total, with_conditions = cursor.fetchone()
    print(f"\nPatients with Chronic Conditions: {with_conditions}/{total} ({round(100*with_conditions/total, 1)}%)")
    
    print("\n" + "-"*60)
    print("SAMPLE QUERIES - DATA VALIDATION")
    print("-"*60)
    
    # Upcoming appointments (next 7 days)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM appointments 
        WHERE next_visit_date BETWEEN DATE('now') AND DATE('now', '+7 days')
        AND status = 'scheduled'
    """)
    print(f"\nUpcoming Appointments (next 7 days): {cursor.fetchone()[0]}")
    
    # Missed appointments (past 7 days)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM appointments 
        WHERE next_visit_date BETWEEN DATE('now', '-7 days') AND DATE('now')
        AND status = 'missed'
    """)
    print(f"Missed Appointments (past 7 days): {cursor.fetchone()[0]}")
    
    # High-risk patients needing follow-up
    cursor.execute("""
        SELECT COUNT(DISTINCT patient_id)
        FROM appointments
        WHERE risk_score > 0.7
        AND status IN ('scheduled', 'missed')
    """)
    print(f"High-risk patients needing follow-up: {cursor.fetchone()[0]}")
    
    # Pending messages
    cursor.execute("""
        SELECT COUNT(*)
        FROM messages_outbox
        WHERE status = 'pending'
    """)
    print(f"Pending SMS messages: {cursor.fetchone()[0]}")
    
    print("\n" + "="*60)
    print("DATABASE READY FOR COMPREHENSIVE TESTING")
    print("="*60)

def main():
    """Main execution function."""
    print("Starting database population for ClinicLite testing...")
    print(f"Database path: {DB_PATH}")
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Create missing tables
        print("\n1. Creating missing tables...")
        create_missing_tables(conn)
        
        # Populate clinics
        print("2. Populating clinics...")
        clinic_ids = populate_clinics(conn)
        print(f"   Created/verified {len(clinic_ids)} clinics")
        
        # Populate patients
        print("3. Populating patients...")
        patient_ids = populate_patients(conn, clinic_ids)
        print(f"   Created/verified {len(patient_ids)} patients")
        
        # Populate appointments
        print("4. Populating appointments...")
        populate_appointments(conn, patient_ids, clinic_ids)
        print("   Created 600+ appointments with varied statuses and risk scores")
        
        # Populate stock items
        print("5. Populating stock items...")
        populate_stock_items(conn, clinic_ids)
        print("   Created stock items with 20% below reorder level")
        
        # Populate waitlist
        print("6. Populating waitlist...")
        populate_waitlist(conn, patient_ids, clinic_ids)
        print("   Created 25+ waitlist entries")
        
        # Populate messages outbox
        print("7. Populating messages outbox...")
        populate_messages_outbox(conn, patient_ids)
        print("   Created 60+ SMS messages")
        
        # Verify data integrity
        verify_data_integrity(conn)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    print("\n✅ Database population complete!")
    print(f"Database ready at: {DB_PATH}")

if __name__ == "__main__":
    main()