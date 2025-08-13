# ClinicLite Botswana Specification
> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.
> Based on Context7 principles - https://context7.com/

## High-Level Objective

Build **ClinicLite Botswana**: A lightweight, offline-friendly web application for primary clinics to manage SMS reminders for patient appointments and monitor medicine stock levels to prevent stock-outs.

## Mid-Level Objectives

1. **CSV Data Upload System**: Enable bulk import of clinic, patient, appointment, and stock data via CSV files
2. **Dashboard Interface**: Create a single-screen view showing upcoming visits, missed visits, and low-stock items
3. **SMS Reminder Generation**: Generate patient reminders in English or Setswana with language tagging
4. **Stock Management**: Track inventory levels and generate reorder alerts when items fall below thresholds
5. **Offline-First Architecture**: Ensure the system works reliably with limited connectivity
6. **Zero-Error Delivery**: Achieve 100% test pass rate with Playwright-based testing

## IDKs (Important Domain Keywords)

1. **Offline-first**: System must function without constant internet connectivity, using local storage and batch syncing
2. **CSV Upload**: Primary data input method for clinics, patients, appointments, and stock inventory
3. **Low Bandwidth**: Optimized for environments with limited internet speeds (< 256 kbps)
4. **SMS Reminder (Simulated)**: Text message generation for appointment reminders, queued to outbox file
5. **Missed Visit**: Appointments where next_visit_date is in the past 7 days
6. **Upcoming Visit**: Appointments scheduled within the next 7 days
7. **Low-Stock Threshold**: When on_hand_qty falls below reorder_level for any stock item
8. **Reorder Draft**: Auto-generated CSV file listing items needing reorder
9. **Language Toggle (EN/TSW)**: Support for English and Setswana with visible language tags
10. **Clinic Dashboard**: Single-page interface showing all critical information at a glance

## TYPE Artifacts

### Types (Data Structures)
```python
# Define the core data types for this project
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime, date
from enum import Enum

class Language(str, Enum):
    """Supported languages for SMS reminders"""
    EN = "EN"  # English
    TSW = "TSW"  # Setswana

class Clinic(BaseModel):
    """Primary health clinic entity"""
    clinic_id: str = Field(..., description="Unique clinic identifier")
    name: str = Field(..., description="Clinic name")
    district: str = Field(..., description="District location")
    
    @validator('clinic_id')
    def validate_clinic_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError("clinic_id must be at least 3 characters")
        return v

class Patient(BaseModel):
    """Patient registered at a clinic"""
    patient_id: str = Field(..., description="Unique patient identifier")
    clinic_id: str = Field(..., description="Associated clinic ID")
    first_name: str = Field(..., description="Patient first name")
    last_name: str = Field(..., description="Patient last name")
    phone_e164: str = Field(..., description="Phone number in E.164 format")
    preferred_lang: Language = Field(Language.EN, description="Preferred language")
    
    @validator('phone_e164')
    def validate_phone(cls, v):
        if not v.startswith('+'):
            raise ValueError("Phone must be in E.164 format (starting with +)")
        if len(v) < 10:
            raise ValueError("Phone number too short")
        return v

class Appointment(BaseModel):
    """Scheduled patient appointment"""
    appointment_id: str = Field(..., description="Unique appointment identifier")
    patient_id: str = Field(..., description="Associated patient ID")
    clinic_id: str = Field(..., description="Associated clinic ID")
    visit_type: str = Field(..., description="Type of visit (routine, follow-up, etc)")
    next_visit_date: date = Field(..., description="Scheduled visit date")
    
    @validator('next_visit_date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v

class StockItem(BaseModel):
    """Medicine/supply inventory item"""
    stock_id: str = Field(..., description="Unique stock item identifier")
    clinic_id: str = Field(..., description="Associated clinic ID")
    item_name: str = Field(..., description="Name of medicine/supply")
    on_hand_qty: int = Field(..., ge=0, description="Current quantity on hand")
    reorder_level: int = Field(..., ge=0, description="Minimum quantity before reorder")
    unit: str = Field(..., description="Unit of measurement (tablets, bottles, etc)")
    
    @property
    def is_low_stock(self) -> bool:
        """Check if item is below reorder threshold"""
        return self.on_hand_qty < self.reorder_level

class ReminderMessage(BaseModel):
    """SMS reminder message for patient"""
    patient_id: str = Field(..., description="Associated patient ID")
    lang_tag: Literal["[EN]", "[TSW]"] = Field(..., description="Language tag for message")
    text: str = Field(..., description="Message content")
    created_at: datetime = Field(default_factory=datetime.now, description="Message creation timestamp")
    
    @validator('lang_tag')
    def validate_lang_tag(cls, v):
        if v not in ["[EN]", "[TSW]"]:
            raise ValueError("lang_tag must be [EN] or [TSW]")
        return v

class DashboardData(BaseModel):
    """Aggregated dashboard view data"""
    upcoming_visits: List[Dict[str, Any]] = Field(default_factory=list)
    missed_visits: List[Dict[str, Any]] = Field(default_factory=list)
    low_stock_items: List[StockItem] = Field(default_factory=list)
    total_clinics: int = Field(0, ge=0)
    total_patients: int = Field(0, ge=0)
```

