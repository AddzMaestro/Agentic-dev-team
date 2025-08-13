# TYPE Specification: No-Show Prediction System

## Overview
This specification defines the TYPE-driven architecture for the Intelligent No-Show Prediction & Smart Scheduling System, extending ClinicLite with predictive capabilities.

## Core Types

### Risk Assessment Types

```typescript
// Base risk score with invariants
type RiskScore = {
  value: number;              // Invariant: 0 <= value <= 100
  category: RiskCategory;     // Invariant: Derived from value
  factors: RiskFactor[];      // Invariant: Sum of weights = 1.0
  confidence: number;         // Invariant: 0 <= confidence <= 1
  calculated_at: timestamp;   // Invariant: UTC timezone
  model_version: string;      // Invariant: Semantic versioning
}

// Risk categories with thresholds
type RiskCategory = 
  | "Low"      // 0-30
  | "Medium"   // 31-60
  | "High"     // 61-80
  | "VeryHigh" // 81-100

// Individual risk factors
type RiskFactor = {
  name: RiskFactorName;
  weight: number;            // Invariant: 0 <= weight <= 1
  raw_value: number | string;
  normalized_value: number;  // Invariant: 0 <= normalized <= 1
  contribution: number;      // Invariant: weight * normalized_value
}

type RiskFactorName = 
  | "previous_no_shows"
  | "distance_km"
  | "season_factor"
  | "day_of_week"
  | "age_group"
  | "appointment_type"
  | "chronic_condition"
  | "phone_availability"
  | "language_preference"
  | "transport_access"
```

### Patient Profile Types

```typescript
type PatientRiskProfile = {
  patient_id: PatientId;
  base_risk: number;           // Historical average
  current_risk: RiskScore;
  risk_history: RiskScore[];   // Last 10 calculations
  no_show_count: number;
  total_appointments: number;
  attendance_rate: number;     // Invariant: 0 <= rate <= 1
  last_updated: timestamp;
}

type PatientId = string;       // Format: "P" + 5 digits

type PatientPreferences = {
  language: "en" | "tn";       // English or Tswana
  sms_enabled: boolean;
  reminder_time: "morning" | "evening" | "both";
  transport_needed: boolean;
  preferred_days: DayOfWeek[];
  preferred_times: TimeSlot[];
}
```

### Appointment Types

```typescript
type AppointmentWithRisk = {
  appointment_id: AppointmentId;
  patient_id: PatientId;
  clinic_id: ClinicId;
  scheduled_time: timestamp;
  appointment_type: AppointmentType;
  risk_score: RiskScore;
  interventions: Intervention[];
  overbooked: boolean;
  overbook_percentage: number;  // 0, 5, 10, 15, or 20
  status: AppointmentStatus;
  outcome?: AppointmentOutcome;
}

type AppointmentStatus = 
  | "scheduled"
  | "confirmed"
  | "reminded"
  | "attended"
  | "no_show"
  | "cancelled"
  | "rescheduled"

type AppointmentOutcome = {
  actual_attendance: boolean;
  arrival_time?: timestamp;
  no_show_reason?: NoShowReason;
  prediction_accuracy: number;  // Invariant: 0 <= accuracy <= 1
}

type NoShowReason = 
  | "transport"
  | "work"
  | "forgot"
  | "weather"
  | "illness"
  | "family_emergency"
  | "other"
  | "unknown"
```

### Intervention Types

```typescript
type Intervention = {
  id: InterventionId;
  type: InterventionType;
  target: PatientId;
  appointment_id: AppointmentId;
  scheduled_at: timestamp;
  executed_at?: timestamp;
  status: InterventionStatus;
  details: InterventionDetails;
  outcome?: InterventionOutcome;
}

type InterventionType = 
  | "sms_reminder"
  | "phone_call"
  | "transport_voucher"
  | "family_notification"
  | "overbook_slot"
  | "waitlist_activate"

type InterventionStatus = 
  | "pending"
  | "in_progress"
  | "completed"
  | "failed"
  | "cancelled"

type InterventionDetails = 
  | SmsDetails
  | PhoneCallDetails
  | TransportDetails
  | OverbookDetails
  | WaitlistDetails

type SmsDetails = {
  message_template: string;
  language: "en" | "tn";
  phone_number: string;
  delivery_status?: "sent" | "delivered" | "failed";
  response?: string;
}

type InterventionOutcome = {
  effective: boolean;
  patient_response?: string;
  attendance_impact?: "positive" | "negative" | "neutral";
  cost: number;              // In BWP
}
```

