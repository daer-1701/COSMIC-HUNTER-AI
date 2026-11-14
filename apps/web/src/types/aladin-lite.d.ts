declare module "aladin-lite" {
  const aladin: {
    init: Promise<unknown>;
    aladin: (target: HTMLElement, options: Record<string, unknown>) => {
      gotoRaDec: (ra: number, dec: number) => void;
      setFov: (fovDeg: number) => void;
    };
  };
  export default aladin;
}
