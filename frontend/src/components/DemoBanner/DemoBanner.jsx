/**
 * DemoBanner
 * Shown at the top of the page whenever demo mode is active.
 * Makes it unmistakably clear the user is looking at synthetic data.
 */
export default function DemoBanner({ onExit }) {
  return (
    <div className="demo-banner">
      <div className="demo-banner__content">
        <span className="demo-banner__icon">⚠</span>
        <span className="demo-banner__text">
          <strong>Demo Mode</strong> — All data is synthetically generated.
          Predictions, player profiles, and chat responses do not reflect real players.
        </span>
      </div>
      <button className="demo-banner__exit" onClick={onExit}>
        Exit Demo
      </button>
    </div>
  );
}
