import { useEffect, useRef } from "react";

export interface MetricSeries {
  name: string;
  values: Array<number | null>;
  color: string;
}

export interface MetricChartProps {
  steps: number[];
  series: MetricSeries[];
  title: string;
}

export function MetricChart({ steps, series, title }: MetricChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current || !window.Plotly) {
      return;
    }

    const traces = series.map((entry) => ({
      type: "scatter",
      mode: "lines+markers",
      x: steps,
      y: entry.values,
      name: entry.name,
      line: { color: entry.color, width: 2 },
      marker: { color: entry.color, size: 6 },
      connectgaps: true
    }));

    const layout = {
      title: { text: title, font: { size: 14 }, x: 0, y: 1 },
      margin: { l: 40, r: 10, t: 32, b: 32 },
      xaxis: { title: "Step", dtick: 1 },
      yaxis: { range: [-1.1, 1.1] },
      legend: { orientation: "h", x: 0, y: -0.2 }
    };

    window.Plotly.react(containerRef.current, traces, layout, {
      displaylogo: false,
      responsive: true
    });
  }, [steps, series, title]);

  return <div className="metric-chart" ref={containerRef} />;
}