### Scheduling Types

```typescript
type SmartSchedule = {
  date: DateString;           // Format: "YYYY-MM-DD"
  clinic_id: ClinicId;
  total_slots: number;
  appointments: AppointmentWithRisk[];
  overbooked_slots: TimeSlot[];
  buffer_slots: TimeSlot[];
  utilization_forecast: number;  // Invariant: 0 <= forecast <= 1.2
  expected_attendance: number;
  recommended_actions: SchedulingAction[];
}

type SchedulingAction = {
  action_type: "overbook" | "add_buffer" | "activate_waitlist" | "send_reminders";
  target_slots: TimeSlot[];
  priority: "urgent" | "high" | "medium" | "low";
  reason: string;
}

type TimeSlot = {
  start_time: TimeString;    // Format: "HH:MM"
  end_time: TimeString;
  capacity: number;
  booked: number;
  overbook_limit: number;
}
```

### Waitlist Types

```typescript
type WaitlistEntry = {
  entry_id: WaitlistId;
  patient_id: PatientId;
  requested_dates: DateString[];
  urgency: "emergency" | "urgent" | "routine";
  added_at: timestamp;
  expires_at: timestamp;
  priority_score: number;     // Calculated based on urgency + wait time
  notification_sent: boolean;
  response_window: number;    // Hours to respond
  status: WaitlistStatus;
}

type WaitlistStatus = 
  | "waiting"
  | "notified"
  | "accepted"
  | "declined"
  | "expired"
  | "scheduled"

type WaitlistQueue = {
  clinic_id: ClinicId;
  entries: WaitlistEntry[];
  auto_fill_enabled: boolean;
  max_response_time: number;  // Hours
  fill_strategy: "priority" | "fifo" | "urgent_first";
}
```

### Analytics Types

```typescript
type PredictionMetrics = {
  date_range: DateRange;
  total_predictions: number;
  accuracy: number;           // Overall accuracy
  precision: number;          // True positive rate
  recall: number;             // Sensitivity
  f1_score: number;
  false_positive_rate: number;
  false_negative_rate: number;
  risk_category_accuracy: Record<RiskCategory, number>;
}

type InterventionMetrics = {
  intervention_type: InterventionType;
  total_count: number;
  success_rate: number;
  cost_per_intervention: number;
  attendance_improvement: number;  // Percentage points
  roi: number;                     // Return on investment
}

type ClinicMetrics = {
  clinic_id: ClinicId;
  period: DateRange;
  baseline_no_show_rate: number;
  current_no_show_rate: number;
  improvement: number;            // Percentage points
  slots_saved: number;
  revenue_impact: number;         // In BWP
  patient_satisfaction: number;   // 1-5 scale
}
```

### Model Types

```typescript
type PredictionModel = {
  model_id: ModelId;
  version: SemanticVersion;    // Format: "major.minor.patch"
  algorithm: "logistic_regression" | "random_forest" | "gradient_boost";
  features: FeatureDefinition[];
  weights: ModelWeights;
  training_metrics: PredictionMetrics;
  training_date: timestamp;
  training_samples: number;
  validation_score: number;
  deployment_status: "testing" | "shadow" | "active" | "retired";
}

type FeatureDefinition = {
  name: string;
  type: "numeric" | "categorical" | "boolean";
  normalization: "minmax" | "zscore" | "none";
  importance: number;          // Feature importance score
  missing_strategy: "mean" | "median" | "mode" | "zero";
}

type ModelWeights = {
  feature_weights: Record<string, number>;
  intercept: number;
  threshold: number;
}
```

## Invariants

### Risk Score Invariants
1. **Value Range**: `0 <= risk_score.value <= 100`
2. **Category Mapping**: Category must match value ranges exactly
3. **Factor Weights**: Sum of all factor weights must equal 1.0
4. **Confidence Range**: `0 <= confidence <= 1`
5. **Temporal Ordering**: `calculated_at` must be after patient registration

