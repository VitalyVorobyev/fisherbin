import {describe, expect, it} from "vitest";

import {isActiveNavEntry, isBlogPostList} from "../src/lib/navigation";

// The deployed baseUrl, post root-site promotion. Neither predicate may
// hard-code it — it is exercised here only as an input fixture.
const base = "/scorequant";

describe("primary navigation highlighting", () => {
  it("marks the entry active on its own route, with or without a trailing slash", () => {
    expect(isActiveNavEntry(`${base}/theory`, "/theory")).toBe(true);
    expect(isActiveNavEntry(`${base}/blog/`, "/blog")).toBe(true);
  });

  it("stays active on routes nested below the entry", () => {
    expect(isActiveNavEntry(`${base}/blog/why-the-best-bins-cannot-be-certified`, "/blog")).toBe(true);
    expect(isActiveNavEntry(`${base}/blog/tags/research`, "/blog")).toBe(true);
    expect(isActiveNavEntry(`${base}/blog/page/2`, "/blog")).toBe(true);
  });

  it("does not leak across entries or onto the home route", () => {
    expect(isActiveNavEntry(`${base}/docs`, "/blog")).toBe(false);
    expect(isActiveNavEntry(`${base}/blog`, "/docs")).toBe(false);
    expect(isActiveNavEntry(`${base}/`, "/docs")).toBe(false);
  });

  it("survives a change of baseUrl", () => {
    expect(isActiveNavEntry("/scorequant/blog/some-post", "/blog")).toBe(true);
    expect(isActiveNavEntry("/blog", "/blog")).toBe(true);
  });
});

describe("blog index detection", () => {
  it("is true for the index and its numbered pages", () => {
    expect(isBlogPostList(`${base}/blog`)).toBe(true);
    expect(isBlogPostList(`${base}/blog/`)).toBe(true);
    expect(isBlogPostList(`${base}/blog/page/2`)).toBe(true);
  });

  it("is false for posts, tags, and the archive", () => {
    // These carry their own h1; a second PageIntro would duplicate it.
    expect(isBlogPostList(`${base}/blog/why-the-best-bins-cannot-be-certified`)).toBe(false);
    expect(isBlogPostList(`${base}/blog/tags/research`)).toBe(false);
    expect(isBlogPostList(`${base}/blog/archive`)).toBe(false);
  });
});
