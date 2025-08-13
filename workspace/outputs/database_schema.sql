-- ClinicLite Botswana Database Schema
-- Enhanced with No-Show Prediction & Smart Scheduling
-- SQLite 3.x compatible

-- ============================================================================
-- CORE TABLES (Existing System)
-- ============================================================================

-- Clinics table
CREATE TABLE IF NOT EXISTS clinics (
    clinic_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    district TEXT NOT NULL,
    latitude REAL,                      -- For distance calculations
    longitude REAL,                      -- For distance calculations
    capacity_morning INTEGER DEFAULT 20, -- Morning slot capacity
    capacity_afternoon INTEGER DEFAULT 20, -- Afternoon slot capacity
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    clinic_id TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone_e164 TEXT NOT NULL,
    preferred_lang TEXT CHECK(preferred_lang IN ('EN', 'TSW')) DEFAULT 'EN',
    date_of_birth DATE,                 -- For demographic analysis
    gender TEXT CHECK(gender IN ('M', 'F', 'O')),
    address TEXT,
    distance_km REAL,                   -- Distance from clinic
    transport_mode TEXT CHECK(transport_mode IN ('WALKING', 'COMBI', 'PRIVATE', 'UNKNOWN')) DEFAULT 'UNKNOWN',
    no_show_count INTEGER DEFAULT 0,    -- Historical no-show count
    total_appointments INTEGER DEFAULT 0, -- Total appointments scheduled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    clinic_id TEXT NOT NULL,
    visit_type TEXT NOT NULL,
    next_visit_date DATE NOT NULL,
    time_slot TEXT CHECK(time_slot IN ('MORNING', 'AFTERNOON')),
    status TEXT DEFAULT 'SCHEDULED' CHECK(status IN ('SCHEDULED', 'ATTENDED', 'NO_SHOW', 'CANCELLED', 'RESCHEDULED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
);

-- Stock items table
CREATE TABLE IF NOT EXISTS stock_items (
    stock_id TEXT PRIMARY KEY,
    clinic_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    on_hand_qty INTEGER NOT NULL CHECK(on_hand_qty >= 0),
    reorder_level INTEGER NOT NULL CHECK(reorder_level >= 0),
    unit TEXT NOT NULL,
    last_reorder_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
);

-- ============================================================================
-- NO-SHOW PREDICTION TABLES
-- ============================================================================

-- Risk scores table for caching predictions
CREATE TABLE IF NOT EXISTS risk_scores (
    score_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    appointment_id TEXT NOT NULL,
    risk_percentage REAL NOT NULL CHECK(risk_percentage >= 0 AND risk_percentage <= 100),
    risk_level TEXT NOT NULL CHECK(risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    
    -- Factor scores (weights: distance=35%, history=25%, weather=20%, demographic=20%)
    distance_score REAL,
    history_score REAL,
    weather_score REAL,
    demographic_score REAL,
    
    -- Confidence metrics
    confidence_score REAL CHECK(confidence_score >= 0 AND confidence_score <= 100),
    sample_size INTEGER,
    model_version TEXT DEFAULT 'v1.0',
    
    -- Metadata
    day_of_week TEXT,
    is_rainy_season BOOLEAN DEFAULT 0,
    
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- Cache expiration
    
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

-- Prediction history for model training and accuracy tracking
CREATE TABLE IF NOT EXISTS prediction_history (
    history_id TEXT PRIMARY KEY,
    appointment_id TEXT NOT NULL,
    patient_id TEXT NOT NULL,
    clinic_id TEXT NOT NULL,
    
    -- Prediction details
    predicted_risk REAL NOT NULL CHECK(predicted_risk >= 0 AND predicted_risk <= 100),
    predicted_level TEXT CHECK(predicted_level IN ('LOW', 'MEDIUM', 'HIGH')),
    prediction_date DATE NOT NULL,
    
    -- Actual outcome
    actual_outcome TEXT CHECK(actual_outcome IN ('ATTENDED', 'NO_SHOW', 'CANCELLED', 'PENDING')),
    outcome_date DATE,
    
    -- Feature snapshot at prediction time (JSON)
    features_json TEXT NOT NULL,
    
    -- Model performance tracking
    model_version TEXT,
    accuracy_score REAL, -- Calculated after outcome known
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
);

-- Prediction factors configuration
CREATE TABLE IF NOT EXISTS prediction_factors (
    factor_id TEXT PRIMARY KEY,
    factor_name TEXT NOT NULL UNIQUE,
    weight REAL NOT NULL CHECK(weight >= 0 AND weight <= 1),
    is_active BOOLEAN DEFAULT 1,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default factor weights
INSERT OR IGNORE INTO prediction_factors (factor_id, factor_name, weight, description) VALUES
('F001', 'distance', 0.35, 'Distance from clinic in kilometers'),
('F002', 'history', 0.25, 'Previous no-show history'),
('F003', 'weather', 0.20, 'Weather and seasonal factors'),
('F004', 'demographics', 0.20, 'Age group and gender factors');

-- ============================================================================
-- SMART SCHEDULING TABLES
-- ============================================================================

-- Overbooking configuration per clinic/date/slot
CREATE TABLE IF NOT EXISTS overbooking_config (
    config_id TEXT PRIMARY KEY,
    clinic_id TEXT NOT NULL,
    date DATE NOT NULL,
    time_slot TEXT NOT NULL CHECK(time_slot IN ('MORNING', 'AFTERNOON')),
    
    -- Capacity settings
    baseline_capacity INTEGER NOT NULL,
    maximum_capacity INTEGER NOT NULL CHECK(maximum_capacity <= baseline_capacity * 1.25),
    current_bookings INTEGER DEFAULT 0,
    recommended_capacity INTEGER,
    
    -- Decision factors
    historical_no_show_rate REAL,
    day_multiplier REAL DEFAULT 1.0,     -- Monday=1.18, Friday=1.15, etc.
    seasonal_adjustment REAL DEFAULT 1.0, -- Rainy season=1.4
    staff_availability REAL DEFAULT 1.0,
    
    -- Constraints
    max_overbook_percentage INTEGER DEFAULT 25,
    min_staff_ratio REAL DEFAULT 0.2,
    emergency_buffer INTEGER DEFAULT 2,
    
    -- Audit
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT DEFAULT 'SYSTEM',
    
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id),
    UNIQUE(clinic_id, date, time_slot)
);

-- Day-of-week multipliers for overbooking
CREATE TABLE IF NOT EXISTS day_multipliers (
    day_name TEXT PRIMARY KEY CHECK(day_name IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    multiplier REAL NOT NULL DEFAULT 1.0,
    avg_no_show_rate REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default day multipliers based on research
INSERT OR IGNORE INTO day_multipliers (day_name, multiplier, avg_no_show_rate) VALUES
('Monday', 1.18, 0.38),
('Tuesday', 1.08, 0.32),
('Wednesday', 1.05, 0.30),
('Thursday', 1.05, 0.30),
('Friday', 1.15, 0.35),
('Saturday', 1.10, 0.33),
('Sunday', 1.00, 0.28);

-- ============================================================================
-- WAITLIST MANAGEMENT TABLES
-- ============================================================================

-- Waitlist queue for appointment slots
CREATE TABLE IF NOT EXISTS waitlist_queue (
    entry_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    clinic_id TEXT NOT NULL,
    
    -- Scheduling preferences
    earliest_date DATE NOT NULL,
    latest_date DATE NOT NULL,
    preferred_times TEXT, -- JSON array of time preferences
    acceptable_days TEXT, -- JSON array of acceptable days
    max_distance_km REAL,
    
    -- Priority calculation
    priority_level INTEGER NOT NULL CHECK(priority_level BETWEEN 1 AND 5), -- 1=Urgent, 5=Routine
    priority_score REAL,
    medical_urgency TEXT,
    wait_time_days INTEGER DEFAULT 0,
    
    -- Status tracking
    status TEXT NOT NULL DEFAULT 'WAITING' CHECK(status IN ('WAITING', 'NOTIFIED', 'SCHEDULED', 'EXPIRED', 'CANCELLED')),
    notification_count INTEGER DEFAULT 0,
    last_notified_at TIMESTAMP,
    
    -- Timestamps
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    scheduled_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
);

-- Slot recovery tracking
CREATE TABLE IF NOT EXISTS slot_recovery (
    recovery_id TEXT PRIMARY KEY,
    original_appointment_id TEXT NOT NULL,
    clinic_id TEXT NOT NULL,
    slot_datetime TIMESTAMP NOT NULL,
    
    -- Cancellation details
    cancellation_reason TEXT,
    cancelled_at TIMESTAMP NOT NULL,
    cancelled_by TEXT,
    
    -- Recovery process
    recovery_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recovery_completed_at TIMESTAMP,
    filled_by_patient_id TEXT,
    recovery_successful BOOLEAN DEFAULT 0,
    time_to_fill_hours REAL,
    
    -- Notifications sent
    patients_notified INTEGER DEFAULT 0,
    responses_received INTEGER DEFAULT 0,
    
    FOREIGN KEY (original_appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id),
    FOREIGN KEY (filled_by_patient_id) REFERENCES patients(patient_id)
);

-- ============================================================================
-- SMS COMMUNICATION TABLES
-- ============================================================================

-- SMS interactions (two-way communication)
CREATE TABLE IF NOT EXISTS sms_interactions (
    interaction_id TEXT PRIMARY KEY,
    patient_id TEXT,
    phone_number TEXT NOT NULL,
    
    -- Message details
    direction TEXT NOT NULL CHECK(direction IN ('OUTBOUND', 'INBOUND')),
    message_text TEXT NOT NULL,
    language TEXT CHECK(language IN ('EN', 'TSW')),
    template_id TEXT,
    char_count INTEGER CHECK(char_count <= 160),
    
    -- Context
    appointment_id TEXT,
    interaction_type TEXT CHECK(interaction_type IN ('REMINDER', 'RESCHEDULE', 'CONFIRMATION', 'CANCELLATION', 'WAITLIST')),
    reply_code_expected BOOLEAN DEFAULT 0,
    parent_message_id TEXT, -- For conversation threading
    
    -- Status tracking
    status TEXT NOT NULL DEFAULT 'QUEUED' CHECK(status IN ('QUEUED', 'SENT', 'DELIVERED', 'FAILED', 'REPLIED')),
    gateway_id TEXT, -- External SMS gateway reference
    error_message TEXT,
    
    -- Response handling (for inbound)
    response_code TEXT CHECK(response_code IN ('1', '2')), -- 1=tomorrow, 2=next week
    action_taken TEXT,
    processed_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    replied_at TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id),
    FOREIGN KEY (parent_message_id) REFERENCES sms_interactions(interaction_id)
);

-- SMS templates for consistent messaging
CREATE TABLE IF NOT EXISTS sms_templates (
    template_id TEXT PRIMARY KEY,
    template_name TEXT NOT NULL UNIQUE,
    language TEXT NOT NULL CHECK(language IN ('EN', 'TSW')),
    template_text TEXT NOT NULL,
    placeholders TEXT, -- JSON array of placeholder names
    char_count INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default SMS templates
INSERT OR IGNORE INTO sms_templates (template_id, template_name, language, template_text, placeholders) VALUES
('T001', 'reminder_en', 'EN', '[EN] Reminder: You have an appointment at {clinic} on {date} at {time}. Reply 1 for tomorrow, 2 for next week to reschedule.', '["clinic", "date", "time"]'),
('T002', 'reminder_tsw', 'TSW', '[TSW] Gakologelwa: O na le bookelo kwa {clinic} ka {date} ka {time}. Araba 1 go beela maabane, 2 bekeng e e tlang.', '["clinic", "date", "time"]'),
('T003', 'confirmation_en', 'EN', '[EN] Confirmed: Your appointment is now on {date} at {time}.', '["date", "time"]'),
('T004', 'confirmation_tsw', 'TSW', '[TSW] Netefaditswe: Bookelo ya gago jaanong ke ka {date} ka {time}.', '["date", "time"]'),
('T005', 'waitlist_en', 'EN', '[EN] A slot is available on {date} at {time}. Reply 1 to confirm.', '["date", "time"]'),
('T006', 'waitlist_tsw', 'TSW', '[TSW] Go na le nako e e leng teng ka {date} ka {time}. Araba 1 go netefatsa.', '["date", "time"]');

-- ============================================================================
-- ANALYTICS AND REPORTING TABLES
-- ============================================================================

-- No-show patterns analysis
CREATE TABLE IF NOT EXISTS no_show_patterns (
    pattern_id TEXT PRIMARY KEY,
    clinic_id TEXT NOT NULL,
    analysis_date DATE NOT NULL,
    
    -- Pattern metrics
    total_appointments INTEGER,
    no_show_count INTEGER,
    no_show_rate REAL,
    
    -- Breakdown by factors
    by_day_of_week TEXT, -- JSON object
    by_time_slot TEXT,   -- JSON object
    by_age_group TEXT,   -- JSON object
    by_distance TEXT,    -- JSON object
    by_weather TEXT,     -- JSON object
    
    -- Trends
    trend_direction TEXT CHECK(trend_direction IN ('IMPROVING', 'WORSENING', 'STABLE')),
    trend_percentage REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id),
    UNIQUE(clinic_id, analysis_date)
);

-- Capacity utilization tracking
CREATE TABLE IF NOT EXISTS capacity_utilization (
    utilization_id TEXT PRIMARY KEY,
    clinic_id TEXT NOT NULL,
    date DATE NOT NULL,
    time_slot TEXT CHECK(time_slot IN ('MORNING', 'AFTERNOON')),
    
    -- Capacity metrics
    baseline_capacity INTEGER,
    actual_bookings INTEGER,
    actual_attendance INTEGER,
    no_shows INTEGER,
    
    -- Utilization percentages
    booking_rate REAL,      -- bookings/capacity
    attendance_rate REAL,   -- attendance/capacity
    no_show_rate REAL,      -- no_shows/bookings
    
    -- Overbooking impact
    was_overbooked BOOLEAN DEFAULT 0,
    overbook_percentage REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id),
    UNIQUE(clinic_id, date, time_slot)
);

-- ============================================================================
-- SYSTEM TABLES
-- ============================================================================

-- Sync queue for offline operation
CREATE TABLE IF NOT EXISTS sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL CHECK(operation IN ('INSERT', 'UPDATE', 'DELETE')),
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    payload TEXT NOT NULL, -- JSON payload
    status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP
);

-- Audit log for compliance
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    old_value TEXT, -- JSON
    new_value TEXT, -- JSON
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Core table indexes
CREATE INDEX IF NOT EXISTS idx_patients_clinic ON patients(clinic_id);
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone_e164);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(next_visit_date);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status, next_visit_date);
CREATE INDEX IF NOT EXISTS idx_stock_clinic ON stock_items(clinic_id);
CREATE INDEX IF NOT EXISTS idx_stock_levels ON stock_items(on_hand_qty, reorder_level);

-- Prediction indexes
CREATE INDEX IF NOT EXISTS idx_risk_patient ON risk_scores(patient_id, calculated_at DESC);
CREATE INDEX IF NOT EXISTS idx_risk_appointment ON risk_scores(appointment_id);
CREATE INDEX IF NOT EXISTS idx_risk_level ON risk_scores(risk_level, calculated_at DESC);
CREATE INDEX IF NOT EXISTS idx_risk_high ON risk_scores(calculated_at DESC) WHERE risk_level = 'HIGH';
CREATE INDEX IF NOT EXISTS idx_prediction_accuracy ON prediction_history(prediction_date, actual_outcome);
CREATE INDEX IF NOT EXISTS idx_prediction_patient ON prediction_history(patient_id, prediction_date DESC);

-- Scheduling indexes
CREATE INDEX IF NOT EXISTS idx_overbook_date ON overbooking_config(date, clinic_id);
CREATE INDEX IF NOT EXISTS idx_overbook_clinic ON overbooking_config(clinic_id, date);

-- Waitlist indexes
CREATE INDEX IF NOT EXISTS idx_waitlist_priority ON waitlist_queue(clinic_id, priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_waitlist_active ON waitlist_queue(priority_score DESC) WHERE status = 'WAITING';
CREATE INDEX IF NOT EXISTS idx_waitlist_patient ON waitlist_queue(patient_id, status);
CREATE INDEX IF NOT EXISTS idx_recovery_success ON slot_recovery(recovery_successful, time_to_fill_hours);

-- SMS indexes
CREATE INDEX IF NOT EXISTS idx_sms_patient ON sms_interactions(patient_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sms_status ON sms_interactions(status, created_at);
CREATE INDEX IF NOT EXISTS idx_sms_pending ON sms_interactions(created_at) WHERE status = 'QUEUED';
CREATE INDEX IF NOT EXISTS idx_sms_replies ON sms_interactions(parent_message_id);
CREATE INDEX IF NOT EXISTS idx_sms_appointment ON sms_interactions(appointment_id);

-- Sync and audit indexes
CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_queue(status, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_log(entity_type, entity_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id, created_at DESC);

-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

-- High-risk appointments view
CREATE VIEW IF NOT EXISTS v_high_risk_appointments AS
SELECT 
    a.appointment_id,
    a.next_visit_date,
    a.time_slot,
    p.patient_id,
    p.first_name || ' ' || p.last_name AS patient_name,
    p.phone_e164,
    p.preferred_lang,
    r.risk_percentage,
    r.risk_level,
    c.name AS clinic_name
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN clinics c ON a.clinic_id = c.clinic_id
LEFT JOIN risk_scores r ON a.appointment_id = r.appointment_id
WHERE a.status = 'SCHEDULED'
    AND a.next_visit_date >= DATE('now')
    AND (r.risk_level = 'HIGH' OR r.risk_percentage > 60)
ORDER BY a.next_visit_date, r.risk_percentage DESC;

-- Waitlist priority view
CREATE VIEW IF NOT EXISTS v_waitlist_priority AS
SELECT 
    w.entry_id,
    w.patient_id,
    p.first_name || ' ' || p.last_name AS patient_name,
    p.phone_e164,
    w.priority_level,
    w.priority_score,
    w.medical_urgency,
    w.wait_time_days,
    w.earliest_date,
    w.latest_date,
    c.name AS clinic_name
FROM waitlist_queue w
JOIN patients p ON w.patient_id = p.patient_id
JOIN clinics c ON w.clinic_id = c.clinic_id
WHERE w.status = 'WAITING'
    AND w.expires_at > DATETIME('now')
ORDER BY w.priority_score DESC, w.added_at;

-- Daily capacity overview
CREATE VIEW IF NOT EXISTS v_daily_capacity AS
SELECT 
    c.clinic_id,
    c.name AS clinic_name,
    o.date,
    o.time_slot,
    o.baseline_capacity,
    o.current_bookings,
    o.recommended_capacity,
    ROUND((o.current_bookings * 100.0 / o.baseline_capacity), 1) AS booking_percentage,
    o.historical_no_show_rate,
    o.day_multiplier,
    o.seasonal_adjustment
FROM overbooking_config o
JOIN clinics c ON o.clinic_id = c.clinic_id
WHERE o.date >= DATE('now')
ORDER BY o.date, c.name, o.time_slot;

-- ============================================================================
-- TRIGGERS FOR DATA INTEGRITY
-- ============================================================================

-- Update patient no-show count on appointment status change
CREATE TRIGGER IF NOT EXISTS update_patient_no_show_count
AFTER UPDATE OF status ON appointments
WHEN NEW.status = 'NO_SHOW' AND OLD.status != 'NO_SHOW'
BEGIN
    UPDATE patients 
    SET no_show_count = no_show_count + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE patient_id = NEW.patient_id;
END;

-- Update patient total appointments on new appointment
CREATE TRIGGER IF NOT EXISTS update_patient_appointment_count
AFTER INSERT ON appointments
BEGIN
    UPDATE patients 
    SET total_appointments = total_appointments + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE patient_id = NEW.patient_id;
END;

-- Auto-calculate waitlist priority score
CREATE TRIGGER IF NOT EXISTS calculate_waitlist_priority
BEFORE INSERT ON waitlist_queue
BEGIN
    UPDATE waitlist_queue
    SET priority_score = (
        (5 - NEW.priority_level) * 20 +  -- Priority level (inverted)
        MIN(NEW.wait_time_days * 2, 30) + -- Wait time factor
        CASE 
            WHEN NEW.medical_urgency IS NOT NULL THEN 20 
            ELSE 0 
        END
    )
    WHERE entry_id = NEW.entry_id;
END;

-- Update timestamps
CREATE TRIGGER IF NOT EXISTS update_clinics_timestamp
AFTER UPDATE ON clinics
BEGIN
    UPDATE clinics SET updated_at = CURRENT_TIMESTAMP WHERE clinic_id = NEW.clinic_id;
END;

CREATE TRIGGER IF NOT EXISTS update_patients_timestamp
AFTER UPDATE ON patients
BEGIN
    UPDATE patients SET updated_at = CURRENT_TIMESTAMP WHERE patient_id = NEW.patient_id;
END;

CREATE TRIGGER IF NOT EXISTS update_appointments_timestamp
AFTER UPDATE ON appointments
BEGIN
    UPDATE appointments SET updated_at = CURRENT_TIMESTAMP WHERE appointment_id = NEW.appointment_id;
END;

-- ============================================================================
-- MIGRATION SUPPORT
-- ============================================================================

-- Migration tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Record this migration
INSERT OR IGNORE INTO schema_migrations (version, name) VALUES 
(1, 'initial_schema'),
(2, 'no_show_prediction_enhancement');

-- ============================================================================
-- INITIAL DATA SEEDING (for testing)
-- ============================================================================

-- Sample clinic (commented out for production)
-- INSERT OR IGNORE INTO clinics (clinic_id, name, district, latitude, longitude) VALUES
-- ('CLN001', 'Gaborone Central Clinic', 'South-East', -24.6282, 25.9231);

-- ============================================================================
-- UTILITY QUERIES (Documentation)
-- ============================================================================

/*
-- Get high-risk appointments for tomorrow
SELECT * FROM v_high_risk_appointments 
WHERE next_visit_date = DATE('now', '+1 day');

-- Calculate clinic no-show rate for last month
SELECT 
    clinic_id,
    COUNT(*) as total_appointments,
    SUM(CASE WHEN status = 'NO_SHOW' THEN 1 ELSE 0 END) as no_shows,
    ROUND(SUM(CASE WHEN status = 'NO_SHOW' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as no_show_rate
FROM appointments
WHERE next_visit_date >= DATE('now', '-30 days')
GROUP BY clinic_id;

-- Find optimal overbooking for next week
SELECT 
    date,
    clinic_name,
    time_slot,
    baseline_capacity,
    recommended_capacity,
    ROUND((recommended_capacity - baseline_capacity) * 100.0 / baseline_capacity, 1) as overbook_percentage
FROM v_daily_capacity
WHERE date BETWEEN DATE('now') AND DATE('now', '+7 days')
ORDER BY date, clinic_name;

-- Get waitlist candidates for a specific slot
SELECT * FROM v_waitlist_priority
WHERE earliest_date <= '2024-03-15'
    AND latest_date >= '2024-03-15'
LIMIT 5;

-- SMS response rate analysis
SELECT 
    DATE(created_at) as date,
    COUNT(*) as messages_sent,
    SUM(CASE WHEN status = 'REPLIED' THEN 1 ELSE 0 END) as replies_received,
    ROUND(SUM(CASE WHEN status = 'REPLIED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as response_rate
FROM sms_interactions
WHERE direction = 'OUTBOUND'
    AND reply_code_expected = 1
    AND created_at >= DATE('now', '-7 days')
GROUP BY DATE(created_at);
*/