import { useEffect, useMemo, useRef, useId } from "react";

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
  const headingId = useId();

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
        subtitle: target,
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
          button?.focus();
        }
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [dispatch, items.length, simulation.selectedStep]);

  return (
    <section
      className="timeline-scrubber"
      aria-labelledby={headingId}
      role="region"
    >
      <div className="timeline-header">
        <h3 id={headingId}>
          Timeline{" "}
          <span className="timeline-hint">
            (<kbd>←</kbd>/<kbd>→</kbd>)
          </span>
        </h3>
        <span className="timeline-meta" aria-live="polite">
          {items.length > 0 ? `Step ${selected + 1} of ${items.length}` : "No steps"}
        </span>
      </div>
      {items.length === 0 ? (
        <p className="placeholder" role="status">
          Timeline will appear once gates are added.
        </p>
      ) : (
        <div
          className="timeline-track"
          ref={containerRef}
          role="listbox"
          aria-label="Simulation timeline steps"
          aria-activedescendant={`timeline-step-${selected}`}
        >
          {items.map((item, index) => (
            <button
              key={`${item.step}-${index}`}
              id={`timeline-step-${index}`}
              type="button"
              role="option"
              data-step-index={index}
              className={`timeline-step ${index === selected ? "active" : ""}`}
              onClick={() => dispatch(setSelectedStep(index))}
              aria-selected={index === selected}
              aria-label={`Step ${item.step}: ${item.label}${item.subtitle ? ` on ${item.subtitle}` : ""}`}
            >
              <span className="timeline-pill-step" aria-hidden="true">
                {item.step}
              </span>
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
