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
        blog: false,
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