### Invariants (What must always be true)
1. **Valid Date Range**: `next_visit_date` must be a valid ISO date format (YYYY-MM-DD)
2. **Non-Negative Stock**: `on_hand_qty >= 0` and `reorder_level >= 0` for all stock items
3. **Low Stock Definition**: Item is low-stock if and only if `on_hand_qty < reorder_level`
4. **Phone Format**: All phone numbers must be in E.164 format with country code
5. **Language Consistency**: Language tags must match patient's preferred_lang setting
6. **Unique Identifiers**: All entity IDs (clinic_id, patient_id, etc.) must be unique within their type
7. **Referential Integrity**: Patient.clinic_id must reference an existing Clinic
8. **Message Queue Append-Only**: messages_outbox.csv is append-only, never truncated

### Protocols (Interfaces and Contracts)
```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class DataUploadProtocol(ABC):
    """Protocol for CSV data upload operations"""
    
    @abstractmethod
    def upload_clinics(self, csv_path: str) -> List[Clinic]:
        """Upload and validate clinic data from CSV"""
        pass
    
    @abstractmethod
    def upload_patients(self, csv_path: str) -> List[Patient]:
        """Upload and validate patient data from CSV"""
        pass
    
    @abstractmethod
    def upload_appointments(self, csv_path: str) -> List[Appointment]:
        """Upload and validate appointment data from CSV"""
        pass
    
    @abstractmethod
    def upload_stock(self, csv_path: str) -> List[StockItem]:
        """Upload and validate stock data from CSV"""
        pass

class DashboardProtocol(ABC):
    """Protocol for dashboard data operations"""
    
    @abstractmethod
    def get_upcoming_visits(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get appointments in next N days"""
        pass
    
    @abstractmethod
    def get_missed_visits(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get appointments missed in past N days"""
        pass
    
    @abstractmethod
    def get_low_stock_items(self) -> List[StockItem]:
        """Get all items below reorder threshold"""
        pass

class ReminderProtocol(ABC):
    """Protocol for SMS reminder operations"""
    
    @abstractmethod
    def generate_reminder(self, patient: Patient, appointment: Appointment) -> ReminderMessage:
        """Generate reminder message in patient's preferred language"""
        pass
    
    @abstractmethod
    def preview_reminders(self, patient_ids: List[str]) -> List[ReminderMessage]:
        """Preview messages without sending"""
        pass
    
    @abstractmethod
    def queue_reminders(self, messages: List[ReminderMessage]) -> str:
        """Queue messages to outbox CSV file"""
        pass

class StockProtocol(ABC):
    """Protocol for stock management operations"""
    
    @abstractmethod
    def check_stock_levels(self, clinic_id: Optional[str] = None) -> List[StockItem]:
        """Check current stock levels for clinic(s)"""
        pass
    
    @abstractmethod
    def generate_reorder_draft(self, low_items: List[StockItem]) -> str:
        """Generate reorder CSV for low stock items"""
        pass
```

