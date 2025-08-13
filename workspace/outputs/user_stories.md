# ClinicLite No-Show Prediction & Smart Scheduling User Stories

**Project**: ClinicLite Botswana  
**Date**: August 12, 2025  
**Context**: Based on research showing 28-42% no-show rates in Botswana clinics  
**Goal**: Achieve 15% no-show reduction through intelligent prediction and scheduling

## Epic Overview

| Epic | Priority | Story Points | MVP Phase |
|------|----------|--------------|-----------|
| EPIC 1: No-Show Risk Prediction | P0 | 21 | Phase 1 |
| EPIC 2: Smart Overbooking | P1 | 13 | Phase 2 |
| EPIC 3: SMS Quick Reschedule | P0 | 16 | Phase 1 |
| EPIC 4: Waitlist Management | P1 | 18 | Phase 2 |
| **Total** | - | **68** | **2 Phases** |

---

## EPIC 1: No-Show Risk Prediction (P0 - MVP Phase 1)

### Story 1.1: Risk Score Calculation
**As a** clinic nurse  
**I want** to see each patient's no-show risk score  
**So that** I can proactively manage high-risk appointments

**Acceptance Criteria:**
- **Given** a patient has an upcoming appointment
- **When** I view the appointment list
- **Then** I should see a risk percentage (0-100%) next to each patient name
- **And** the risk should be color-coded:
  - Green: 0-29% (Low Risk)
  - Yellow: 30-59% (Medium Risk) 
  - Red: 60-100% (High Risk)
- **And** the calculation should consider:
  - Distance from clinic (>5km = higher risk)
  - Previous no-show history (exponential weight)
  - Patient age group (18-25 highest risk)
  - Day of week (Monday/Friday higher risk)
  - Transport mode if available

**Edge Cases:**
- New patients with no history show as "New Patient" with 35% baseline risk
- Missing distance data defaults to medium risk (45%)
- System works offline with last calculated scores

**Definition of Done:**
- Risk scores display in real-time
- Color coding is accessible (WCAG 2.1 AA compliant)
- Calculation is documented and auditable
- Works offline with cached data

**Story Points:** 8  
**Dependencies:** Patient history data, distance calculation

---

### Story 1.2: Pattern Dashboard  
**As a** clinic manager  
**I want** to see no-show patterns and trends  
**So that** I can make data-driven scheduling decisions

**Acceptance Criteria:**
- **Given** I have at least 3 months of appointment data
- **When** I access the analytics dashboard
- **Then** I should see:
  - Weekly no-show rate trend (line chart)
  - Day-of-week pattern (bar chart showing Monday=38%, Friday=35%, etc.)
  - Monthly overview with seasonal patterns
  - Top 5 high-risk patient demographics
  - Actionable insights (e.g., "Consider reducing Friday afternoon slots")

**Advanced Criteria:**
- **Given** weather data is available
- **When** viewing patterns
- **Then** rainy day impact should be highlighted (1.4x multiplier)

**Edge Cases:**
- With <50 appointments, show "Insufficient data for patterns"
- Handle data gaps gracefully
- Export patterns to CSV for reporting

**Definition of Done:**
- Dashboard loads in <3 seconds
- Charts are mobile-responsive
- Insights are actionable and specific
- Data export functionality works

**Story Points:** 13  
**Dependencies:** Historical appointment data, analytics engine

---

## EPIC 2: Smart Overbooking (P1 - MVP Phase 2)

### Story 2.1: Automatic Overbooking Recommendations
**As a** scheduler  
**I want** the system to suggest optimal overbooking levels  
**So that** I can maximize clinic utilization without overwhelming staff

**Acceptance Criteria:**
- **Given** I'm scheduling appointments for a specific day/time
- **When** I view the scheduling interface
- **Then** I should see recommended overbooking percentage:
  - Monday/Friday: 118% capacity
  - Tuesday-Thursday: 105-110% capacity
  - Rainy season: +5% additional
- **And** the system should show:
  - Current booking level (e.g., "Currently at 112% - within optimal range")
  - Risk level indicator (Green/Yellow/Red)
  - Expected actual attendance based on risk scores

**Safety Constraints:**
- Never recommend >125% overbooking
- Account for staff capacity and room availability
- Provide override capability with justification required

**Edge Cases:**
- New clinic with no history defaults to 105% conservative booking
- Staff shortage days reduce recommendations by 10%
- Holiday/special days use different algorithms

**Definition of Done:**
- Recommendations update in real-time
- Override mechanism works and logs reasons
- Historical accuracy of recommendations is tracked
- Clear visual indicators for booking levels

**Story Points:** 8  
**Dependencies:** Historical no-show data, clinic capacity configuration

---

### Story 2.2: Capacity Management Interface
**As a** clinic manager  
**I want** visual indicators and controls for daily capacity  
**So that** I can balance patient access with manageable workload

