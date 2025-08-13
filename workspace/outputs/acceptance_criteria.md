# Acceptance Criteria: No-Show Prediction System

## US-001: Risk Score Calculation

### AC-001.1: Basic Risk Calculation
```gherkin
Given a patient with 2 previous no-shows out of 8 appointments
And the patient lives 25km from the clinic
And current season is rainy season
When the risk score is calculated
Then the risk score should be between 55-65
And the risk category should be "Medium"
```

### AC-001.2: Offline Calculation
```gherkin
Given the application is in offline mode
When a new appointment is created
Then the risk score is calculated using local data
And the score is stored in IndexedDB
And no network request is made
```

### AC-001.3: Real-time Updates
```gherkin
Given a patient's risk score is displayed as 45 (Medium)
When the patient confirms attendance via SMS
Then the risk score updates to 30 (Low)
And the dashboard reflects the change within 2 seconds
```

## US-002: Risk Visualization Dashboard

### AC-002.1: Color Coding
```gherkin
Given the dashboard displays today's appointments
When risk scores are calculated
Then appointments with score 0-30 show green
And appointments with score 31-60 show yellow
And appointments with score 61-80 show orange
And appointments with score 81-100 show red
```

### AC-002.2: Sorting and Filtering
```gherkin
Given 20 appointments are displayed
When the user clicks "Sort by Risk"
Then appointments are ordered from highest to lowest risk
And the top 5 high-risk patients are highlighted
```

### AC-002.3: Drill-down Details
```gherkin
Given a high-risk appointment is displayed
When the user clicks on the appointment
Then a modal shows risk factors breakdown
And displays previous no-show history
And shows recommended interventions
```

## US-003: Bulk SMS Reminders

### AC-003.1: Selective Sending
```gherkin
Given 15 appointments for tomorrow
And 5 are high-risk, 7 medium-risk, 3 low-risk
When the user clicks "Send SMS Reminders"
Then only high and medium-risk patients receive SMS
And 12 messages are queued for sending
```

### AC-003.2: Language Selection
```gherkin
Given a patient's preferred language is Setswana
When an SMS reminder is generated
Then the message content is in Setswana
And includes appointment date, time, and clinic name
And includes a reschedule instruction
```

### AC-003.3: Delivery Tracking
```gherkin
Given 10 SMS reminders were sent
When checking delivery status after 5 minutes
Then the dashboard shows delivery confirmations
And failed deliveries are marked for retry
And staff can trigger manual phone calls for failures
```

## US-004: Intelligent Overbooking

### AC-004.1: Automatic Suggestions
```gherkin
Given tomorrow's schedule has 3 high-risk appointments
When viewing the appointment calendar
Then system suggests 10% overbooking for those slots
And shows potential waitlist patients
And calculates expected actual attendance
```

### AC-004.2: Conflict Resolution
```gherkin
Given an overbooked slot has both patients arrive
When checking in patients
Then system provides conflict resolution options
And suggests next available slot
And tracks this as a "good problem" metric
```

### AC-004.3: Buffer Management
```gherkin
Given overbooking is enabled at 15%
When scheduling appointments
Then 15-minute buffers are added every 2 hours
And lunch breaks remain protected
And closing time is not exceeded
```

## US-006: Quick Reschedule via SMS

### AC-006.1: SMS Reply Parsing
```gherkin
Given a patient receives an SMS reminder
When they reply "CHANGE" or "BADLA"
Then system recognizes reschedule request
And sends available slots for next 3 days
And waits for slot selection
```

### AC-006.2: Confirmation Flow
```gherkin
Given a patient selects a new slot via SMS
When the selection is processed
Then original appointment is cancelled
And new appointment is confirmed
And confirmation SMS is sent in preferred language
```

## US-007: Automated Waitlist

### AC-007.1: Priority Scoring
```gherkin
Given 5 patients on the waitlist
When a slot becomes available
Then patients are scored by urgency and availability
And the highest priority patient is notified first
And they have 2 hours to respond
```

### AC-007.2: Auto-fill Process
```gherkin
Given a high-risk patient doesn't show
When 15 minutes past appointment time
Then system checks waitlist
And sends SMS to top waitlist patient
And updates schedule if accepted
```

## US-013: Offline Risk Calculation

### AC-013.1: Local Model Storage
```gherkin
Given the prediction model is loaded
When internet connection is lost
Then risk calculations continue using cached model
And IndexedDB stores all predictions
And accuracy is within 5% of online predictions
```

### AC-013.2: Sync on Reconnect
```gherkin
Given 50 risk scores calculated offline
When internet connection is restored
Then all scores sync to server
And any model updates are downloaded
And local cache is refreshed
```

## US-014: Pattern Learning

### AC-014.1: Outcome Tracking
```gherkin
Given predictions were made for 100 appointments
When actual attendance is recorded
Then system compares predictions to outcomes
And updates model weights accordingly
And stores learning metrics
```

### AC-014.2: Continuous Improvement
```gherkin
Given the model has 3 months of outcome data
When recalculating model accuracy
Then accuracy should improve by at least 5%
And false positive rate should decrease
And high-risk predictions should be more precise
```

## Edge Cases

### EC-001: Network Interruption
```gherkin
Given SMS reminders are being sent
When network connection drops mid-batch
Then sent messages are tracked
And unsent messages remain queued
And system retries when connection restored
```

### EC-002: Data Conflicts
```gherkin
Given a patient record is updated offline on two devices
When both sync to server
Then conflict resolution preserves both updates
And audit log tracks all changes
And staff is notified of conflicts
```

### EC-003: Maximum Capacity
```gherkin
Given clinic capacity is 50 patients per day
When overbooking would exceed safe capacity
Then system prevents additional overbooking
And suggests redistributing to other days
And maintains safety thresholds
```

## Performance Criteria

### PC-001: Response Time
```gherkin
Given 1000 patient records in the system
When calculating risk scores for daily appointments
Then all scores calculate within 1 second
And dashboard renders within 2 seconds
And no UI freezing occurs
```

### PC-002: Batch Processing
```gherkin
Given 200 SMS reminders to send
When processing the batch
Then all messages queue within 5 seconds
And delivery attempts complete within 30 minutes
And system remains responsive during processing
```