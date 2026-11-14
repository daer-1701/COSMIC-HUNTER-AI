declare module "plotly.js-basic-dist" {
  import type { PlotlyHTMLElement } from "plotly.js";

  const Plotly: {
    newPlot: (
      root: HTMLElement,
      data: object[],
      layout?: object,
      config?: object,
    ) => Promise<PlotlyHTMLElement>;
    purge: (root: PlotlyHTMLElement) => void;
  };

  export default Plotly;
}