### Examples (Concrete Usage)
```python
# Example 1: Successful CSV upload and validation
clinic_input = {
    "clinic_id": "CLN001",
    "name": "Gaborone Central Clinic",
    "district": "South-East"
}
expected_clinic = Clinic(**clinic_input)

# Example 2: Upcoming visit detection
appointment_input = {
    "appointment_id": "APT001",
    "patient_id": "PAT001",
    "clinic_id": "CLN001",
    "visit_type": "routine",
    "next_visit_date": (datetime.now() + timedelta(days=3)).date()
}
# Should appear in upcoming_visits dashboard card

# Example 3: Low stock alert
stock_input = {
    "stock_id": "STK001",
    "clinic_id": "CLN001",
    "item_name": "Paracetamol 500mg",
    "on_hand_qty": 50,
    "reorder_level": 100,
    "unit": "tablets"
}
# Should trigger low-stock alert (50 < 100)

# Example 4: Language-tagged SMS reminder
reminder_tsw = {
    "patient_id": "PAT001",
    "lang_tag": "[TSW]",
    "text": "[TSW] Gakologelwa: O na le bookelo kwa CLN001 ka 2024-03-15",
    "created_at": datetime.now()
}

# Example 5: Error handling - invalid phone format
error_patient = {
    "patient_id": "PAT002",
    "clinic_id": "CLN001",
    "first_name": "John",
    "last_name": "Doe",
    "phone_e164": "73123456",  # Missing + prefix
    "preferred_lang": "EN"
}
# Should raise ValidationError("Phone must be in E.164 format")
```

## No-Show Prediction & Smart Scheduling Extensions

### Enhanced IDKs (Important Domain Keywords)

11. **No-Show Risk Score**: Predictive percentage (0-100%) indicating likelihood of patient missing appointment
12. **Smart Overbooking**: Intelligent capacity management exceeding 100% based on predicted no-shows  
13. **Two-Way SMS**: Bidirectional SMS communication allowing patients to reschedule via reply codes
14. **Waitlist Priority**: Automated queue management with rules for urgent cases, distance, and chronic care
15. **Slot Recovery**: Process of filling cancelled appointments through waitlist activation
16. **Pattern Analytics**: Historical no-show analysis showing day-of-week, seasonal, and demographic trends
17. **Transport Mode**: Patient's method of reaching clinic (walking, combi, private vehicle) affecting risk
18. **Rainy Season Multiplier**: 1.4x increase in no-show rates during November-March in Botswana

### Enhanced TYPE Artifacts