**Acceptance Criteria:**
- **Given** I'm viewing the daily schedule
- **When** appointments are booked above 100% capacity
- **Then** I should see:
  - Clear capacity meter (e.g., "115% - Optimal Overbook")
  - Color-coded status (Green: 100-110%, Yellow: 110-120%, Red: >120%)
  - Estimated actual attendance (e.g., "Expected: 95% based on risk scores")
  - Real-time adjustment controls

**Interactive Features:**
- **Given** I need to adjust capacity
- **When** I click "Reduce Risk" button
- **Then** system highlights high-risk appointments for potential rescheduling

**Edge Cases:**
- Emergency appointments override overbooking limits
- Staff call-outs trigger capacity warnings
- System suggests waitlist activations when capacity drops

**Definition of Done:**
- Visual indicators are intuitive and accessible
- Real-time updates work smoothly
- Adjustment recommendations are actionable
- Audit trail for capacity decisions

**Story Points:** 5  
**Dependencies:** Real-time schedule data, risk calculation system

---

## EPIC 3: SMS Quick Reschedule (P0 - MVP Phase 1)

### Story 3.1: Two-Way SMS Reschedule
**As a** patient  
**I want** to quickly reschedule my appointment via SMS  
**So that** I can avoid being a no-show when circumstances change

**Acceptance Criteria:**
- **Given** I receive an appointment reminder SMS
- **When** I reply with a reschedule code
- **Then** I should get immediate options:
  - Reply "1" for tomorrow same time
  - Reply "2" for next week same time  
  - Reply "3" for next available slot
  - Reply "CALL" to speak with clinic
- **And** I should receive confirmation within 5 minutes
- **And** the message should be in my preferred language (English/Setswana)

**Setswana Example:**
```
[TSW] Gakologelwa: Bookelo CLN001, 15 Phalane 10:00. 
Araba: 1=kamoso, 2=wiki e e tlang, 3=nako e e lebaleng, CALL=bua le sekolo
```

**Edge Cases:**
- Invalid responses get helpful error message
- No available slots triggers waitlist signup offer
- Multiple simultaneous reschedule attempts handled gracefully
- SMS delivery failures have email backup if available

**Definition of Done:**
- Two-way SMS works reliably
- Response time is <5 minutes
- Both languages supported accurately
- Clear error handling and user guidance

**Story Points:** 13  
**Dependencies:** SMS gateway integration, slot availability engine

---

### Story 3.2: Reminder Optimization
**As a** clinic administrator  
**I want** optimized reminder timing and content  
**So that** we achieve maximum patient response and attendance

**Acceptance Criteria:**
- **Given** a patient has an appointment
- **When** the reminder system activates
- **Then** it should send:
  - 48-hour advance reminder (primary)
  - Morning-of reminder 2 hours before appointment
  - Weather-aware messaging during rainy season
  - Transport time estimates based on patient location

**Message Content Requirements:**
- Clinic name and location
- Appointment date and time
- Doctor/nurse name if assigned
- Estimated travel time
- Reschedule options
- Confirmation request

**Optimization Features:**
- **Given** patient has history of morning appointments
- **When** sending reminders
- **Then** prioritize morning reminder timing
- **And** include relevant transport options

**Edge Cases:**
- SMS delivery failures trigger secondary contact methods
- Patients without phones get paper reminders
- Emergency appointments get immediate confirmation calls

**Definition of Done:**
- Timing optimization reduces no-shows by 15%
- Message templates are culturally appropriate
- Delivery tracking works accurately
- Fallback communication methods function

**Story Points:** 3  
**Dependencies:** Patient contact database, SMS gateway, weather API

---

## EPIC 4: Waitlist Management (P1 - MVP Phase 2)

### Story 4.1: Priority Queue System
**As a** clinic nurse  
**I want** automatic waitlist management with priority rules  
**So that** cancelled appointments are filled efficiently and fairly

**Acceptance Criteria:**
- **Given** an appointment is cancelled or a no-show occurs
- **When** I activate the waitlist
- **Then** the system should automatically:
  - Identify eligible waitlist patients for that time slot
  - Apply priority rules:
    1. Urgent medical conditions (Priority 1)
    2. Patients living <5km from clinic (Priority 2) 
    3. Chronic care follow-ups (Priority 3)
    4. First-come-first-served within same priority
  - Send SMS to top 3 candidates simultaneously
  - Book first confirmed response

**Priority Logic:**
- **Given** multiple patients respond to waitlist SMS
- **When** processing responses
- **Then** highest priority patient gets the slot
- **And** others are notified of next available options

**Edge Cases:**
- All waitlist patients decline - escalate to walk-in management
- Multiple urgent cases - use medical triage protocols
- System failure - manual override capability available

**Definition of Done:**
- Priority rules are configurable by clinic
- Response handling is automatic and accurate
- Clear audit trail for waitlist decisions
- Manual override works when needed

**Story Points:** 10  
**Dependencies:** Patient prioritization system, SMS gateway, slot management

---

### Story 4.2: Slot Recovery System
**As a** clinic scheduler  
**I want** automatic recovery of cancelled appointment slots  
**So that** we maintain high clinic utilization and patient access

