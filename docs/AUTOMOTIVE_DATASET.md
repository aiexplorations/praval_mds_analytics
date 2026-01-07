# Automotive Press Manufacturing Dataset

## Overview

This dataset represents **90 days of production data** from an automotive body panel stamping facility with 2 press lines, 3 part families, comprehensive die management, and full material traceability.

**Key Statistics:**
- **Total Parts Produced:** 4,320 (2,160 per line)
- **Press Lines:** 2 (800T and 1200T capacity)
- **Part Families:** 3 (Door Outer Left, Door Outer Right, Bonnet Outer)
- **Dies Tracked:** 4 (with condition assessments and changeover events)
- **Material Coils:** 126 (from 3 suppliers)
- **Time Period:** 90 days of continuous production
- **Overall Pass Rate:** 96.3%
- **Overall OEE:** 82.5%

---

## Press Line Configuration

### Press Line A: Door Outer Panel Manufacturing
**Specifications:**
- **Press Capacity:** 800 tons
- **Line ID:** LINE_A
- **Database:** `postgres-press-line-a` (port 5436)
- **Part Families Produced:**
  - Door_Outer_Left (50% of production)
  - Door_Outer_Right (50% of production)

**Process Parameters:**
- **Tonnage Range:** 600-650T (75-81% of capacity)
- **Cycle Time:** 1.2-1.5 seconds
- **Stroke Rate:** 45-50 strokes per minute (SPM)
- **Material Grade:** CRS SPCC (Cold Rolled Steel, Standard Commercial)
- **Coil Thickness:** 0.7mm nominal

**Performance Metrics:**
- **Pass Rate:** 97.06%
- **OEE:** 85.8% (Availability: 93.1%, Performance: 91.0%, Quality: 98.3%)
- **Cost per Part:** $1.20 (material: $0.80, labor: $0.25, energy: $0.15)
- **Production Rate:** 24 parts/day average

**Dies Used:**
- **DIE_DOL_Rev3** - Door Outer Left (3rd revision, 185,420 strokes, 74% lifecycle)
- **DIE_DOR_Rev2** - Door Outer Right (2nd revision, 156,890 strokes, 63% lifecycle)

---

### Press Line B: Bonnet Outer Panel Manufacturing
**Specifications:**
- **Press Capacity:** 1200 tons
- **Line ID:** LINE_B
- **Database:** `postgres-press-line-b` (port 5437)
- **Part Family Produced:**
  - Bonnet_Outer (100% of production)

**Process Parameters:**
- **Tonnage Range:** 900-1100T (75-92% of capacity)
- **Cycle Time:** 3-5 seconds (deep draw complexity)
- **Stroke Rate:** 12-20 strokes per minute (SPM)
- **Material Grades:**
  - HSLA 350 (High-Strength Low-Alloy, 70.6% of production)
  - DP600 (Dual-Phase Steel, 29.4% of production)
- **Coil Thickness:** 0.9mm nominal

**Performance Metrics:**
- **Pass Rate:** 95.00%
- **OEE:** 79.1% (Availability: 89.0%, Performance: 86.0%, Quality: 97.2%)
- **Cost per Part:** $1.82 (material: $1.35, labor: $0.28, energy: $0.19)
- **Production Rate:** 24 parts/day average

**Dies Used:**
- **DIE_BO_Rev5** - Bonnet Outer (5th revision, 210,340 strokes, 84% lifecycle)
- **DIE_BO_Rev4** - Bonnet Outer backup (4th revision, 98,760 strokes, 39% lifecycle)

---

## Part Family Specifications

### Door_Outer_Left
**Geometry:**
- **Part Type:** Door panel
- **Overall Length:** 1,250mm ± 2mm
- **Draw Depth:** 85mm ± 1.5mm
- **Flange Width:** 15mm ± 0.5mm
- **Hinge Hole Diameter:** 10mm ± 0.1mm