#### No-Show Prediction Types
```python
from enum import Enum
from typing import Optional, List
import datetime

class RiskLevel(str, Enum):
    """Risk categorization for no-show prediction"""
    LOW = "LOW"      # 0-29%
    MEDIUM = "MEDIUM" # 30-59%  
    HIGH = "HIGH"    # 60-100%

class TransportMode(str, Enum):
    """Patient transport method to clinic"""
    WALKING = "WALKING"
    COMBI = "COMBI"          # Public minibus
    PRIVATE = "PRIVATE"       # Private vehicle
    UNKNOWN = "UNKNOWN"

class NoShowRisk(BaseModel):
    """Patient no-show risk assessment"""
    patient_id: str = Field(..., description="Associated patient identifier")
    appointment_id: str = Field(..., description="Associated appointment identifier")
    risk_score: float = Field(..., ge=0, le=100, description="Risk percentage 0-100")
    risk_level: RiskLevel = Field(..., description="Categorized risk level")
    calculated_at: datetime = Field(default_factory=datetime.now, description="Risk calculation timestamp")
    
    # Risk factors
    distance_km: Optional[float] = Field(None, ge=0, description="Distance from clinic in kilometers")
    previous_no_shows: int = Field(0, ge=0, description="Historical no-show count")
    age_group: str = Field(..., description="Age category (18-25, 26-40, 41-60, 60+)")
    day_of_week: str = Field(..., description="Appointment day (Monday, Tuesday, etc.)")
    transport_mode: TransportMode = Field(TransportMode.UNKNOWN, description="Transport method")
    is_rainy_season: bool = Field(False, description="Appointment during rainy season")
    
    @validator('risk_score', pre=True)
    def calculate_risk_level(cls, v, values):
        if v < 30:
            values['risk_level'] = RiskLevel.LOW
        elif v < 60:
            values['risk_level'] = RiskLevel.MEDIUM
        else:
            values['risk_level'] = RiskLevel.HIGH
        return v

class OverbookingRecommendation(BaseModel):
    """Smart overbooking suggestion for clinic capacity"""
    clinic_id: str = Field(..., description="Target clinic identifier")
    date: date = Field(..., description="Recommendation date")
    time_slot: str = Field(..., description="Time period (morning/afternoon)")
    recommended_capacity: float = Field(..., ge=100, le=125, description="Recommended booking percentage")
    current_capacity: float = Field(..., ge=0, description="Current booking level")
    expected_attendance: float = Field(..., ge=0, le=100, description="Predicted actual attendance rate")
    confidence_level: float = Field(..., ge=0, le=100, description="Recommendation confidence")
    
    # Factors influencing recommendation
    historical_no_show_rate: float = Field(..., ge=0, le=100, description="Historical no-show rate")
    day_of_week_factor: float = Field(..., description="Monday/Friday adjustment factor")
    weather_factor: float = Field(1.0, description="Rainy season multiplier")
    
    @validator('recommended_capacity')
    def validate_safe_overbooking(cls, v):
        if v > 125:
            raise ValueError("Overbooking must not exceed 125% for safety")
        return v

class WaitlistEntry(BaseModel):
    """Patient waitlist registration"""
    patient_id: str = Field(..., description="Patient identifier")
    clinic_id: str = Field(..., description="Target clinic")
    preferred_times: List[str] = Field(..., description="Preferred appointment times")
    priority_level: int = Field(..., ge=1, le=5, description="Priority (1=Urgent, 5=Routine)")
    medical_urgency: Optional[str] = Field(None, description="Medical urgency description")
    max_distance_km: Optional[float] = Field(None, description="Maximum acceptable distance")
    added_at: datetime = Field(default_factory=datetime.now, description="Waitlist registration time")
    
    # Priority factors
    is_chronic_care: bool = Field(False, description="Ongoing chronic condition")
    lives_within_5km: bool = Field(False, description="Lives within 5km of clinic")
    previous_no_shows: int = Field(0, ge=0, description="Historical no-show count")

class SlotRecovery(BaseModel):
    """Cancelled appointment slot recovery tracking"""
    original_appointment_id: str = Field(..., description="Cancelled appointment")
    clinic_id: str = Field(..., description="Clinic identifier")
    slot_datetime: datetime = Field(..., description="Available slot time")
    cancellation_reason: str = Field(..., description="Reason for cancellation")
    recovery_started_at: datetime = Field(default_factory=datetime.now, description="Recovery process start")
    recovery_completed_at: Optional[datetime] = Field(None, description="Recovery completion time")
    filled_by_patient_id: Optional[str] = Field(None, description="Patient who filled slot")
    recovery_successful: bool = Field(False, description="Whether slot was successfully filled")
    time_to_fill_hours: Optional[float] = Field(None, ge=0, description="Hours taken to fill slot")
```

#### Enhanced Protocols

```python
class PredictionProtocol(ABC):
    """Protocol for no-show prediction operations"""
    
    @abstractmethod
    def calculate_risk_score(self, patient_id: str, appointment_id: str) -> NoShowRisk:
        """Calculate no-show risk for specific appointment"""
        pass
    
    @abstractmethod
    def get_high_risk_appointments(self, clinic_id: str, date_range: tuple) -> List[NoShowRisk]:
        """Retrieve appointments with high no-show risk"""
        pass
    
    @abstractmethod
    def update_risk_factors(self, patient_id: str, factors: dict) -> NoShowRisk:
        """Update patient risk factors and recalculate"""
        pass

class OverbookingProtocol(ABC):
    """Protocol for smart overbooking operations"""
    
    @abstractmethod
    def get_overbooking_recommendation(self, clinic_id: str, date: date) -> OverbookingRecommendation:
        """Calculate optimal overbooking level"""
        pass
    
    @abstractmethod
    def validate_capacity_limits(self, clinic_id: str, proposed_capacity: float) -> bool:
        """Ensure overbooking stays within safe limits"""
        pass

class WaitlistProtocol(ABC):
    """Protocol for waitlist management operations"""
    
    @abstractmethod
    def add_to_waitlist(self, entry: WaitlistEntry) -> str:
        """Add patient to waitlist with priority"""
        pass
    
    @abstractmethod
    def fill_cancelled_slot(self, appointment_id: str) -> SlotRecovery:
        """Attempt to fill cancelled slot from waitlist"""
        pass
    
    @abstractmethod
    def get_prioritized_waitlist(self, clinic_id: str, slot_time: datetime) -> List[WaitlistEntry]:
        """Get waitlist ordered by priority for specific slot"""
        pass

class TwoWaySMSProtocol(ABC):
    """Protocol for bidirectional SMS communication"""
    
    @abstractmethod
    def send_reschedule_options(self, patient_id: str) -> str:
        """Send SMS with reschedule codes"""
        pass
    
    @abstractmethod
    def process_sms_response(self, phone_number: str, response_text: str) -> dict:
        """Process patient SMS response and take action"""
        pass
    
    @abstractmethod
    def confirm_reschedule(self, patient_id: str, new_appointment_id: str) -> str:
        """Send reschedule confirmation SMS"""
        pass
```

