import AxeBuilder from "@axe-core/playwright";
import type {Page} from "@playwright/test";
import {expect, test} from "@playwright/test";

/**
 * Drives the real header control (`.theme-toggle`, wired to Docusaurus's
 * `useColorMode`) rather than `page.emulateMedia`, so the scan below
 * exercises what a reader actually does. Docusaurus persists the chosen
 * theme to `localStorage` and restores it on every navigation, so a route
 * that was left in dark mode by an earlier iteration would otherwise leak
 * into the next route's "light" scan; this only clicks the toggle when the
 * page is not already in the requested theme, which both avoids that leak
 * and gives every scan a known starting state.
 */
async function setTheme(page: Page, theme: "light" | "dark"): Promise<void> {
  const current = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
  if (current === theme) return;
  const label = theme === "dark" ? "Switch to dark mode" : "Switch to light mode";
  await page.getByRole("button", {name: label}).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
  // The header is `position: sticky` with `backdrop-filter: blur(18px)`, which
  // needs its own compositor pass; sampling it (or nearby recolored text) in
  // the same tick the attribute flips is a real, reproducible source of
  // false-positive `color-contrast` violations at transiently-blended colors
  // that never render for a reader — confirmed by scanning this page 15 times
  // back-to-back and watching the reported foreground hex (and the flagged
  // element) change from run to run while the steady-state token pairs stay
  // comfortably compliant. A short settle avoids scanning mid-repaint.
  await page.waitForTimeout(200);
}

/**
 * Every route the shell renders. The scan below covers a subset; this list is
 * what the landmark check walks, and it is deliberately the wider of the two.
 */
const ROUTES = [
  "./",
  "./get-started/",
  "./api/",
  "./walkthroughs/",
  "./walkthroughs/flowcyt/",
  "./walkthroughs/hep/",
  "./walkthroughs/michelson/",
  "./walkthroughs/ratios/",
  "./benchmarks/",
  "./research/",
  "./lab/"
];

/**
 * The routes scanned by axe. The two docs-plugin routes are scanned as well as
 * the home page: they render through swizzled theme components
 * (src/theme/DocRoot/Layout/Main and src/theme/DocItem/Layout) rather than the
 * stock ones, so nothing upstream vouches for their markup.
 */
const SCANNED = [
  "./",
  "./get-started/",
  "./research/",
  "./walkthroughs/",
  "./walkthroughs/flowcyt/",
  "./walkthroughs/hep/",
  "./walkthroughs/michelson/",
  "./walkthroughs/ratios/",
  "./lab/"
];

test("home states the problem and then measures it", async ({page}) => {
  await page.goto("./");
  // The assertions target the page's shape rather than a slogan: the opening
  // names the task (labels for the parameters you estimate), the figure shows
  // the committed partition, and the comparison is the measured one.
  await expect(page.getByRole("heading", {name: /Choose K labels for the parameters/})).toBeVisible();
  await expect(page.getByRole("img", {name: /Score-space partition/})).toBeVisible();
  await expect(page.getByText("ScoreQuant, same data, same bin budget")).toBeVisible();
});

test("every route renders one main landmark and none of them loads a runtime", async ({page}) => {
  const heavyRequests: string[] = [];
  page.on("request", (request) => {
    if (/pyodide|marimo|scorequant-.*\.whl/.test(request.url())) heavyRequests.push(request.url());
  });
  for (const route of ROUTES) {
    await page.goto(route);
    // #main-content is AppShell's own landmark, and it must be the only one.
    // The stock layouts of both the blog and the docs plugin render a second
    // <main> of their own inside it; src/theme/BlogLayout and
    // src/theme/DocRoot/Layout/Main exist to strip those. Nested landmarks are
    // invalid HTML and an accessibility failure, and the axe scan below only
    // covers SCANNED, so this count is what catches a regression on the routes
    // it does not reach.
    await expect(page.locator("#main-content")).toBeVisible();
    expect(await page.locator("main").count(), `nested landmark on ${route}`).toBe(1);
  }
  // Including ./lab/: the Lab page itself must cost an ordinary page load, and
  // only pressing a run button may reach the runtime.
  expect(heavyRequests).toEqual([]);
});

