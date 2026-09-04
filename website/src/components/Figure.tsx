export interface FigureProps {
  alt: string;
  caption: React.ReactNode;
  src: string;
  wide?: boolean;
}

/**
 * A captioned static image, sharing the `.chart-figure` frame the SVG charts
 * already use so a page mixes generated plots and rendered images without a
 * visible seam.
 */
export function Figure({alt, caption, src, wide = false}: FigureProps): React.JSX.Element {
  return (
    <figure className={wide ? "chart-figure chart-figure--wide" : "chart-figure"}>
      <img alt={alt} src={src} />
      <figcaption>{caption}</figcaption>
    </figure>
  );
}