**Quality Characteristics:**
- **First Pass Yield:** 96.48%
- **Dominant Defect:** Springback (15 occurrences in 90 days)
- **Defect Types:** springback, surface_scratch, burr, piercing_burst, dimensional
- **Severity Distribution:** Minor 65%, Moderate 25%, Major 8%, Critical 2%

**Material:**
- **Grade:** CRS SPCC
- **Supplier:** JSW Steel (primary), SAIL Steel (backup)
- **Coil Count:** 27 coils consumed over 90 days

**Root Cause Notes:**
- Higher springback defects compared to Door_Outer_Right suggest die calibration drift on DIE_DOL_Rev3
- Recommended action: Inspect draw bead wear, recalibrate die

---

### Door_Outer_Right
**Geometry:**
- **Part Type:** Door panel (mirror of Left)
- **Overall Length:** 1,250mm ± 2mm
- **Draw Depth:** 85mm ± 1.5mm
- **Flange Width:** 15mm ± 0.5mm
- **Hinge Hole Diameter:** 10mm ± 0.1mm

**Quality Characteristics:**
- **First Pass Yield:** 97.59%
- **Dominant Defect:** Springback (9 occurrences - 40% fewer than Left)
- **Defect Types:** springback, surface_scratch, burr, piercing_burst, dimensional
- **Severity Distribution:** Minor 70%, Moderate 20%, Major 8%, Critical 2%

**Material:**
- **Grade:** CRS SPCC
- **Supplier:** JSW Steel (primary), SAIL Steel (backup)
- **Coil Count:** 27 coils consumed over 90 days

**Performance:**
- 28% fewer defects than Door_Outer_Left
- Better die condition (DIE_DOR_Rev2 vs Rev3)

---

### Bonnet_Outer
**Geometry:**
- **Part Type:** Bonnet (hood) panel
- **Overall Length:** 1,450mm ± 2mm
- **Draw Depth (Apex):** 120mm ± 2mm (deeper than doors)
- **Surface Profile Deviation:** ±0.5mm (tight tolerance for aesthetics)
- **Hinge Bracket Position:** 200mm ± 1mm from edge

**Quality Characteristics:**
- **First Pass Yield:** 94.76%
- **Dominant Defects:** splitting_rupture (deep draw failure), necking, mouse_ears
- **Defect Types:** splitting_rupture, necking, mouse_ears, springback, wrinkling
- **Severity Distribution:** Minor 55%, Moderate 30%, Major 12%, Critical 3%

**Material:**
- **Primary Grade:** HSLA 350 (70.6% of production)
  - Higher yield strength for structural integrity
  - 49 coils from NIPPON Steel, SAIL Steel
- **Secondary Grade:** DP600 (29.4% of production)
  - Dual-phase steel for energy absorption
  - 23 coils from NIPPON Steel

**Process Challenges:**
- Complex deep-draw geometry increases defect rate vs doors (5.42% vs 2.5-3.5%)
- Material thinning at apex requires careful blank holder force control
- HSLA material less forgiving than CRS (higher springback risk)

---

## Die Management System

**Database:** `postgres-die-management` (port 5438)

### Die Master Registry
**4 Active Dies:**

| Die ID | Part Family | Tonnage Rating | Current Strokes | Lifecycle % | Health Status |
|--------|-------------|----------------|-----------------|-------------|---------------|
| DIE_DOL_Rev3 | Door_Outer_Left | 800T | 185,420 | 74% | Needs Calibration |
| DIE_DOR_Rev2 | Door_Outer_Right | 800T | 156,890 | 63% | Good |
| DIE_BO_Rev5 | Bonnet_Outer | 1200T | 210,340 | 84% | Wear Detected |
| DIE_BO_Rev4 | Bonnet_Outer | 1200T | 98,760 | 39% | Good (Backup) |

**Service Life:** Each die rated for 250,000 strokes before major overhaul

