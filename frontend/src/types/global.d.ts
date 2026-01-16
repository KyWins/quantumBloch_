declare global {
  interface Window {
    Plotly?: {
      react: (
        element: HTMLElement,
        data: Array<Record<string, unknown>>,
        layout: Record<string, unknown>,
        config: Record<string, unknown>
      ) => Promise<void>;
      purge: (element: HTMLElement) => void;
    };
  }
}

export {};
