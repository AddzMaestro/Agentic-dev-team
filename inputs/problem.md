# ClinicLite Botswana: SMS Reminders & Low-Stock Alerts (demo-ready)

## Elevator pitch
Primary clinics need a simple way to (1) remind patients about upcoming or missed visits and (2) avoid medicine stock-outs.  
**ClinicLite** is a lightweight, offline-friendly web app that:
- Uploads CSVs for clinics, patients, appointments, and stock
- Shows a one-screen dashboard for upcoming/missed visits + low-stock items
- Generates **SMS reminder messages** (simulated) in English or Setswana-tagged format
- Creates a **low-stock alert** and a simple reorder CSV

## Users & pains
- **Reception/Nurse-in-Charge:** manual phone calls, no-shows, no quick view of who’s due.
- **Pharmacy Tech:** reactive stock management; reorder happens after stock-out.
- **Patients:** forget appointments; want clear reminders.

## MVP views (demo-friendly)
1) **Upload**: import `clinics.csv`, `patients.csv`, `appointments.csv`, `stock.csv`
2) **Dashboard**: cards/tables for:
   - Upcoming visits (next 7 days)
   - Missed visits (in past 7 days)
   - Low-stock items (on_hand < reorder_level)
3) **Reminders**:
   - Select patients (EN/TSW preference from CSV)
   - Preview SMS text (simulated send = append to `messages_outbox.csv`)
   - Language toggle adds a visible `[EN]` or `[TSW]` tag in the message (for testing)
4) **Stock Alerts**:
   - List low items
   - One-click **“Draft Reorder CSV”** (writes `reorder_draft.csv`)

## IDKs (Information-Dense Keywords)
Offline-first, CSV Upload, Low Bandwidth, SMS Reminder (Simulated), Missed Visit, Upcoming Visit, Low-Stock Threshold, Reorder Draft, Language Toggle (EN/TSW), Clinic Dashboard.

## TYPE-first (Types, Invariants, Protocols, Examples)
**Types**
- `Clinic { clinic_id, name, district }`
- `Patient { patient_id, clinic_id, first_name, last_name, phone_e164, preferred_lang ∈ {EN,TSW} }`
- `Appointment { appointment_id, patient_id, clinic_id, visit_type, next_visit_date }`
- `StockItem { stock_id, clinic_id, item_name, on_hand_qty >= 0, reorder_level >= 0, unit }`
- `ReminderMessage { patient_id, lang_tag ∈ { "[EN]","[TSW]" }, text, created_at }`

**Invariants**
- `next_visit_date` is a valid ISO date.
- `on_hand_qty < reorder_level` ⇒ low-stock.
- `phone_e164` present for reminders.

**Protocols (demo endpoints)**
- `POST /upload` → store CSVs
- `GET /dashboard` → compute upcoming/missed/low-stock
- `POST /reminders/preview` → generate `[EN]/[TSW]` messages, do not send
- `POST /reminders/queue` → append to `messages_outbox.csv`
- `POST /stock/reorder-draft` → write `reorder_draft.csv`

**Examples → Acceptance tests**
- If a patient’s `next_visit_date` is tomorrow → appears under Upcoming.
- If `next_visit_date` was 2 days ago → appears under Missed.
- If `on_hand_qty < reorder_level` → appears under Low-stock.
- When language toggle is **TSW**, reminder text begins with `[TSW]`.
- Clicking **Queue Reminders** appends rows to `messages_outbox.csv`.
- Clicking **Draft Reorder CSV** creates `reorder_draft.csv` with the right items.