### Die Changeover Events
**Total Changeovers:** 272 events over 90 days
- **Press Line A:** 270 changeovers (alternating Left/Right dies every 8 hours)
- **Press Line B:** 2 changeovers (Rev5 primary, Rev4 backup during maintenance)

**SMED (Single-Minute Exchange of Die) Performance:**
- **Average Changeover Time:** 32.36 minutes (target: 30 minutes)
- **First Pass Success Rate:** 92.22% (successful startup after changeover)
- **Fastest Changeover:** 18 minutes
- **Slowest Changeover:** 52 minutes (hydraulic issue)

### Die Condition Assessments
**Frequency:** Daily assessments for active dies (283 total assessments)

**Tracked Metrics:**
- **Tonnage Drift:** Deviation from nominal tonnage (indicates wear)
- **Defect Rate Trend:** Correlation between die usage and defects
- **Dimensional Drift:** Part dimension changes over die lifecycle
- **Remaining Useful Life (RUL):** Predictive estimate of strokes remaining

**Example Findings:**
- DIE_DOL_Rev3: Tonnage drift +3.2% over last 30 days → calibration needed
- DIE_BO_Rev5: Defect rate increased from 4.2% to 5.8% → wear on draw beads

---

## Material Traceability System

**Database:** `postgres-warehouse` (marts schema: warehouse.staging_marts.material_coils, supplier_master)

### Material Coils
**Total Coils:** 126 coils consumed over 90 days

**Breakdown by Material Grade:**
- **CRS SPCC:** 54 coils (for Door parts)
- **HSLA 350:** 49 coils (for Bonnet, primary)
- **DP600:** 23 coils (for Bonnet, secondary)

**Coil Lifecycle:**
- **Received Date:** Timestamp of coil arrival at warehouse
- **Mounted Date:** Timestamp when coil loaded onto press
- **Parts Produced per Coil:** ~34 parts average (varies by part size)
- **Scrap Count:** Offcut and rejected parts from coil

**Certification Data (per coil):**
- **Yield Strength:** Material property from mill certificate
- **Tensile Strength:** Ultimate strength before fracture
- **Elongation %:** Ductility measure
- **Thickness Actual:** Measured vs nominal (tolerance ±0.05mm)

### Supplier Quality Scorecards
**3 Suppliers:**

| Supplier | Material Grades | Coils Supplied | Avg Defect Rate | Quality Score |
|----------|----------------|----------------|-----------------|---------------|
| JSW Steel | CRS SPCC | 54 | 3.24% | Excellent |
| NIPPON Steel | HSLA 350, DP600 | 20 | 5.76% | Good |
| SAIL Steel | CRS SPCC, HSLA 350 | 52 | 5.77% | Good |

**Quality Issues:**
- **SAIL HSLA Lot (Day 60):** Insufficient yield strength → splitting defects increased
- **JSW Coil Batch (Week 3):** Surface oxide → surface_scratch defects
- **NIPPON DP600 (Week 8):** Thickness variation → wrinkling issues

**Traceability:**
- Every part linked to source coil via `coil_id`
- Defect root cause analysis can trace back to supplier lot
- Enables supplier corrective action requests (SCAR)

---

## Quality Metrics by Part Family

### Defect Type Distribution

**Door_Outer_Left:**
1. Springback: 15 occurrences (41.7%)
2. Surface Scratch: 8 occurrences (22.2%)
3. Burr: 5 occurrences (13.9%)
4. Piercing Burst: 4 occurrences (11.1%)
5. Dimensional: 4 occurrences (11.1%)

**Door_Outer_Right:**
1. Springback: 9 occurrences (34.6%)
2. Surface Scratch: 6 occurrences (23.1%)
3. Burr: 4 occurrences (15.4%)
4. Piercing Burst: 4 occurrences (15.4%)
5. Dimensional: 3 occurrences (11.5%)

**Bonnet_Outer:**
1. Splitting/Rupture: 38 occurrences (32.5%)
2. Necking: 28 occurrences (23.9%)
3. Mouse Ears: 22 occurrences (18.8%)
4. Springback: 18 occurrences (15.4%)
5. Wrinkling: 11 occurrences (9.4%)

