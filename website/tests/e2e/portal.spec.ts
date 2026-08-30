import AxeBuilder from "@axe-core/playwright";
import {expect, test} from "@playwright/test";

test("home is navigable, evidence-backed, and free of heavy runtime requests", async ({page}) => {
  const heavyRequests: string[] = [];
  page.on("request", (request) => {
    if (/pyodide|marimo|scorequant-.*\.whl/.test(request.url())) heavyRequests.push(request.url());
  });
  await page.goto("./");
  await expect(page.getByRole("heading", {name: /Compress events/})).toBeVisible();
  await expect(page.getByRole("img", {name: /Score-space partition/})).toBeVisible();
  await expect(page.getByText("JAX + NumPy")).toBeVisible();
  for (const route of ["./docs", "./api", "./examples", "./showcase", "./theory", "./benchmarks", "./research"]) {
    await page.goto(route);
    await expect(page.locator("main")).toBeVisible();
  }
  expect(heavyRequests).toEqual([]);
  await page.goto("./");
  const accessibility = await new AxeBuilder({page}).analyze();
  expect(accessibility.violations).toEqual([]);
});

test("core learning routes render and search opens from the keyboard", async ({page}) => {
  await page.goto("./theory");
  await expect(page.getByRole("heading", {name: /Theory with the failure modes/})).toBeVisible();
  await page.keyboard.press("Control+k");
  await expect(page.getByRole("dialog", {name: "Search ScoreQuant"})).toBeVisible();
  await page.getByPlaceholder("Search concepts, tasks, and symbols").fill("ExecutionConfig");
  await expect(page.getByRole("link", {name: /ExecutionConfig/})).toBeVisible();
});

test("fixture lab runs without loading Pyodide and mobile panels remain reachable", async ({page}) => {
  const pyodideRequests: string[] = [];
  page.on("request", (request) => {
    if (/pyodide|scorequant-.*\.whl/.test(request.url())) pyodideRequests.push(request.url());
  });
  await page.goto("./lab");
  if ((page.viewportSize()?.width ?? 1000) < 820) await page.getByRole("button", {name: "controls"}).click();
  await page.getByRole("button", {name: /Load verified result/}).click();
  if ((page.viewportSize()?.width ?? 1000) < 820) {
    await page.getByRole("button", {name: "diagnostics"}).click();
    await expect(page.getByText("Retained information")).toBeVisible();
  }
  await expect(page.getByText("complete", {exact: true})).toBeVisible();
  expect(pyodideRequests).toEqual([]);
});

test("the native browser runner executes the local ScoreQuant wheel", async ({page}, testInfo) => {
  test.skip(testInfo.project.name !== "desktop", "One cold-runtime smoke test is sufficient.");
  test.setTimeout(120_000);
  await page.goto("./lab");
  await page.getByLabel("Runner").selectOption("pyodide-numpy");
  await page.getByRole("button", {name: "Run locally"}).click();
  await expect(page.getByText("complete", {exact: true})).toBeVisible({timeout: 110_000});
  await expect(page.getByText("numpy/float64/cpu", {exact: true})).toBeVisible();
});

test("lab validation, cancellation, and lazy lesson states are explicit", async ({page}, testInfo) => {
  test.skip(testInfo.project.name !== "desktop", "Desktop covers worker controls; mobile tabs are covered separately.");
  await page.goto("./lab");
  await page.route("**/runtime/manifest.json", async (route) => route.abort());
  await page.getByLabel("Runner").selectOption("pyodide-numpy");
  await page.getByRole("button", {name: "Run locally"}).click();
  await expect(page.getByText(/runtime manifest is unavailable|Failed to fetch/)).toBeVisible();

  await page.unroute("**/runtime/manifest.json");
  await page.getByRole("button", {name: "Run locally"}).click();
  await page.getByRole("button", {name: "Cancel and terminate worker"}).click();
  await expect(page.getByText("cancelled", {exact: true})).toBeVisible();

  await page.getByRole("button", {name: "Load marimo lesson"}).click();
  await expect(page.getByTitle("ScoreQuant marimo lesson")).toHaveAttribute(
    "src",
    "/scorequant/portal/lessons/score-space/"
  );
});

test("the showcase tells the study end to end without loading a runtime", async ({page}) => {
  // The narrative route must stay a narrative route: the moment it pulls the
  // wheel it stops meeting the ordinary-route budget, and the reader pays 15 MB
  // for a page they may only be reading.
  const heavyRequests: string[] = [];
  page.on("request", (request) => {
    if (/pyodide|marimo|scorequant-.*\.whl|flowcyt-scores/.test(request.url())) {
      heavyRequests.push(request.url());
    }
  });
  await page.goto("./showcase");

  await expect(page.getByRole("heading", {name: /Thirty patients/})).toBeVisible();
  for (const section of ["The problem", "The data", "Results"]) {
    await expect(page.getByRole("heading", {name: section})).toBeVisible();
  }

  // The licence is not decoration: the data is CC BY-NC-SA and the attribution
  // travels with anything derived from it.
  await expect(page.getByText("CC-BY-NC-SA-4.0")).toBeVisible();
  await expect(page.getByText(/Marchand-Maillet/)).toBeVisible();

  await expect(page.getByRole("img", {name: /composition of every patient/})).toBeVisible();
  await expect(page.getByRole("img", {name: /macro RMSE against bin budget/})).toBeVisible();
  await expect(page.getByRole("img", {name: /FS INT intensity distribution/})).toBeVisible();

  expect(heavyRequests).toEqual([]);

  const accessibility = await new AxeBuilder({page}).analyze();
  expect(accessibility.violations).toEqual([]);
});

