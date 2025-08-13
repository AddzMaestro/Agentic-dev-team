# Important Domain Keywords (IDKs) - Updated for No-Show Prediction

## Core ClinicLite IDKs (Existing)
1. **Offline-first** - Primary operation mode without internet
2. **CSV Upload** - Bulk data import mechanism
3. **Low Bandwidth** - Optimized for 2G/3G networks
4. **SMS Reminder (Simulated)** - Text message notifications
5. **Missed Visit** - Past appointments not attended
6. **Upcoming Visit** - Future scheduled appointments
7. **Low-Stock Threshold** - Inventory alert trigger
8. **Reorder Draft** - Automated supply requisition
9. **Language Toggle (EN/TSW)** - English/Setswana switching
10. **Clinic Dashboard** - Main interface view

## No-Show Prediction IDKs (New)
11. **No-Show Risk Score** - Numerical probability (0-100) of patient missing appointment
12. **Smart Overbooking** - Intelligent double-booking based on risk scores
13. **Waitlist Auto-fill** - Automatic patient substitution from queue
14. **SMS Quick Reschedule** - One-click appointment change via text
15. **Pattern Recognition** - ML-based behavior analysis
16. **Distance Factor** - Geographic accessibility weighting
17. **Weather Impact** - Seasonal/rainfall correlation
18. **Historical Attendance** - Past appointment compliance rate
19. **Prediction Confidence** - Model certainty percentage
20. **Buffer Slot** - Flexible time allocation for overbooking

## Integration IDKs (New)
21. **Risk Category** - Low/Medium/High/Very High classification
22. **Transport Voucher** - Financial assistance flag
23. **Family Reminder** - Secondary contact notification
24. **Clinic Utilization** - Appointment slot efficiency
25. **Reschedule Window** - Time limit for changes
26. **Auto-confirm** - Automated appointment validation
27. **No-Show Reason** - Categorized absence justification
28. **Intervention Protocol** - Action plan per risk level
29. **Fill Rate** - Waitlist success percentage
30. **Time Slot Preference** - Patient scheduling optimization

## Technical IDKs (New)
31. **IndexedDB Cache** - Local prediction storage
32. **Batch Prediction** - Bulk risk calculation
33. **Model Versioning** - Algorithm iteration tracking
34. **Fallback Logic** - Offline prediction mode
35. **Sync Queue** - Pending prediction updates
36. **Risk Threshold** - Configurable trigger points
37. **Prediction Lag** - Calculation time metric
38. **Model Accuracy** - Performance measurement
39. **Feature Vector** - Input parameters array
40. **Training Dataset** - Historical learning data

## Context7 Compliance
All IDKs are:
- TYPE-defined in specs
- Validated at runtime
- Documented with invariants
- Tested via Playwright
- Context-mapped to agents