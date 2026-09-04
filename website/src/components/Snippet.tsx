import {snippet} from "../lib/snippets";

export interface SnippetProps {
  id: string;
  title?: string;
}

/**
 * One cell of `/get-started`'s single-sourced program: its code, then the
 * stdout `generate_snippets.py` captured actually running it.
 *
 * Nothing here is retyped from a notebook -- `code` and `stdout` are both
 * `website/scripts/get_started_program.py`'s own text, read through
 * `website/src/lib/snippets.ts`. The output block carries its own label and
 * a left border rather than a colour change alone, so the code/output
 * boundary still reads without colour vision. A cell that prints nothing
 * (the initial setup, for instance) renders its code with no output block
 * at all, rather than an empty one.
 *
 * Both blocks scroll horizontally, so both carry `tabIndex` and a name: a
 * scrollable region that cannot be reached by keyboard is unreadable without a
 * mouse, which axe reports as `scrollable-region-focusable`.
 */
export function Snippet({id, title}: SnippetProps): React.JSX.Element {
  const cell = snippet(id);
  return (
    <figure className="snippet">
      {title !== undefined && <figcaption className="snippet__title">{title}</figcaption>}
      <pre className="code-block" tabIndex={0} aria-label={`Source of the ${id} step`}>
        <code>{cell.code}</code>
      </pre>
      {cell.stdout.length > 0 && (
        <div className="snippet__output">
          <span className="snippet__output-label">Output</span>
          <pre
            className="code-block snippet__output-block"
            tabIndex={0}
            aria-label={`Captured output of the ${id} step`}
          >
            <code>{cell.stdout}</code>
          </pre>
        </div>
      )}
    </figure>
  );
}
