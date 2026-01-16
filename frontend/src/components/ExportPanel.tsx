import { useEffect, useMemo, useState } from "react";

import { exportCircuitApi } from "../services/api";
import type { ExportResponseDto } from "../types/schemas";
import { useAppSelector } from "../hooks/useRedux";

export interface ExportPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

function downloadTextFile(filename: string, contents: string) {
  const blob = new Blob([contents], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function ExportPanel({ isOpen, onClose }: ExportPanelProps) {
  const circuit = useAppSelector((state) => state.circuit);
  const noise = useAppSelector((state) => state.simulation.noise);
  const focusQubit = useAppSelector((state) => state.simulation.focusQubit);
  const [share, setShare] = useState(false);
  const [name, setName] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExportResponseDto | null>(null);

  const circuitDto = useMemo(
    () => ({
      qubit_count: circuit.qubitCount,
      global_phase: null,
      gates: circuit.gates.map((gate) => ({
        name: gate.name,
        targets: gate.targets,
        controls: gate.controls ?? [],
        parameters: gate.parameters,
        metadata: {}
      }))
    }),
    [circuit]
  );

  const noisePayload = useMemo(() => {
    if (
      !noise.enabled ||
      (noise.depolarizing === 0 && noise.amplitudeDamping === 0 && noise.phaseDamping === 0)
    ) {
      return null;
    }
    return {
      depolarizing: noise.depolarizing || null,
      amplitude_damping: noise.amplitudeDamping || null,
      phase_damping: noise.phaseDamping || null
    };
  }, [noise]);

  useEffect(() => {
    if (isOpen) {
      setStatus("idle");
      setError(null);
      setResult(null);
    }
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  const handleGenerate = async () => {
    try {
      setStatus("loading");
      setError(null);
      const response = await exportCircuitApi({
        circuit: circuitDto,
        noise: noisePayload,
        focus_qubit: focusQubit,
        share,
        name: share ? name || null : null
      });
      setResult(response);
      setStatus("ready");
    } catch (err) {
      setStatus("error");
      setResult(null);
      setError(err instanceof Error ? err.message : "Export failed");
    }
  };

  const handleDownload = (type: "qasm" | "json") => {
    if (!result) return;
    const baseName = name.trim() || "circuit";
    if (type === "qasm") {
      downloadTextFile(`${baseName}.qasm`, result.qasm);
    } else {
      downloadTextFile(`${baseName}-snapshots.json`, result.snapshot_json);
    }
  };

  const shareLink =
    result?.share_id && typeof window !== "undefined"
      ? `${window.location.origin}?circuit=${result.share_id}`
      : null;
  const embedSnippet =
    result?.share_id && typeof window !== "undefined"
      ? `<iframe src="${window.location.origin}?circuit=${result.share_id}&embed=1" width="600" height="520" style="border:none;"></iframe>`
      : null;

  const handleCopyLink = async () => {
    if (!shareLink || !navigator.clipboard) return;
    try {
      await navigator.clipboard.writeText(shareLink);
    } catch {
      // Ignore clipboard errors; user can copy manually.
    }
  };

  return (
    <div className="export-backdrop">
      <div className="export-panel">
        <header className="export-header">
          <h3>Export &amp; Share</h3>
          <button onClick={onClose} className="text-button">
            Close
          </button>
        </header>
        <div className="export-content">
          <p className="muted">
            Generate OpenQASM 3 and snapshot JSON exports. Optionally create a saved circuit link.
          </p>
          <div className="export-form">
            <label className="checkbox">
              <input
                type="checkbox"
                checked={share}
                onChange={(event) => setShare(event.target.checked)}
              />
              Create shareable circuit entry
            </label>
            {share && (
              <input
                type="text"
                placeholder="Circuit name (optional)"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            )}
            <button onClick={handleGenerate} disabled={status === "loading"}>
              {status === "loading" ? "Generating…" : "Generate exports"}
            </button>
          </div>
          {error && <p className="error">{error}</p>}
          {status === "ready" && result && (
            <div className="export-results">
              <div className="export-actions">
                <button onClick={() => handleDownload("qasm")}>Download QASM</button>
                <button onClick={() => handleDownload("json")}>Download snapshots JSON</button>
              </div>
              <p className="muted">Snapshots: {result.snapshot_count} · focus q[{focusQubit}]</p>
              {shareLink && (
                <div className="share-link">
                  <input type="text" value={shareLink} readOnly />
                  <button onClick={handleCopyLink}>Copy</button>
                </div>
              )}
              {embedSnippet && (
                <div className="embed-snippet">
                  <label>Embed snippet</label>
                  <textarea readOnly value={embedSnippet} rows={3} />
                  <button
                    onClick={async () => {
                      if (!navigator.clipboard) return;
                      try {
                        await navigator.clipboard.writeText(embedSnippet);
                      } catch {
                        /* ignore */
                      }
                    }}
                  >
                    Copy iframe
                  </button>
                </div>
              )}
            </div>
          )}
          {status === "error" && <p className="error">Unable to export. Try again.</p>}
        </div>
      </div>
    </div>
  );
}
