import Head from "@docusaurus/Head";
import Link from "@docusaurus/Link";
import {useLocation} from "@docusaurus/router";
import clsx from "clsx";
import {useEffect, useState} from "react";

import {isActiveNavEntry} from "../lib/navigation";
import {Logo} from "./Logo";
import {SearchDialog} from "./SearchDialog";

const navigation = [
  ["Docs", "/docs"],
  ["API", "/api"],
  ["Examples", "/examples"],
  ["Showcase", "/showcase"],
  ["Theory", "/theory"],
  ["Benchmarks", "/benchmarks"],
  ["Research", "/research"],
  ["Blog", "/blog"]
] as const;

interface AppShellProps {
  children: React.ReactNode;
  description: string;
  lab?: boolean;
  /**
   * Set false where Docusaurus already emits the page metadata — the blog and
   * the error pages. Two competing <title> tags would otherwise race, and the
   * winner would be decided by render order rather than by intent.
   */
  manageHead?: boolean;
  title: string;
}

export function AppShell({
  children,
  description,
  lab = false,
  manageHead = true,
  title
}: AppShellProps): React.JSX.Element {
  const {pathname} = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  useEffect(() => {
    const shortcut = (event: KeyboardEvent): void => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener("keydown", shortcut);
    return () => window.removeEventListener("keydown", shortcut);
  }, []);

  return (
    <div className={clsx("site-shell", lab && "site-shell--lab")}>
      {manageHead && (
        <Head>
          <title>{title === "ScoreQuant" ? title : `${title} · ScoreQuant`}</title>
          <meta name="description" content={description} />
        </Head>
      )}
      <a className="skip-link" href="#main-content">Skip to content</a>
      <header className="site-header">
        <div className="site-header__inner">
          <Logo />
          <nav className={clsx("site-nav", menuOpen && "site-nav--open")} aria-label="Primary">
            {navigation.map(([label, href]) => (
              <Link key={href} to={href} className={isActiveNavEntry(pathname, href) ? "is-active" : ""}>
                {label}
              </Link>
            ))}
          </nav>
          <div className="site-actions">
            <button className="search-trigger" onClick={() => setSearchOpen(true)} aria-label="Search">
              <span aria-hidden="true">⌕</span><span>Search</span><kbd>⌘ K</kbd>
            </button>
            <Link className="lab-link" to="/lab">Open Lab <span aria-hidden="true">↗</span></Link>
            <button
              className="menu-trigger"
              aria-expanded={menuOpen}
              aria-label="Toggle navigation"
              onClick={() => setMenuOpen((value) => !value)}
            >
              <span/><span/>
            </button>
          </div>
        </div>
      </header>
      <main id="main-content" data-pagefind-body>{children}</main>
      {!lab && (
        <footer className="site-footer">
          <div>
            <Logo />
            <p>Hard bins, with the information loss made visible.</p>
          </div>
          <div className="site-footer__links">
            <span>Learn</span><Link to="/docs">Start here</Link><Link to="/theory">Theory</Link><Link to="/examples">Examples</Link><Link to="/blog">Blog</Link>
          </div>
          <div className="site-footer__links">
            <span>Reference</span><a href="/scorequant/reference/">Python API</a><a href="https://github.com/VitalyVorobyev/scorequant">GitHub</a>
          </div>
          <small>Open source · research provenance is explicit · no browser data leaves your device</small>
        </footer>
      )}
      <SearchDialog open={searchOpen} onClose={() => setSearchOpen(false)} />
    </div>
  );
}
