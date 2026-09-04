export interface DiagnosticsItem {
  label: string;
  meaning: string;
  value: string;
}

export interface DiagnosticsProps {
  caption?: string;
  items: readonly DiagnosticsItem[];
}

/**
 * Beat 5's numbers readout: every number labelled with what it means.
 *
 * No value ever appears without its `meaning` line -- that is the point of
 * this component, not an incidental style choice. A definition list keeps
 * the label/value/meaning grouping explicit for assistive technology, and
 * the grid collapses to one column on a narrow viewport rather than
 * shrinking the value text.
 */
export function Diagnostics({caption, items}: DiagnosticsProps): React.JSX.Element {
  return (
    <figure className="diagnostics">
      <dl className="diagnostics-grid">
        {items.map((item) => (
          <div className="diagnostics-item" key={item.label}>
            <dt className="diagnostics-item__label">{item.label}</dt>
            <dd className="diagnostics-item__value">{item.value}</dd>
            <dd className="diagnostics-item__meaning">{item.meaning}</dd>
          </div>
        ))}
      </dl>
      {caption !== undefined && <figcaption>{caption}</figcaption>}
    </figure>
  );
}
