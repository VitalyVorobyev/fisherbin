import type {Config} from "@docusaurus/types";
import type {Options as ClassicOptions} from "@docusaurus/preset-classic";

const config: Config = {
  title: "ScoreQuant",
  tagline: "Information-optimal score-space quantization",
  favicon: "img/mark.svg",
  url: "https://vitalyvorobyev.github.io",
  baseUrl: "/scorequant/portal/",
  organizationName: "VitalyVorobyev",
  projectName: "scorequant",
  trailingSlash: false,
  // Matches the separator AppShell already uses for the pages it titles itself,
  // so blog routes — whose titles come from Docusaurus metadata — read the same.
  titleDelimiter: "·",
  onBrokenLinks: "throw",
  onBrokenAnchors: "throw",
  markdown: {hooks: {onBrokenMarkdownLinks: "throw"}},
  plugins: [
    () => ({
      name: "runtime-boundary-warnings",
      configureWebpack: () => ({
        // These two imports intentionally resolve only in the assembled static
        // artifact; keeping them dynamic is what prevents eager runtime loads.
        ignoreWarnings: [
          {module: /SearchDialog\.tsx$/, message: /request of a dependency is an expression/},
          {module: /lab\.worker\.tsx?$/, message: /request of a dependency is an expression/}
        ]
      })
    })
  ],
  presets: [
    [
      "classic",
      {
        docs: false,
        // The development blog is the portal's plain-English record of what
        // changed and why. Docusaurus owns routing, MDX, tags, and the feed;
        // `src/theme/Layout` renders every one of those routes in the
        // ScoreQuant shell rather than the stock Docusaurus chrome.
        blog: {
          path: "blog",
          routeBasePath: "blog",
          // Docusaurus appends the site title, so this must not repeat it.
          blogTitle: "Development blog",
          blogDescription:
            "Plain-English notes on what changed in ScoreQuant, why it matters, and what is next.",
          // No recent-posts rail: `src/theme/BlogLayout` drops it, so generating
          // one would only ship unused data. The index and the post paginator
          // carry navigation instead.
          blogSidebarCount: 0,
          postsPerPage: 10,
          showReadingTime: true,
          // Each of these is a real editorial rule, enforced at build time: a
          // post declares an author who exists, carries only known tags, and
          // states its own summary above the fold.
          onInlineAuthors: "throw",
          onInlineTags: "throw",
          onUntruncatedBlogPosts: "throw",
          feedOptions: {
            type: ["rss", "atom"],
            title: "ScoreQuant development blog",
            description:
              "Plain-English notes on what changed in ScoreQuant, why it matters, and what is next.",
            copyright: `Copyright © ${String(new Date().getFullYear())} ScoreQuant contributors.`
          }
        },
        pages: {},
        sitemap: {changefreq: "weekly", priority: 0.6},
        theme: {customCss: "./src/css/global.css"}
      } satisfies ClassicOptions
    ]
  ],
  themeConfig: {
    image: "img/social-card.svg",
    colorMode: {defaultMode: "light", disableSwitch: true, respectPrefersColorScheme: false},
    metadata: [
      {name: "theme-color", content: "#07152f"},
      {name: "description", content: "Learn, inspect, and run information-preserving score-space quantization."}
    ]
  }
};

export default config;