### Statistical Process Control (SPC)

**OEE Breakdown by Part Family:**

| Part Family | OEE | Availability | Performance | Quality Rate |
|-------------|-----|--------------|-------------|--------------|
| Door_Outer_Left | 85.7% | 93.0% | 90.9% | 98.4% |
| Door_Outer_Right | 85.9% | 93.2% | 91.1% | 98.3% |
| Bonnet_Outer | 79.1% | 89.0% | 86.0% | 97.2% |

**Key Observations:**
- Bonnet lower OEE due to complex geometry (deep draw)
- Door parts have higher availability (simpler die changeovers)
- Quality rate high across all parts (>97%)

### Cost Analysis by Part Family

| Part Family | Avg Cost/Part | Material % | Labor % | Energy % |
|-------------|---------------|------------|---------|----------|
| Door_Outer_Left | $1.20 | 66.7% | 20.8% | 12.5% |
| Door_Outer_Right | $1.20 | 66.7% | 20.8% | 12.5% |
| Bonnet_Outer | $1.82 | 74.2% | 15.4% | 10.4% |

**Cost Drivers:**
- Bonnet higher cost due to advanced materials (HSLA, DP600 vs CRS)
- Bonnet larger part → more material consumption
- Door parts more labor-intensive (frequent die changeovers)

---

## Data Freshness & Availability

**Data Sources:**
- **Press Line A Production:** Real-time updates every part cycle (~1.35s)
- **Press Line B Production:** Real-time updates every part cycle (~3.97s)
- **Die Changeovers:** Logged at completion (every 8 hours for Line A)
- **Die Condition Assessments:** Daily at shift end
- **Material Coil Data:** Updated on receipt and mount events

**Historical Retention:**
- **Production Data:** 90 days retained in source databases
- **Die History:** Full lifecycle retained (multi-year)
- **Material Certificates:** Retained per regulatory requirements (7 years)

**Data Warehouse Refresh:**
- **dbt Transformation:** Scheduled via Airflow (daily at 2 AM)
- **Cube.js Pre-Aggregations:** Auto-refresh on query or scheduled (configurable)

---

## Analytical Use Cases

### 1. Quality Root Cause Analysis
**Question:** "Why does Door_Outer_Left have 40% more springback defects than Door_Outer_Right?"

**Data Journey:**
- Query `PressOperations` cube filtered by `partFamily` = Door_Outer_Left/Right, `defectType` = springback
- Compare defect counts → Left: 15, Right: 9
- Investigate die condition: DIE_DOL_Rev3 (Left) has +3.2% tonnage drift vs DIE_DOR_Rev2 (Right)
- Root cause: Die calibration drift on Rev3
- Action: Schedule die recalibration

### 2. Material Supplier Impact
**Question:** "Which supplier has the best quality record for HSLA material?"

**Data Journey:**
- Query `material_coils` joined with `supplier_master`
- Filter by `material_grade` = HSLA_350
- Aggregate defect rate by supplier
- Result: NIPPON Steel 5.76% defect rate, SAIL Steel 5.77% (nearly identical)
- Insight: Both suppliers meet quality standards, choose based on cost/delivery

### 3. Press Line Utilization
**Question:** "What's the weekend vs weekday production efficiency?"

**Data Journey:**
- Query `PressLineUtilization` cube
- Compare `weekendParts` vs `weekdayParts`, `weekendProductionPct`
- Result: Weekend production 28.9% of total, similar OEE
- Insight: Weekend shifts as productive as weekday (skilled operators on all shifts)

### 4. Die Maintenance Optimization
**Question:** "When should DIE_BO_Rev5 be scheduled for maintenance?"

**Data Journey:**
- Query `die_condition_assessments` for DIE_BO_Rev5
- Check `remaining_useful_life_strokes` → 39,660 strokes remaining (16% RUL)
- Check defect rate trend → increasing from 4.2% to 5.8%
- Recommendation: Schedule maintenance within next 2 weeks (before RUL < 10%)