### Scheduling Invariants
1. **Capacity Limits**: `booked <= capacity + overbook_limit`
2. **Overbook Percentage**: Only 0%, 5%, 10%, 15%, or 20% allowed
3. **Buffer Slots**: At least 15 minutes every 2 hours
4. **Utilization**: Cannot exceed 120% (20% max overbook)
5. **Time Ordering**: Appointments must not overlap unless overbooked

### Intervention Invariants
1. **Idempotency**: Same intervention cannot be executed twice
2. **Time Constraints**: SMS sent 3 days, 1 day, and morning of appointment
3. **Language Matching**: Intervention language must match patient preference
4. **Cost Tracking**: All interventions must have associated cost
5. **Response Window**: Waitlist responses valid for max 4 hours

### Data Invariants
1. **Patient ID Format**: Must match pattern "P[0-9]{5}"
2. **Clinic ID Format**: Must match pattern "C[0-9]{3}"
3. **Date Format**: All dates in ISO 8601 format
4. **Phone Numbers**: Must be valid Botswana format (+267...)
5. **Historical Limit**: Keep maximum 90 days of history

## Validation Rules

### Risk Score Validation
```typescript
function validateRiskScore(score: RiskScore): ValidationResult {
  const errors: string[] = [];
  
  if (score.value < 0 || score.value > 100) {
    errors.push("Risk value out of range");
  }
  
  const expectedCategory = getRiskCategory(score.value);
  if (score.category !== expectedCategory) {
    errors.push("Category mismatch for value");
  }
  
  const weightSum = score.factors.reduce((sum, f) => sum + f.weight, 0);
  if (Math.abs(weightSum - 1.0) > 0.001) {
    errors.push("Factor weights do not sum to 1.0");
  }
  
  return { valid: errors.length === 0, errors };
}
```

### Appointment Validation
```typescript
function validateAppointment(apt: AppointmentWithRisk): ValidationResult {
  const errors: string[] = [];
  
  if (apt.overbooked && ![5, 10, 15, 20].includes(apt.overbook_percentage)) {
    errors.push("Invalid overbook percentage");
  }
  
  if (apt.risk_score.value > 60 && apt.interventions.length === 0) {
    errors.push("High-risk appointment missing interventions");
  }
  
  if (apt.scheduled_time < Date.now()) {
    errors.push("Cannot schedule appointment in the past");
  }
  
  return { valid: errors.length === 0, errors };
}
```

## Error Handling

### Error Types
```typescript
type PredictionError = 
  | "MODEL_NOT_LOADED"
  | "INVALID_PATIENT_DATA"
  | "MISSING_FEATURES"
  | "CALCULATION_TIMEOUT"
  | "OFFLINE_SYNC_FAILED"

type InterventionError = 
  | "SMS_GATEWAY_DOWN"
  | "INVALID_PHONE_NUMBER"
  | "LANGUAGE_NOT_SUPPORTED"
  | "QUEUE_FULL"
  | "DUPLICATE_INTERVENTION"

type SchedulingError = 
  | "CAPACITY_EXCEEDED"
  | "INVALID_TIME_SLOT"
  | "CONFLICT_DETECTED"
  | "BUFFER_VIOLATION"
  | "OVERBOOK_LIMIT_REACHED"
```

### Error Recovery
1. **Offline Fallback**: Use cached model if server unavailable
2. **Queue Persistence**: Store failed SMS in IndexedDB for retry
3. **Graceful Degradation**: Show last known risk if calculation fails
4. **Audit Logging**: Record all errors with context
5. **User Notification**: Clear error messages in preferred language

## Testing Requirements

### Unit Test Coverage
- All TYPE validations must have tests
- Invariant violations must be caught
- Edge cases for each risk factor
- Model version compatibility

### Integration Tests
- CSV import with risk data
- Offline/online transitions
- SMS queue processing
- Waitlist operations
- Concurrent updates

### Playwright E2E Tests
- Risk dashboard interactions
- SMS reminder workflow
- Overbooking scenarios
- Waitlist notifications
- Analytics visualizations

## Performance Constraints

### Latency Requirements
- Risk calculation: < 100ms
- Batch processing: < 20ms per patient
- Dashboard load: < 2 seconds
- SMS queue: < 500ms per message
- Model update: < 5 seconds

### Resource Limits
- IndexedDB: 5MB per clinic
- Memory: 100MB for model
- CPU: Single-threaded JS
- Network: 2G minimum
- Battery: Optimize for mobile