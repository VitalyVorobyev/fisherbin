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
  for (const route of ["./docs", "./api", "./examples", "./theory", "./benchmarks", "./research"]) {
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
