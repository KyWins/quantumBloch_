import { useEffect, useMemo, useRef } from "react";

import { useAppDispatch, useAppSelector } from "../hooks/useRedux";
import { setSelectedStep } from "../store/simulationSlice";

interface TimelineItem {
  step: number;
  label: string;
  subtitle: string | null;
}

export function TimelineScrubber() {
  const dispatch = useAppDispatch();
  const simulation = useAppSelector((state) => state.simulation);
  const selected = simulation.selectedStep ?? simulation.snapshots.length - 1;
  const containerRef = useRef<HTMLDivElement | null>(null);

  const items = useMemo<TimelineItem[]>(() => {
    if (!simulation.snapshots.length) {
      return [];
    }
    return simulation.snapshots.map((snapshot, index) => {
      const meta = snapshot.metadata ?? {};
      const gate = meta.gate ?? (index === 0 ? "Init" : `Step ${snapshot.step}`);
      const target = meta.targets ? `q[${meta.targets}]` : null;
      return {
        step: snapshot.step,
        label: gate,
        subtitle: target
      };
    });
  }, [simulation.snapshots]);

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (!items.length) return;
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        const direction = event.key === "ArrowLeft" ? -1 : 1;
        const next = Math.min(
          Math.max((simulation.selectedStep ?? items.length - 1) + direction, 0),
          items.length - 1
        );
        dispatch(setSelectedStep(next));
        if (containerRef.current) {
          const button = containerRef.current.querySelector<HTMLButtonElement>(
            `button[data-step-index="${next}"]`
          );
          button?.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
        }
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [dispatch, items.length, simulation.selectedStep]);

  return (
    <section className="timeline-scrubber">
      <div className="timeline-header">
        <h3>Timeline <span className="timeline-hint">(←/→)</span></h3>
        <span className="timeline-meta">steps: {items.length}</span>
      </div>
      {items.length === 0 ? (
        <p className="placeholder">Timeline will appear once gates are added.</p>
      ) : (
        <div className="timeline-track" ref={containerRef}>
          {items.map((item, index) => (
            <button
              key={`${item.step}-${index}`}
              type="button"
              data-step-index={index}
              className={`timeline-step ${index === selected ? "active" : ""}`}
              onClick={() => dispatch(setSelectedStep(index))}
            >
              <span className="timeline-pill-step">{item.step}</span>
              <div className="timeline-text">
                <span className="timeline-label">{item.label}</span>
                {item.subtitle && <span className="timeline-subtitle">{item.subtitle}</span>}
              </div>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}
