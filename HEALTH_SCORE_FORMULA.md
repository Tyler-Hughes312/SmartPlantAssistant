# Plant Health Score Formula

## Overview

The Plant Health Score is a comprehensive metric (0-100) that evaluates the overall health of a plant based on sensor readings and recent trends.

## Formula Breakdown

### Total Health Score = Moisture Score + Temperature Score + Light Score + Trend Score

**Maximum Possible Score: 100 points**

---

## 1. Moisture Score (0-30 points)

Evaluates soil moisture levels based on optimal ranges for most plants.

| Moisture Range | Points | Status |
|----------------|--------|--------|
| 40-70% | 30 | Optimal |
| 30-40% or 70-80% | 20 | Good |
| 20-30% or 80-90% | 10 | Fair |
| <20% or >90% | 0 | Poor |

**Reasoning**: Most plants thrive in soil moisture between 40-70%. Below 30% risks dehydration, above 80% risks root rot.

---

## 2. Temperature Score (0-25 points)

Evaluates ambient temperature based on optimal growing conditions.

| Temperature Range (°F) | Points | Status |
|------------------------|--------|--------|
| 65-80°F | 25 | Optimal |
| 60-65°F or 80-85°F | 18 | Good |
| 55-60°F or 85-90°F | 10 | Fair |
| <55°F or >90°F | 0 | Poor |

**Reasoning**: Most common houseplants and garden vegetables thrive in the 65-80°F range. Extreme temperatures stress plants.

---

## 3. Light Score (0-25 points)

Evaluates ambient light levels (lux) based on typical plant needs.

| Light Range (lux) | Points | Status |
|-------------------|--------|--------|
| 300-800 lux | 25 | Optimal |
| 200-300 lux or 800-1000 lux | 18 | Good |
| 100-200 lux or 1000-1500 lux | 10 | Fair |
| <100 lux or >1500 lux | 0 | Poor |

**Reasoning**: 
- 300-800 lux: Ideal for most indoor plants (indirect bright light)
- <100 lux: Too dim, insufficient for photosynthesis
- >1500 lux: Potentially too intense, may cause stress

---

## 4. Trend Score (0-20 points)

Evaluates the stability and direction of recent sensor readings.

### Calculation Method:

1. **Analyze Last 5 Readings**: Compare each reading with the previous one
2. **Moisture Trend**: 
   - Declining moisture is negative (plant needs water)
   - Average change rate calculated: `(current - previous) / time`
   - Rapid decline (< -5% per reading): -10 points
   - Moderate decline (< -2% per reading): -5 points
3. **Temperature Stability**:
   - Calculate average temperature variation
   - Stable temperatures = better health
   - High variation (>5°F average): -5 points

### Scoring:
- **Base Score**: 20 points
- **Moisture decline penalty**: Up to -10 points
- **Temperature instability penalty**: Up to -5 points
- **Final Trend Score**: `max(0, 20 - penalties)`

**Reasoning**: Healthy plants show stable or improving conditions. Rapid declines indicate stress or immediate needs.

---

## Health Status Categories

Based on total score:

| Score Range | Status | Meaning |
|------------|--------|---------|
| 80-100 | Excellent | All conditions optimal, plant is thriving |
| 65-79 | Good | Minor improvements possible but plant is healthy |
| 50-64 | Fair | Some conditions need attention |
| 30-49 | Poor | Multiple factors need immediate attention |
| 0-29 | Critical | Plant is in distress, urgent action needed |

---

## Example Calculation

### Sample Reading:
- **Moisture**: 55%
- **Temperature**: 72°F
- **Light**: 450 lux
- **Recent Trend**: Stable conditions, minimal changes

### Calculation:
1. **Moisture Score**: 55% is in 40-70% range → **30 points**
2. **Temperature Score**: 72°F is in 65-80°F range → **25 points**
3. **Light Score**: 450 lux is in 300-800 lux range → **25 points**
4. **Trend Score**: Stable, no penalties → **20 points**

### **Total Score: 30 + 25 + 25 + 20 = 100 (Excellent)**

---

## Implementation Notes

- The formula analyzes the **most recent reading** for current conditions
- The **last 5 readings** are used for trend analysis
- If fewer than 5 readings exist, available readings are used
- If no readings exist, a default score of 50 is returned with "Unknown" status
- Scores are rounded to 1 decimal place for display
- The formula is designed to be conservative - lower scores indicate real issues

## Customization

For plant-specific health scores, optimal ranges can be adjusted:
- **Succulents**: Prefer lower moisture (30-50%)
- **Tropical plants**: Prefer higher temperatures (70-85°F)
- **Shade plants**: Prefer lower light (200-500 lux)
- **Full sun plants**: Tolerate higher light (1000+ lux)

These adjustments would require modifying the threshold values in the `calculate_plant_health_score()` function in `backend/app.py`.