#### Enhanced Examples

```python
# Example 1: High-risk appointment identification
high_risk_patient = NoShowRisk(
    patient_id="PAT001",
    appointment_id="APT001", 
    risk_score=75.0,
    risk_level=RiskLevel.HIGH,
    distance_km=12.5,  # >5km threshold
    previous_no_shows=2,  # History of no-shows
    age_group="18-25",  # High-risk age group
    day_of_week="Monday",  # High no-show day
    transport_mode=TransportMode.COMBI,  # Unreliable transport
    is_rainy_season=True  # Additional risk factor
)

# Example 2: Smart overbooking recommendation
monday_recommendation = OverbookingRecommendation(
    clinic_id="CLN001",
    date=date(2024, 3, 18),  # Monday
    time_slot="afternoon",
    recommended_capacity=118.0,  # 18% overbooking
    current_capacity=115.0,
    expected_attendance=92.0,  # Accounting for no-shows
    confidence_level=85.0,
    historical_no_show_rate=38.0,  # Monday rate
    day_of_week_factor=1.18,
    weather_factor=1.0
)

# Example 3: Priority waitlist entry
urgent_waitlist = WaitlistEntry(
    patient_id="PAT002",
    clinic_id="CLN001", 
    preferred_times=["09:00", "10:00", "14:00"],
    priority_level=1,  # Urgent
    medical_urgency="Chest pain follow-up",
    max_distance_km=10.0,
    is_chronic_care=False,
    lives_within_5km=True,  # Priority factor
    previous_no_shows=0  # Reliable patient
)

# Example 4: Successful slot recovery
recovery_success = SlotRecovery(
    original_appointment_id="APT003",
    clinic_id="CLN001",
    slot_datetime=datetime(2024, 3, 15, 10, 0),
    cancellation_reason="Transport breakdown",
    filled_by_patient_id="PAT002",  # From waitlist
    recovery_successful=True,
    time_to_fill_hours=1.5  # Under 2-hour target
)
```

### Enhanced Invariants

9. **Risk Score Bounds**: `0 <= risk_score <= 100` for all NoShowRisk calculations
10. **Safe Overbooking**: `recommended_capacity <= 125` to prevent overwhelming clinic capacity
11. **Priority Ordering**: Waitlist entries must be sorted by priority_level (1=highest) then by added_at timestamp
12. **Recovery Time Tracking**: `time_to_fill_hours` calculated as `(recovery_completed_at - recovery_started_at).hours`
13. **Risk Factor Weights**: Distance (22%), Previous no-shows (28%), Day of week (15%), Age (12%), Other (23%)
14. **SMS Response Window**: Two-way SMS responses must be processed within 5 minutes
15. **Slot Recovery Target**: Aim for 65% success rate with <2 hours average fill time

## Implementation Notes
- **Frontend Framework**: React or Vue.js for responsive dashboard interface
- **Backend Framework**: FastAPI (Python) for REST API with automatic validation
- **Data Storage**: SQLite for local storage (offline-first), CSV files for import/export
- **Testing Framework**: Playwright for end-to-end testing (mandatory)
- **CSV Processing**: pandas for efficient data manipulation
- **Deployment**: Docker container for consistent deployment across environments
- **Performance Requirements**: Dashboard load < 2 seconds, CSV processing < 1 second per 1000 records, Risk prediction < 100ms
- **Security Considerations**: Input sanitization, secure file uploads, no PII in logs
- **Browser Support**: Chrome, Firefox, Edge (latest 2 versions)
- **Mobile Responsive**: Dashboard must work on tablets (minimum 768px width)

## Architectural Decisions for No-Show Prediction