/**
 * One test per route rather than one loop inside a single test. Sixteen axe
 * analyses plus their navigations and theme settles do not fit in one 30s
 * budget on a CI runner — the loop form failed there while passing locally,
 * which is the least useful way for a suite to fail. Split, each route gets
 * its own budget and the projects' workers run them in parallel; the set of
 * assertions is unchanged.
 */
for (const route of SCANNED) {
  test(`${route} has no accessibility violations in either theme`, async ({page}) => {
    await page.goto(route);
    for (const theme of ["light", "dark"] as const) {
      await setTheme(page, theme);
      const accessibility = await new AxeBuilder({page}).analyze();
      expect(accessibility.violations, `accessibility violations on ${route} (${theme} mode)`).toEqual([]);
    }
  });
}

test("core learning routes render and search opens from the keyboard", async ({page}) => {
  await page.goto("./walkthroughs/");
  await expect(page.getByRole("heading", {name: "Walkthroughs", level: 1})).toBeVisible();
  await page.keyboard.press("Control+k");
  await expect(page.getByRole("dialog", {name: "Search ScoreQuant"})).toBeVisible();
  await page.getByPlaceholder("Search concepts, tasks, and symbols").fill("ExecutionConfig");
  await expect(page.getByRole("link", {name: /ExecutionConfig/})).toBeVisible();
});

test("the get-started LiveFit demo stays behind its click, then actually reaches the runtime", async ({page}, testInfo) => {
  test.skip(testInfo.project.name !== "desktop", "One activation-gated runtime pass is sufficient.");
  test.setTimeout(120_000);
  const heavyRequests: string[] = [];
  page.on("request", (request) => {
    if (/pyodide|marimo|scorequant-.*\.whl/.test(request.url())) heavyRequests.push(request.url());
  });

  await page.goto("./get-started/");
  await expect(page.getByRole("heading", {name: "Get started", level: 1})).toBeVisible();
  await expect(page.getByText("D-efficiency printed by get_started_program.py")).toBeVisible();
  const committedValue = await page.locator(".live-fit__committed .live-fit__value").innerText();

  // The invariant's usual, negative direction: navigating to the page and
  // letting it settle -- including the committed panel above, which needs no
  // runtime at all -- must not have reached Pyodide or the wheel.
  expect(heavyRequests).toEqual([]);

  await page.getByRole("button", {name: "Refit this table in your browser"}).click();
  await expect(page.locator(".live-fit__state")).toHaveText(/complete|error/, {timeout: 110_000});
  await expect(page.locator(".live-fit__state")).toHaveText("complete");

  // The other direction, which a demo that silently never worked would also
  // pass if only the negative half were asserted: activation actually did
  // reach the heavy runtime, and the run that came back agrees with the
  // number this page already published.
  expect(heavyRequests.length).toBeGreaterThan(0);
  const liveValue = await page.locator(".live-fit__result--live .live-fit__value").innerText();
  expect(liveValue).toBe(committedValue);
});

test("the flowcyt walkthrough tells the study end to end without loading a runtime", async ({page}) => {
  // The narrative route must stay a narrative route: the moment it pulls the
  // wheel it stops meeting the ordinary-route budget, and the reader pays 15 MB
  // for a page they may only be reading.
  const heavyRequests: string[] = [];
  page.on("request", (request) => {
    if (/pyodide|marimo|scorequant-.*\.whl|flowcyt-scores/.test(request.url())) {
      heavyRequests.push(request.url());
    }
  });
  await page.goto("./walkthroughs/flowcyt/");

  await expect(page.getByRole("heading", {name: /Bone-marrow cell populations/})).toBeVisible();
  for (const section of [
    "The report is a few fractions; the instrument measures every cell",
    "The data, and what travels with it",
    "The numbers"
  ]) {
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

test("the lessons page lists one lesson per walkthrough and loads no runtime", async ({page}) => {
  const heavyRequests: string[] = [];
  page.on("request", (request) => {
    if (/pyodide|marimo|scorequant-.*\.whl/.test(request.url())) heavyRequests.push(request.url());
  });
  await page.goto("./lab/");
  await expect(page.getByRole("heading", {name: /One dataset, one task/, level: 1})).toBeVisible();
  const walkthroughLinks = page.locator('a[href*="/walkthroughs/"]');
  expect(await walkthroughLinks.count()).toBeGreaterThanOrEqual(4);
  expect(heavyRequests).toEqual([]);
});
