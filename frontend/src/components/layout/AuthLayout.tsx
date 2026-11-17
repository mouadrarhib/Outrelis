import { Outlet } from 'react-router'
import { DiscoveryDiagram } from './DiscoveryDiagram'

export function AuthLayout() {
  return <main className="shell">
    <aside className="brand" aria-label="About Outrelis">
      <span className="logo-plate"><img src="/outrelis-logo.svg" alt="Outrelis" width="192" height="56" /></span>
      <div className="brand-content">
        <h2>A place to find<br />what’s <em>next.</em></h2>
        <p className="brand-copy">Discover local businesses.<br />Make room for new opportunities.</p>
        <DiscoveryDiagram />
      </div>
      <div className="brand-foot"><span>Considered connections.<br />New possibilities.</span><span className="foot-note">For freelancers<br />and small agencies.</span></div>
    </aside>
    <section className="form-panel" aria-label="Authentication">
      <header className="panel-top"><span className="mobile-logo"><span className="logo-plate"><img src="/outrelis-logo.svg" alt="Outrelis" width="152" height="44" /></span></span></header>
      <div className="form-wrap"><Outlet /></div>
    </section>
  </main>
}