### ADR-001: Prediction Engine Architecture
**Context**: Need to predict no-shows with <100ms latency for 1000+ patients
**Decision**: Hybrid ML/rule-based approach with caching
**Consequences**: 
- Fast predictions via cache (TTL=1 hour)
- Fallback to rules for small datasets (<500 records)
- Logistic regression for larger datasets
- Feature weights: distance(35%), history(25%), weather(20%), demographics(20%)

### ADR-002: Overbooking Strategy
**Context**: 28-42% baseline no-show rates require intelligent capacity management
**Decision**: Dynamic overbooking capped at 125% with day-specific adjustments
**Consequences**:
- Monday/Friday: 118% capacity
- Mid-week: 105-110% capacity
- Rainy season: 1.4x multiplier
- Emergency buffer: 2 slots always reserved

### ADR-003: SMS Gateway Integration
**Context**: Need two-way SMS for rescheduling with limited connectivity
**Decision**: Simulated Africa's Talking API with reply codes
**Consequences**:
- Reply "1" = reschedule tomorrow
- Reply "2" = reschedule next week
- 5-minute response window
- Queue-based processing for offline resilience

### ADR-004: Waitlist Prioritization
**Context**: Need fair, efficient slot recovery when appointments cancel
**Decision**: Weighted priority scoring system
**Consequences**:
- Medical urgency: 40% weight
- Wait time: 30% weight
- Reliability: 20% weight
- Distance: 10% weight
- Target 65% fill rate for cancelled slots

### ADR-005: Offline-First Data Sync
**Context**: Clinics have intermittent connectivity
**Decision**: IndexedDB with background sync queue
**Consequences**:
- All writes go to local first
- Sync queue for pending operations
- Conflict resolution: last-write-wins
- 7-day offline operation capability

## Context

### Beginning Context
- `/Users/addzmaestro/coding projects/Claude system/inputs/problem.md` - Problem statement
- `/Users/addzmaestro/coding projects/Claude system/specs/spec_template.md` - Specification template
- `/Users/addzmaestro/coding projects/Claude system/CLAUDE.md` - Project guidelines
- Empty workspace directories for agents to populate
- Playwright 1.38.0 installed via npm
- Python 3.8+ environment available

### Ending Context  
- `/Users/addzmaestro/coding projects/Claude system/workspace/backend/` - Complete API implementation
- `/Users/addzmaestro/coding projects/Claude system/workspace/frontend/` - Dashboard UI implementation
- `/Users/addzmaestro/coding projects/Claude system/workspace/data/` - Sample CSV files and outbox
- `/Users/addzmaestro/coding projects/Claude system/tests/e2e/` - Full Playwright test suite
- `/Users/addzmaestro/coding projects/Claude system/workspace/reports/test_results.xml` - Test execution report
- All tests passing (100% green)
- System deployed and accessible at http://localhost:3000

## Low-Level Tasks
> Ordered from start to finish. Each task maps 1:1 with a QA test.

### Task 1: Research Domain and Establish IDKs
```yaml
agent: Researcher
description: Investigate Botswana healthcare context and establish domain keywords
acceptance_criteria:
  - Document healthcare challenges in Botswana primary clinics
  - Identify key terminology and local considerations
  - Generate IDKs document with 10-12 domain keywords
test_mapping: test_research.py::test_idks_documented
dependencies: []
estimated_duration: 30 minutes

# Execution prompt
prompt: |
  Research the Botswana primary healthcare context for ClinicLite.
  Focus on: SMS communication patterns, language preferences (English/Setswana),
  stock management challenges, patient appointment compliance.
  Create workspace/research/summary.md and workspace/outputs/idks.md
```

### Task 2: Design System Architecture
```yaml
agent: Architect
description: Create system architecture following TYPE-driven principles
acceptance_criteria:
  - Complete architecture diagram
  - Define all system components and interactions
  - Specify data flow for offline-first operation
test_mapping: test_architecture.py::test_architecture_complete
dependencies: [Task 1]
estimated_duration: 45 minutes

# Execution prompt
prompt: |
  Design the ClinicLite system architecture based on PRIMARY_SPEC.md.
  Create workspace/outputs/architecture.md with:
  - Component diagram (Frontend, Backend, Data Storage)
  - Data flow for CSV upload -> Processing -> Dashboard
  - Offline-first synchronization strategy
  - API endpoint specifications matching the protocols
```