test("marker panels can be filtered by population and expanded", async ({page}, testInfo) => {
  test.skip(testInfo.project.name !== "desktop", "One interaction pass is sufficient.");
  await page.goto("./showcase");

  // "other" dominates every panel, so it starts hidden and can be restored.
  const other = page.getByRole("button", {name: "other", exact: true});
  await expect(other).not.toHaveClass(/is-active/);
  await other.click();
  await expect(other).toHaveClass(/is-active/);

  await expect(page.getByRole("img", {name: /FL5 INT_CD34-PC7/})).toHaveCount(0);
  await page.getByRole("button", {name: /Show all 12 markers/}).click();
  await expect(page.getByRole("img", {name: /FL5 INT_CD34-PC7/})).toBeVisible();
});

test("the lab runs the study's real five-dimensional scores, warm on the second run", async ({page}, testInfo) => {
  test.skip(testInfo.project.name !== "desktop", "One cold-runtime pass is enough; it costs a Pyodide bootstrap.");
  test.setTimeout(300_000);
  await page.goto("./lab");

  // The score table is fetched only when chosen, so the fixture path stays free.
  await page.getByRole("button", {name: /FlowCyt scores/}).click();
  await expect(page.getByText(/5 dimensions/)).toBeVisible({timeout: 30_000});

  await page.getByLabel("Criterion").selectOption("profiled_d_optimality");
  await page.getByRole("button", {name: "HSPCs", exact: true}).click();
  await page.getByLabel("Solver").selectOption("soft_voronoi");
  await page.getByLabel("Runner").selectOption("pyodide-numpy");

  await page.getByRole("button", {name: "Run locally"}).click();
  // Waiting only for "complete" turns any refusal into a full timeout, which
  // reads as a hang and hides the message that would explain it.
  await expect(page.locator(".lab-state")).toHaveText(/complete|error/, {timeout: 280_000});
  await expect(page.locator(".lab-state")).toHaveText("complete");

  // The reported retention must be the profiled one, and must say so: the
  // full-D retention of a D_s fit answers a different question.
  await expect(page.getByText(/Profiled D_s \(HSPCs\)/)).toBeVisible();
  await expect(page.getByText("numpy/float64/cpu", {exact: true})).toBeVisible();

  // A second run reuses the warmed runtime rather than reinstalling the wheel.
  const started = Date.now();
  await page.getByRole("button", {name: "Run locally"}).click();
  await expect(page.locator(".lab-state")).toHaveText(/complete|error/, {timeout: 120_000});
  await expect(page.locator(".lab-state")).toHaveText("complete");
  await expect(page.getByText(/warm — reruns skip the cold start/)).toBeVisible();
  testInfo.annotations.push({type: "warm-run-ms", description: String(Date.now() - started)});
});

test("a local file is read in the tab and validated before anything runs", async ({page}, testInfo) => {
  test.skip(testInfo.project.name !== "desktop", "One file-handling pass is sufficient.");
  await page.goto("./lab");

  const uploads: string[] = [];
  page.on("request", (request) => {
    if (request.method() === "POST" || request.method() === "PUT") uploads.push(request.url());
  });

  await page.setInputFiles('input[type="file"]', {
    name: "scores.csv",
    mimeType: "text/csv",
    buffer: Buffer.from("alpha,beta,weight\n1,2,1\n2,1,1\n0.5,0.4,2\n-1,0.2,1\n"),
  });
  await expect(page.getByText("scores.csv")).toBeVisible();
  await expect(page.getByText(/4 rows · 2 dimensions/)).toBeVisible();

  // The header row became the score schema, so profiling can name a column.
  await page.getByLabel("Criterion").selectOption("profiled_d_optimality");
  await expect(page.getByRole("button", {name: "alpha", exact: true})).toBeVisible();

  // A malformed file is refused with the row that caused it, not a generic failure.
  await page.setInputFiles('input[type="file"]', {
    name: "broken.csv",
    mimeType: "text/csv",
    buffer: Buffer.from("a,b\n1,2\n3,oops\n"),
  });
  await expect(page.getByText(/Row 3 contains a non-numeric value/)).toBeVisible();

  // Nothing was sent anywhere: there is no server to send it to.
  expect(uploads).toEqual([]);
});
