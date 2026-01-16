import { useEffect, useRef } from "react";

import type { SimulationSnapshot } from "../store/types";

export interface BlochPlotProps {
  snapshots: SimulationSnapshot[];
  selectedStep: number;
  measurementOverlay?: { x: number; y: number; z: number } | null;
}

type Scatter3DTrace = {
  type: "scatter3d";
  mode: "lines" | "markers" | "lines+markers";
  x: number[];
  y: number[];
  z: number[];
  name: string;
  line?: { color: string; width?: number };
  marker?: { size: number; opacity?: number; color?: string };
  hoverinfo?: "skip";
};

type SurfaceTrace = {
  type: "surface";
  opacity: number;
  showscale: boolean;
  x: number[][];
  y: number[][];
  z: number[][];
  hoverinfo?: "skip";
};

type PlotTrace = Scatter3DTrace | SurfaceTrace;

function unitSphereMesh(segments = 32) {
  const u = Array.from({ length: segments }, (_, i) => (2 * Math.PI * i) / (segments - 1));
  const v = Array.from({ length: segments }, (_, j) => (Math.PI * j) / (segments - 1));
  const x: number[][] = [];
  const y: number[][] = [];
  const z: number[][] = [];
  u.forEach((uu, i) => {
    x[i] = [];
    y[i] = [];
    z[i] = [];
    v.forEach((vv, j) => {
      x[i][j] = Math.cos(uu) * Math.sin(vv);
      y[i][j] = Math.sin(uu) * Math.sin(vv);
      z[i][j] = Math.cos(vv);
    });
  });
  return { x, y, z };
}

function buildPath(snapshots: SimulationSnapshot[]) {
  const xs: number[] = [];
  const ys: number[] = [];
  const zs: number[] = [];
  snapshots.forEach((snapshot) => {
    if (snapshot.bloch) {
      xs.push(snapshot.bloch.x);
      ys.push(snapshot.bloch.y);
      zs.push(snapshot.bloch.z);
    }
  });
  return { xs, ys, zs };
}

export function BlochPlot({ snapshots, selectedStep, measurementOverlay }: BlochPlotProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const plotly = window.Plotly;
    if (!containerRef.current || !plotly) {
      return;
    }
    const { xs, ys, zs } = buildPath(snapshots);
    const mesh = unitSphereMesh();
    if (xs.length === 0) {
      plotly.purge(containerRef.current);
      return;
    }
    const safeIndex = Math.min(Math.max(selectedStep, 0), snapshots.length - 1);
    const highlight = snapshots[safeIndex]?.bloch ?? snapshots[snapshots.length - 1]?.bloch;

    const trails: Scatter3DTrace[] = [];
    if (xs.length > 1) {
      trails.push({
        type: "scatter3d",
        mode: "lines+markers",
        x: xs,
        y: ys,
        z: zs,
        line: { color: "#ef4444", width: 4 },
        marker: { size: 4, opacity: 0.8, color: "#ef4444" },
        name: "trajectory"
      });
    }

    const selectedTrace: Scatter3DTrace | null = highlight
      ? {
          type: "scatter3d",
          mode: "markers",
          x: [highlight.x],
          y: [highlight.y],
          z: [highlight.z],
          marker: { size: 12, color: "#6366f1" },
          name: "selected"
        }
      : null;

    const overlayTrace: Scatter3DTrace | null = measurementOverlay
      ? {
          type: "scatter3d",
          mode: "markers",
          x: [measurementOverlay.x],
          y: [measurementOverlay.y],
          z: [measurementOverlay.z],
          marker: { size: 14, color: "#10b981" },
          name: "measurement"
        }
      : null;

    const axisTraces: Scatter3DTrace[] = [
      {
        type: "scatter3d",
        mode: "lines",
        x: [-1.1, 1.1],
        y: [0, 0],
        z: [0, 0],
        line: { color: "#06b6d4", width: 3 },
        hoverinfo: "skip",
        name: "X"
      },
      {
        type: "scatter3d",
        mode: "lines",
        x: [0, 0],
        y: [-1.1, 1.1],
        z: [0, 0],
        line: { color: "#8b5cf6", width: 3 },
        hoverinfo: "skip",
        name: "Y"
      },
      {
        type: "scatter3d",
        mode: "lines",
        x: [0, 0],
        y: [0, 0],
        z: [-1.1, 1.1],
        line: { color: "#f59e0b", width: 3 },
        hoverinfo: "skip",
        name: "Z"
      }
    ];

    const data: PlotTrace[] = [
      {
        type: "surface",
        opacity: 0.15,
        showscale: false,
        x: mesh.x,
        y: mesh.y,
        z: mesh.z,
        hoverinfo: "skip"
      },
      ...axisTraces,
      ...trails
    ];
    if (selectedTrace) data.push(selectedTrace);
    if (overlayTrace) data.push(overlayTrace);

    const layout: Record<string, unknown> = {
      margin: { l: 0, r: 0, b: 0, t: 0 },
      paper_bgcolor: "rgba(0,0,0,0)",
      scene: {
        bgcolor: "rgba(0,0,0,0)",
        aspectmode: "cube",
        xaxis: {
          range: [-1, 1],
          title: { text: "X", font: { color: "#94a3b8" } },
          tickfont: { color: "#64748b" },
          gridcolor: "rgba(148,163,184,0.15)",
          zerolinecolor: "rgba(148,163,184,0.3)"
        },
        yaxis: {
          range: [-1, 1],
          title: { text: "Y", font: { color: "#94a3b8" } },
          tickfont: { color: "#64748b" },
          gridcolor: "rgba(148,163,184,0.15)",
          zerolinecolor: "rgba(148,163,184,0.3)"
        },
        zaxis: {
          range: [-1, 1],
          title: { text: "Z", font: { color: "#94a3b8" } },
          tickfont: { color: "#64748b" },
          gridcolor: "rgba(148,163,184,0.15)",
          zerolinecolor: "rgba(148,163,184,0.3)"
        }
      },
      showlegend: true,
      legend: {
        x: 1,
        y: 1,
        font: { color: "#f8fafc", size: 10 },
        bgcolor: "rgba(0,0,0,0.3)",
        bordercolor: "rgba(255,255,255,0.1)",
        borderwidth: 1
      }
    };

    plotly.react(containerRef.current, data, layout, {
      displaylogo: false,
      responsive: true
    });
  }, [snapshots, selectedStep, measurementOverlay]);

  return <div className="bloch-plot" ref={containerRef} />;
}