### Task 3: Define User Stories and Scenarios
```yaml
agent: ProductOwner
description: Create user stories and Gherkin scenarios for all features
acceptance_criteria:
  - User stories for each dashboard feature
  - Gherkin scenarios for happy path and edge cases
  - Acceptance criteria for each story
test_mapping: test_user_stories.py::test_stories_complete
dependencies: [Task 1, Task 2]
estimated_duration: 30 minutes

# Execution prompt
prompt: |
  Create user stories for ClinicLite in workspace/outputs/user_stories.md.
  Include stories for:
  - CSV upload (clinics, patients, appointments, stock)
  - Dashboard viewing (upcoming, missed, low stock)
  - SMS reminder generation with language toggle
  - Stock reorder draft creation
  Write Gherkin scenarios for each story.
```

### Task 4: Design Data Pipeline
```yaml
agent: DataEngineer
description: Implement CSV processing and data validation pipeline
acceptance_criteria:
  - CSV parser for all 4 entity types
  - Data validation with Pydantic models
  - Error handling for malformed data
test_mapping: test_data_pipeline.py::test_csv_processing
dependencies: [Task 2]
estimated_duration: 1 hour

# Execution prompt
prompt: |
  Implement CSV data pipeline in workspace/backend/data_pipeline.py.
  Create functions to:
  - Parse CSV files (clinics.csv, patients.csv, appointments.csv, stock.csv)
  - Validate data using Pydantic models from PRIMARY_SPEC.md
  - Handle errors gracefully with detailed error messages
  - Store validated data in SQLite database
  Include sample CSV files in workspace/data/samples/
```

### Task 5: Implement Backend API
```yaml
agent: BackendEngineer
description: Build FastAPI backend with all required endpoints
acceptance_criteria:
  - All endpoints from protocols implemented
  - Request/response validation
  - SQLite database integration
test_mapping: test_api.py::test_all_endpoints
dependencies: [Task 4]
estimated_duration: 2 hours

# Execution prompt
prompt: |
  Create FastAPI backend in workspace/backend/main.py.
  Implement endpoints:
  - POST /upload (handle 4 CSV types)
  - GET /dashboard (return upcoming/missed/low-stock)
  - POST /reminders/preview (generate messages with [EN]/[TSW] tags)
  - POST /reminders/queue (append to messages_outbox.csv)
  - POST /stock/reorder-draft (generate reorder_draft.csv)
  Use SQLite for storage, ensure offline-first design.
```

### Task 6: Build Frontend Dashboard
```yaml
agent: FrontendEngineer
description: Create responsive single-page dashboard interface
acceptance_criteria:
  - Upload interface for 4 CSV types
  - Dashboard cards for upcoming/missed/low-stock
  - SMS preview with language toggle
  - Reorder draft generation button
test_mapping: test_dashboard.py::test_ui_complete
dependencies: [Task 5]
estimated_duration: 2 hours

# Execution prompt
prompt: |
  Build dashboard UI in workspace/frontend/.
  Create single-page app with:
  - CSV upload area (drag-drop or browse for 4 file types)
  - Dashboard with 3 cards: Upcoming Visits, Missed Visits, Low Stock
  - SMS reminder interface with EN/TSW toggle and preview
  - Stock management with reorder button
  Use React or Vue.js, make it mobile-responsive (min 768px).
  Style with a clean, medical theme using blue/white colors.
```

### Task 7: Create Playwright Test Suite
```yaml
agent: QA
description: Develop comprehensive Playwright tests for all features
acceptance_criteria:
  - Tests for CSV upload flow
  - Tests for dashboard data display
  - Tests for SMS reminder generation
  - Tests for stock management
  - Edge case testing
test_mapping: test_e2e.py::test_complete_suite
dependencies: [Task 6]
estimated_duration: 2 hours

# Execution prompt
prompt: |
  Create Playwright tests in tests/e2e/.
  Test scenarios:
  - test_csv_upload.py: Upload all 4 CSV types
  - test_dashboard.py: Verify upcoming/missed/low-stock display
  - test_reminders.py: Test [EN]/[TSW] message generation
  - test_stock.py: Test reorder draft creation
  - test_edge_cases.py: Invalid data, missing fields, etc.
  Use ARIA selectors, add delays (100-500ms) for human-like interaction.
  Generate screenshots on failure to workspace/reports/screenshots/.
```

