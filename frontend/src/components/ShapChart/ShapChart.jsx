/**
 * ShapChart Component
 * ====================
 * Renders a horizontal bar chart of SHAP feature importance values.
 * Shows which features are pushing the model toward or away from predicting churn.
 *
 * PROPS:
 *   shapValues — array from the API:
 *     [
 *       { feature: "days_since_last_game", label: "Days since last game", shap_value: 0.42, direction: "increases_churn" },
 *       { feature: "games_7d",             label: "Games (7 days)",       shap_value: -0.18, direction: "decreases_churn" },
 *       ...
 *     ]
 *
 * WHY RECHARTS?
 * --------------
 * Recharts is the most "React-native" charting library — you build charts
 * with JSX components rather than imperative D3 code.
 * It's declarative, easy to customize, and works well with React state.
 *
 * WHAT TO BUILD:
 * ---------------
 * A horizontal BarChart where:
 *   - Y-axis = feature labels (the human-readable names)
 *   - X-axis = SHAP values (negative = decreases churn, positive = increases churn)
 *   - Bars colored by direction:
 *       increases_churn  → red   (#e05c5c)
 *       decreases_churn  → green (#5cb85c)
 *   - Reference line at x=0
 *   - Show top 8 features maximum (most impactful)
 *
 * RECHARTS QUICK REFERENCE:
 * --------------------------
 * import { BarChart, Bar, XAxis, YAxis, Tooltip, ReferenceLine, Cell, ResponsiveContainer } from 'recharts'
 *
 * <ResponsiveContainer width="100%" height={300}>
 *   <BarChart data={data} layout="vertical">
 *     <XAxis type="number" />
 *     <YAxis type="category" dataKey="label" width={200} />
 *     <Tooltip />
 *     <ReferenceLine x={0} stroke="#666" />
 *     <Bar dataKey="shap_value">
 *       {data.map((entry, i) => (
 *         <Cell key={i} fill={entry.direction === 'increases_churn' ? '#e05c5c' : '#5cb85c'} />
 *       ))}
 *     </Bar>
 *   </BarChart>
 * </ResponsiveContainer>
 *
 * LEARN MORE: https://recharts.org/en-US/api
 *
 * TODO: Implement this component.
 * Steps:
 *   1. Import the Recharts components you need
 *   2. Slice the top 8 features: shapValues.slice(0, 8)
 *   3. Render the BarChart as described above
 *   4. Add a title: "What's Driving This Prediction?"
 *   5. Add a small legend explaining red = increases risk, green = decreases risk
 */

import './ShapChart.css'

function ShapChart({ shapValues }) {
  if (!shapValues || shapValues.length === 0) {
    return <p className="shap-empty">No SHAP data available.</p>
  }

  // Top 8 most impactful features (already sorted by the API)
  const topFeatures = shapValues.slice(0, 8)

  return (
    <div className="shap-chart">
      <h3>What's Driving This Prediction?</h3>
      {/*
        TODO: Replace this placeholder with a Recharts BarChart.
        The data is `topFeatures` — each item has label, shap_value, direction.
      */}
      <p>TODO: Render the SHAP bar chart using Recharts</p>
    </div>
  )
}

export default ShapChart
