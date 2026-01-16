import { useMemo } from "react";

interface MeasurementHistogramProps {
  counts: Record<string, number>;
  samples: string[];
  shots: number;
}

const LABELS: { key: string; color: string; name: string }[] = [
  { key: "plus", color: "#22c55e", name: "+" },
  { key: "minus", color: "#ef4444", name: "-" }
];

export function MeasurementHistogram({ counts, samples, shots }: MeasurementHistogramProps) {
  const sampleStrips = useMemo(() => samples.slice(0, 64), [samples]);
  const timeline = useMemo(() => samples.slice(0, 128), [samples]);

  return (
    <div className="measurement-viz">
      <div className="histogram">
        {LABELS.map(({ key, color, name }) => {
          const value = counts[key] ?? 0;
          const pct = shots > 0 ? Math.max(0, Math.min(100, (value / shots) * 100)) : 0;
          return (
            <div key={key} className="bar-row">
              <span className="bar-label">{name}</span>
              <div className="bar-track" aria-label={`${name} probability`}>
                <div className="bar-fill" style={{ width: `${pct}%`, backgroundColor: color }} />
              </div>
              <span className="bar-count">
                {value}/{shots}
              </span>
            </div>
          );
        })}
      </div>
      {sampleStrips.length > 0 && (
        <div className="sample-strip" aria-label="measurement samples preview">
          {sampleStrips.map((sample, index) => (
            <span
              key={`${sample}-${index}`}
              className={`sample-dot ${sample === "plus" ? "plus" : "minus"}`}
              title={`Shot ${index + 1}: ${sample}`}
            />
          ))}
          {samples.length > sampleStrips.length && <span className="sample-ellipsis">…</span>}
        </div>
      )}
      {timeline.length > 0 && (
        <div className="sample-timeline" role="list" aria-label="measurement timeline">
          {timeline.map((sample, index) => (
            <button
              key={`timeline-${index}`}
              type="button"
              className={`timeline-dot-button ${sample === "plus" ? "plus" : "minus"}`}
              title={`Shot ${index + 1}: ${sample}`}
              aria-label={`Shot ${index + 1}: ${sample}`}
              data-shot-index={index + 1}
              data-shot-value={sample}
            >
              <span className="timeline-dot" />
            </button>
          ))}
          {samples.length > timeline.length && <span className="sample-ellipsis">…</span>}
        </div>
      )}
    </div>
  );
}