### Task 8: Fix Failing Tests
```yaml
agent: SelfHealing
description: Identify and fix any test failures
acceptance_criteria:
  - All tests passing (100% green)
  - No regression in existing functionality
  - Patches documented
test_mapping: test_e2e.py::test_all_passing
dependencies: [Task 7]
estimated_duration: 1 hour

# Execution prompt
prompt: |
  Run all Playwright tests and identify failures.
  For each failure:
  1. Analyze the error and root cause
  2. Generate fix in workspace/patches/
  3. Apply fix to source code
  4. Re-run tests to verify
  Maximum 5 attempts. Document all fixes in workspace/patches/fixes.md.
```

### Task 9: Prepare Release
```yaml
agent: DeliveryLead
description: Package system for deployment and create release documentation
acceptance_criteria:
  - Docker container ready
  - Deployment instructions complete
  - Release notes generated
test_mapping: test_deployment.py::test_release_ready
dependencies: [Task 8]
estimated_duration: 30 minutes

# Execution prompt
prompt: |
  Prepare ClinicLite for release:
  1. Create Dockerfile for the application
  2. Write deployment guide in workspace/reports/deployment.md
  3. Generate release notes in workspace/reports/release_notes.md
  4. Create executive summary in workspace/reports/status.md
  Ensure all documentation follows Context7 standards.
```

## Test Plan

### Unit Tests
- [ ] Test Clinic model validation
- [ ] Test Patient model with phone validation
- [ ] Test Appointment date parsing
- [ ] Test StockItem low-stock calculation
- [ ] Test ReminderMessage language tag validation
- [ ] Test CSV parser for each entity type
- [ ] Test data validation error handling

### Integration Tests
- [ ] Test CSV upload to database flow
- [ ] Test dashboard data aggregation
- [ ] Test reminder generation with correct language
- [ ] Test outbox CSV file writing
- [ ] Test reorder draft generation
- [ ] Test API endpoint integration

### End-to-End Tests (Playwright)
- [ ] Test complete CSV upload journey for all 4 types
- [ ] Test dashboard displays correct upcoming visits (next 7 days)
- [ ] Test dashboard displays correct missed visits (past 7 days)
- [ ] Test low-stock items appear when qty < reorder level
- [ ] Test SMS preview with [EN] and [TSW] tags
- [ ] Test reminder queue to messages_outbox.csv
- [ ] Test reorder draft CSV creation
- [ ] Test responsive design on tablet (768px)

### Edge Cases
- [ ] Empty CSV files: Should show appropriate error
- [ ] Malformed dates: Should reject with clear message
- [ ] Invalid phone numbers: Should validate E.164 format
- [ ] Duplicate IDs: Should prevent duplicates
- [ ] Missing required fields: Should show field-specific errors
- [ ] Network timeout: Should work offline with local storage
- [ ] Large CSV files (10,000+ rows): Should process within 10 seconds

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Poor internet connectivity | High | Medium | Offline-first architecture with local SQLite storage |
| CSV data quality issues | High | High | Robust validation with detailed error messages |
| Language translation errors | Medium | Medium | Use simple, clear message templates reviewed by native speakers |
| Browser compatibility | Low | Medium | Test on Chrome, Firefox, Edge; use standard web APIs |
| Large data volumes | Medium | Medium | Implement pagination and lazy loading for dashboard |
| Data loss | Low | High | Regular backups, append-only message queue |

## Success Metrics

- [ ] All tests passing (100% green)
- [ ] Code coverage > 80%
- [ ] Performance: Dashboard load < 2 seconds
- [ ] Performance: CSV processing < 1 second per 1000 records
- [ ] Security: No SQL injection vulnerabilities
- [ ] Security: Input sanitization on all user inputs
- [ ] Accessibility: WCAG 2.1 AA compliance
- [ ] Documentation: Complete API docs and user guide

## Notes

- Primary target: Botswana primary healthcare clinics
- Internet connectivity: Assume 256 kbps or less
- Languages: English (EN) and Setswana (TSW) are official languages
- SMS costs: Keep messages under 160 characters
- Data privacy: Follow Botswana Data Protection Act
- Testing: Playwright is mandatory per Context7 requirements
- Zero-error policy: No feature ships with failing tests
- Contact: TechLead agent for orchestration questions