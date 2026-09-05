/**
 * The compact contract every lesson opens with (ADR 0028): the same fixed
 * rows in the same order on every page, so a reader can identify what is
 * observed, what is estimated, what K constrains and how the result is
 * judged before any exposition.
 *
 * Numbers reach a row through the page's facts (`factsFor`), never as a
 * literal typed here; `tests/test_walkthrough_facts.py` guards the MDX that
 * renders this.
 */

export interface ProblemContractProps {
  observation: React.ReactNode;
  interest: React.ReactNode;
  nuisance: React.ReactNode;
  referencePoint: React.ReactNode;
  budget: React.ReactNode;
  admissibleLabels: React.ReactNode;
  sourceMeasure: React.ReactNode;
  provenance: React.ReactNode;
  taskOutput: React.ReactNode;
  evaluation: React.ReactNode;
}

/** Row order and labels, shared with the lesson index so the two agree. */
export const CONTRACT_ROWS: readonly {key: keyof ProblemContractProps; label: string}[] = [
  {key: "observation", label: "Observation"},
  {key: "interest", label: "Parameters of interest"},
  {key: "nuisance", label: "Nuisance"},
  {key: "referencePoint", label: "Reference point"},
  {key: "budget", label: "Bin budget K"},
  {key: "admissibleLabels", label: "Admissible labels"},
  {key: "sourceMeasure", label: "Source measure"},
  {key: "provenance", label: "Score provenance"},
  {key: "taskOutput", label: "Task and output"},
  {key: "evaluation", label: "Evaluation"}
];

export function ProblemContract(props: ProblemContractProps): React.JSX.Element {
  return (
    <dl className="problem-contract" aria-label="Problem contract">
      {CONTRACT_ROWS.map(({key, label}) => (
        <div className="problem-contract__row" key={key}>
          <dt>{label}</dt>
          <dd>{props[key]}</dd>
        </div>
      ))}
    </dl>
  );
}
