import Link from "@docusaurus/Link";
import Layout from "@theme/Layout";

import {PageIntro} from "../components/PageIntro";
import {BROWSER_MATRIX, LESSONS, LESSON_STEPS, type Lesson} from "../data/lessons";
import {LAB_LIMITS} from "../lab/protocol";

/**
 * The lesson index.
 *
 * Historically this route was a free-form solver console: pickers for runner,
 * solver, criterion and bin budget over a score table with no stated model,
 * task or provenance. That taught nothing (ADR 0029). The route is kept, the
 * console is gone. Each lesson is one dataset and one task, and the browser
 * runtime is loaded only by a lesson's own experiment, never here: this page
 * imports `LAB_LIMITS` (a plain constant) and nothing that reaches the worker.
 */

const CONTRACT_ROWS: readonly {key: keyof Lesson["contract"]; label: string}[] = [
  {key: "observation", label: "Observation"},
  {key: "interest", label: "Parameters of interest"},
  {key: "nuisance", label: "Nuisance"},
  {key: "referencePoint", label: "Reference point"},
  {key: "sourceMeasure", label: "Source measure"},
  {key: "provenance", label: "Score provenance"},
  {key: "admissibleLabels", label: "Admissible labels"},
  {key: "taskOutput", label: "Task and output"},
  {key: "criterion", label: "Criterion"},
  {key: "budget", label: "Bin budget K"},
  {key: "evaluation", label: "Evaluation"}
];

function LessonCard({lesson}: {lesson: Lesson}): React.JSX.Element {
  return (
    <article className="lesson" aria-labelledby={`lesson-${lesson.slug}`}>
      <header className="lesson__head">
        <div>
          <span className={`lesson__status lesson__status--${lesson.status}`}>
            {lesson.status === "complete" ? "Lesson" : "Walkthrough · lesson pattern pending"}
          </span>
          <h2 id={`lesson-${lesson.slug}`}>
            <Link to={lesson.href}>{lesson.title}</Link>
          </h2>
          <p className="lesson__question">{lesson.question}</p>
        </div>
      </header>
      <dl className="lesson__contract">
        {CONTRACT_ROWS.map(({key, label}) => (
          <div key={key}>
            <dt>{label}</dt>
            <dd>{lesson.contract[key]}</dd>
          </div>
        ))}
        <div className="lesson__browser">
          <dt>In your browser</dt>
          <dd>{lesson.browser}</dd>
        </div>
      </dl>
      <Link className="plain-link" to={lesson.href}>
        Open the {lesson.status === "complete" ? "lesson" : "walkthrough"} →
      </Link>
    </article>
  );
}

export default function Lessons(): React.JSX.Element {
  return (
    <Layout title="Lessons" description="One dataset and one statistical task per lesson, taught in the same order; the browser runs at the end.">
      <PageIntro
        eyebrow="Lessons"
        title="One dataset, one task, in the same order every time"
        lead="Each lesson states its problem as a contract, writes the model and its score down, decides what may be grouped together, runs the fit, evaluates it against a matching baseline, and only then offers one experiment. Nothing computes in your browser until that experiment asks for it."
      />
      <section className="section-wrap lessons-order" aria-labelledby="lesson-order">
        <h2 id="lesson-order" className="visually-hidden">Reading order</h2>
        <ol className="lesson-steps">
          {LESSON_STEPS.map((step) => (
            <li key={step.title}>
              <strong>{step.title}</strong>
              <span>{step.detail}</span>
            </li>
          ))}
        </ol>
      </section>
      <section className="section-wrap section-rule lessons-list" aria-labelledby="lessons-heading">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Choose by the shape of your problem</span>
            <h2 id="lessons-heading">Four datasets, two tasks</h2>
          </div>
          <p>
            Pick by what you observe, what you estimate and where your scores come from, not by
            the field the data happens to be from.
          </p>
        </div>
        {LESSONS.map((lesson) => (
          <LessonCard key={lesson.slug} lesson={lesson} />
        ))}
      </section>
      <section className="section-wrap section-rule lessons-runtime" aria-labelledby="runtime-heading">
        <div className="section-heading">
          <div>
            <span className="eyebrow">What the browser can run</span>
            <h2 id="runtime-heading">The same NumPy backend, inside the page</h2>
          </div>
          <p>
            A lesson&rsquo;s experiment loads ScoreQuant&rsquo;s own wheel into a Web Worker and
            runs the NumPy backend on the score table you can already see. Inputs stay in the tab.
          </p>
        </div>
        <div className="provenance-grid">
          <div>
            <small>Rows</small>
            <strong>up to {LAB_LIMITS.maxRows.toLocaleString()}</strong>
          </div>
          <div>
            <small>Score dimensions</small>
            <strong>up to {LAB_LIMITS.maxDimensions}</strong>
          </div>
          <div>
            <small>Hard bins</small>
            <strong>up to {LAB_LIMITS.maxBins}</strong>
          </div>
        </div>
        {/* A horizontally scrollable region must be reachable from the keyboard. */}
        <div className="lessons-matrix" role="region" aria-label="Browser runtime capability matrix" tabIndex={0}>
          <table>
            <caption>Task, criterion and solver pairs the browser runtime admits</caption>
            <thead>
              <tr>
                <th scope="col">Task</th>
                <th scope="col">Criterion</th>
                <th scope="col">Solver</th>
                <th scope="col">Runs</th>
                <th scope="col">Why</th>
              </tr>
            </thead>
            <tbody>
              {BROWSER_MATRIX.map((row) => (
                <tr key={`${row.task}-${row.criterion}-${row.solver}`}>
                  <td><code>{row.task}</code></td>
                  <td><code>{row.criterion}</code></td>
                  <td><code>{row.solver}</code></td>
                  <td>{row.runnable ? "yes" : "refused"}</td>
                  <td>{row.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="provenance-note">
          <span aria-hidden="true">◇</span>
          <span>
            A browser run is a deterministic NumPy float64 fit for the weighted table it was given.
            It does not make estimated input ratios exact, and it does not turn an exchange-stable
            partition into a global optimum. The full task and solver contract is on the{" "}
            <Link to="/api">API page</Link>.
          </span>
        </p>
      </section>
    </Layout>
  );
}
