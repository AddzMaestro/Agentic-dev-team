# User Stories: No-Show Prediction & Smart Scheduling System

## Epic: Reduce clinic no-shows by 15% through intelligent prediction and intervention

### Priority 0 (Core Features)

#### US-001: Risk Score Calculation
**As a** clinic nurse  
**I want** to see no-show risk scores for all daily appointments  
**So that** I can prioritize interventions for high-risk patients  

**Priority:** P0  
**Risk Category:** Technical  
**Effort:** L  
**Offline:** Required  

#### US-002: Risk Visualization Dashboard
**As a** clinic administrator  
**I want** a color-coded dashboard showing appointment risks  
**So that** I can quickly identify problem appointments  

**Priority:** P0  
**Risk Category:** User  
**Effort:** M  
**Offline:** Required  

#### US-003: Bulk SMS Reminders
**As a** clinic receptionist  
**I want** to send SMS reminders to high-risk patients  
**So that** I can reduce no-shows proactively  

**Priority:** P0  
**Risk Category:** Business  
**Effort:** M  
**Offline:** Queue for later  

### Priority 1 (Smart Scheduling)

#### US-004: Intelligent Overbooking
**As a** appointment scheduler  
**I want** the system to suggest overbooking for high-risk slots  
**So that** clinic utilization remains high despite no-shows  

**Priority:** P1  
**Risk Category:** Business  
**Effort:** L  
**Offline:** Required  

#### US-005: Language Toggle for SMS
**As a** Setswana-speaking patient  
**I want** to receive SMS reminders in my preferred language  
**So that** I clearly understand my appointment details  

**Priority:** P1  
**Risk Category:** User  
**Effort:** S  
**Offline:** N/A  

#### US-006: Quick Reschedule via SMS
**As a** patient who cannot attend  
**I want** to reschedule by replying to the SMS reminder  
**So that** I can easily change my appointment without calling  

**Priority:** P1  
**Risk Category:** Technical  
**Effort:** L  
**Offline:** Queue for sync  

### Priority 2 (Waitlist Management)

#### US-007: Automated Waitlist
**As a** clinic manager  
**I want** cancelled slots to auto-fill from a waitlist  
**So that** no appointment slots are wasted  

**Priority:** P2  
**Risk Category:** Business  
**Effort:** M  
**Offline:** Local processing  

#### US-008: Waitlist Notifications
**As a** waitlisted patient  
**I want** immediate SMS notification when a slot opens  
**So that** I can quickly confirm my availability  

**Priority:** P2  
**Risk Category:** Technical  
**Effort:** M  
**Offline:** Queue for later  

#### US-009: Transport Assistance Flag
**As a** rural patient living >20km away  
**I want** to see if I qualify for transport assistance  
**So that** distance doesn't prevent my attendance  

**Priority:** P2  
**Risk Category:** User  
**Effort:** S  
**Offline:** Required  

### Priority 3 (Analytics & Learning)

#### US-010: Prediction Accuracy Tracking
**As a** health system administrator  
**I want** to monitor the accuracy of no-show predictions  
**So that** I can validate the system's effectiveness  

**Priority:** P3  
**Risk Category:** Business  
**Effort:** M  
**Offline:** Store locally, sync later  

#### US-011: Intervention Effectiveness Report
**As a** clinic director  
**I want** reports showing which interventions work best  
**So that** I can optimize our reminder strategies  

**Priority:** P3  
**Risk Category:** Business  
**Effort:** L  
**Offline:** Generate from local data  

#### US-012: Cost Savings Calculator
**As a** financial officer  
**I want** to see the monetary impact of reduced no-shows  
**So that** I can justify the system investment  

**Priority:** P3  
**Risk Category:** Business  
**Effort:** S  
**Offline:** Required  

### System Stories

#### US-013: Offline Risk Calculation
**As a** system  
**I want** to calculate risk scores without internet connection  
**So that** predictions work during network outages  

**Priority:** P0  
**Risk Category:** Technical  
**Effort:** L  
**Offline:** Core requirement  

#### US-014: Pattern Learning
**As a** system  
**I want** to learn from actual attendance outcomes  
**So that** predictions improve over time  

**Priority:** P2  
**Risk Category:** Technical  
**Effort:** XL  
**Offline:** Store feedback locally  

#### US-015: CSV Data Import
**As a** system  
**I want** to import historical no-show data from CSV  
**So that** initial predictions have baseline data  

**Priority:** P0  
**Risk Category:** Technical  
**Effort:** M  
**Offline:** Required  

## Story Point Summary
- P0 Stories: 4 (Total: 16 points)
- P1 Stories: 3 (Total: 10 points)
- P2 Stories: 3 (Total: 9 points)
- P3 Stories: 3 (Total: 6 points)
- System Stories: 3 (Total: 11 points)

**Total: 52 story points**

## Implementation Sequence
1. Sprint 1: US-001, US-002, US-013, US-015 (Core prediction)
2. Sprint 2: US-003, US-004, US-005 (Basic interventions)
3. Sprint 3: US-006, US-007, US-008 (Waitlist & reschedule)
4. Sprint 4: US-009, US-010, US-011, US-014 (Enhancement & learning)
5. Sprint 5: US-012, Testing, Polish (Delivery)