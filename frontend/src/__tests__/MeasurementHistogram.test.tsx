import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { MeasurementHistogram } from "../components/MeasurementHistogram";

describe("MeasurementHistogram", () => {
  it("renders proportional bars for counts", () => {
    const markup = renderToStaticMarkup(
      <MeasurementHistogram counts={{ plus: 3, minus: 1 }} samples={["plus", "minus"]} shots={4} />
    );
    expect(markup).toContain("plus");
    expect(markup).toContain("3/4");
    expect(markup).toContain("width:75%");
  });

  it("renders timeline buttons for samples", () => {
    const samples = new Array(5).fill("plus");
    const markup = renderToStaticMarkup(
      <MeasurementHistogram counts={{ plus: 5, minus: 0 }} samples={samples} shots={5} />
    );
    expect(markup).toContain("data-shot-index=\"1\"");
  });
});