**Acceptance Criteria:**
- **Given** an appointment is cancelled or no-show occurs
- **When** the slot becomes available
- **Then** the system should:
  - Immediately activate waitlist for that time slot
  - Track recovery success rate (target: 65%)
  - Measure time-to-fill (target: <2 hours)
  - Update utilization metrics in real-time

**Recovery Process:**
1. **Immediate (0-15 minutes):** SMS to waitlist priority 1-3 patients
2. **Quick (15-60 minutes):** Expand to priority 4-5 patients  
3. **Extended (1-2 hours):** Open to any waitlist patient
4. **Same-day (2+ hours):** Convert to walk-in capacity

**Metrics Tracking:**
- **Given** slot recovery is attempted
- **When** outcome is determined
- **Then** system should log:
  - Recovery success/failure
  - Time to fill slot
  - Patient priority level who filled slot
  - Original reason for cancellation

**Edge Cases:**
- Last-minute cancellations (<2 hours) use expedited process
- High-demand time slots get additional waitlist priority
- Recurring appointment cancellations trigger proactive outreach

**Definition of Done:**
- 65% slot recovery rate achieved
- Average fill time <2 hours
- Comprehensive metrics dashboard
- Automated escalation process works

**Story Points:** 8  
**Dependencies:** Waitlist system, metrics tracking, notification system

---

## Cross-Cutting User Stories

### Story X.1: Offline-First Architecture
**As a** clinic staff member  
**I want** the prediction and scheduling system to work offline  
**So that** internet outages don't disrupt patient care

**Acceptance Criteria:**
- **Given** internet connection is lost
- **When** I use the scheduling system
- **Then** I should be able to:
  - View cached risk scores and recommendations
  - Add patients to waitlist offline
  - Queue SMS reminders for sending when online
  - Access last 7 days of appointment data

**Sync Requirements:**
- **Given** internet connection is restored
- **When** system syncs
- **Then** it should:
  - Upload queued SMS messages
  - Sync appointment changes bidirectionally
  - Update risk calculations with latest data
  - Resolve conflicts with timestamp-based rules

**Definition of Done:**
- Core functionality works without internet
- Sync process is reliable and conflict-free
- Clear offline/online status indicators
- No data loss during offline periods

**Story Points:** 8  
**Dependencies:** Offline storage, sync engine, conflict resolution

---

### Story X.2: Integration with Existing ClinicLite
**As a** system administrator  
**I want** seamless integration with current CSV upload system  
**So that** existing workflows are enhanced, not disrupted

**Acceptance Criteria:**
- **Given** clinic uploads patient/appointment CSV files
- **When** data is processed
- **Then** risk calculations should automatically update
- **And** existing dashboard should show enhanced data
- **And** current SMS reminder system should use new optimization

**Integration Points:**
- CSV upload triggers risk score recalculation
- Existing appointment views show risk indicators
- Current stock management unaffected
- SMS outbox enhanced with reschedule capabilities

**Migration Strategy:**
- **Given** clinic has existing data
- **When** new features are enabled
- **Then** historical data should be analyzed for patterns
- **And** gradual rollout should preserve existing functionality

**Definition of Done:**
- Zero disruption to existing workflows
- Enhanced features are opt-in initially
- Data migration is complete and verified
- Staff training materials updated

**Story Points:** 5  
**Dependencies:** Existing ClinicLite system, data migration tools

---

## Success Metrics & Acceptance

### Primary Success Criteria
- **No-show rate reduction:** 15% minimum within 3 months
- **SMS response rate:** >40% for reschedule requests  
- **Slot recovery rate:** >65% for cancelled appointments
- **Prediction accuracy:** >70% for high-risk identification
- **User adoption:** 80% of clinic staff actively using risk scores

### Secondary Success Criteria
- **Patient satisfaction:** <20 minute average wait time maintained
- **Staff efficiency:** 25% reduction in scheduling-related overtime
- **Revenue recovery:** BWP 8,000-12,000 monthly per clinic
- **System performance:** <3 second dashboard load time maintained

### Compliance Requirements
- **Data privacy:** Full compliance with Botswana Data Protection Act
- **Accessibility:** WCAG 2.1 AA compliance for all interfaces
- **Language support:** Accurate Setswana translations validated by native speakers
- **Offline capability:** Core functions work without internet

---

## Definition of Ready (DoR)
Before any story enters development:
- [ ] Acceptance criteria are clear and testable
- [ ] UI/UX mockups completed where applicable
- [ ] Dependencies identified and resolved
- [ ] Technical approach agreed upon
- [ ] Test scenarios defined
- [ ] Setswana translations reviewed

## Definition of Done (DoD)
Before any story is considered complete:
- [ ] All acceptance criteria met
- [ ] Unit tests written and passing
- [ ] Playwright e2e tests passing
- [ ] Code reviewed and approved
- [ ] Accessibility tested
- [ ] Performance requirements met
- [ ] Documentation updated
- [ ] Manual testing by clinic staff completed

---

*Document prepared by ProductOwner agent following Context7 principles*  
*Last updated: August 12, 2025*