### 5. Shift Performance Comparison
**Question:** "Which shift has the best quality performance?"

**Data Journey:**
- Query `PressOperations` cube aggregated by `shiftId`
- Compare `passRate` across morning/afternoon/night shifts
- Result: Morning 96.8%, Afternoon 96.5%, Night 95.4%
- Insight: Night shift slightly lower (operator fatigue? lighting? investigate)

---

## Data Model Architecture

```
┌─────────────────────┐
│  Source Databases   │
│  (PostgreSQL)       │
├─────────────────────┤
│ • press_line_a      │──┐
│ • press_line_b      │──┤
│ • die_management    │──┼──► Foreign Data Wrappers (FDW)
│ • (warehouse marts) │──┘         ↓
└─────────────────────┘      ┌──────────────────┐
                             │  Data Warehouse  │
                             │  (PostgreSQL)    │
                             ├──────────────────┤
                             │ • raw schema     │ ← FDW foreign tables
                             │ • staging schema │ ← dbt staging models
                             │ • marts schema   │ ← dbt mart models
                             └──────────────────┘
                                      ↓
                             ┌──────────────────┐
                             │     Cube.js      │
                             │  Metrics Layer   │
                             ├──────────────────┤
                             │ • PressOperations│
                             │ • PartFamilyPerf │
                             │ • PressLineUtil  │
                             └──────────────────┘
                                      ↓
                             ┌──────────────────┐
                             │  Praval Agents   │
                             │  (5 Specialists) │
                             ├──────────────────┤
                             │ • Mfg Advisor    │
                             │ • Analytics Spec │
                             │ • Viz Specialist │
                             │ • Quality Insp   │
                             │ • Report Writer  │
                             └──────────────────┘
                                      ↓
                             ┌──────────────────┐
                             │  Frontend UI     │
                             │  (Next.js)       │
                             └──────────────────┘
```

---

## Example Queries

### Natural Language Queries (via Praval Agents):
- "What's the OEE for each press line?"
- "Show me defect trends for Door_Outer_Left over the last 30 days"
- "Compare springback defects between door parts"
- "Which material supplier has the best quality?"
- "What's the shift performance for Line A?"
- "Show me the die changeover frequency"
- "What's the cost breakdown by part family?"
- "Are there any quality anomalies I should know about?"

### SQL Queries (Direct Access):
```sql
-- Part family performance summary
SELECT
    part_family,
    total_parts_produced,
    first_pass_yield,
    avg_oee,
    avg_cost_per_part
FROM staging_marts.agg_part_family_performance
ORDER BY first_pass_yield DESC;

-- Die condition assessment (latest)
SELECT
    die_id,
    assessment_date,
    overall_health_score,
    remaining_useful_life_strokes,
    recommended_action
FROM die_condition_assessments
WHERE assessment_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY overall_health_score ASC;

-- Material coil traceability
SELECT
    mc.coil_id,
    sm.supplier_name,
    mc.material_grade,
    mc.parts_produced,
    mc.scrap_count,
    mc.coil_defect_rate
FROM staging_marts.material_coils mc
JOIN supplier_master sm ON mc.supplier_id = sm.supplier_id
WHERE mc.material_grade = 'HSLA_350'
ORDER BY mc.coil_defect_rate ASC;
```

---

## Conclusion

This automotive dataset provides comprehensive insights into press manufacturing operations with:
- **Production Detail:** 4,320 parts across 90 days with full process parameters
- **Die Lifecycle:** Complete changeover history and condition assessments
- **Material Genealogy:** Full traceability from coil to part with supplier quality data
- **Quality Analytics:** Part-family-specific defect patterns with root cause analysis

The dataset is designed for **AI-driven analytics**, enabling natural language queries via Praval agents that understand manufacturing terminology and provide actionable insights.
