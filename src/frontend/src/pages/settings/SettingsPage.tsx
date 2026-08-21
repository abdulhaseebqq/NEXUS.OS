function SettingsPage() {
  return (
    <main className="simple-page">
      <div className="simple-page-header">
        <span>SYSTEM</span>

        <h1>Settings</h1>

        <p>
          Configure the NEXUS.OS experience.
        </p>
      </div>

      <section className="settings-grid">
        <article className="simple-card">
          <h2>Appearance</h2>
          <p>
            Dark NEXUS interface is currently active.
          </p>
        </article>

        <article className="simple-card">
          <h2>AI preferences</h2>
          <p>
            Personality and model controls will be
            connected with the AI engine.
          </p>
        </article>

        <article className="simple-card">
          <h2>Devices</h2>
          <p>
            Mobile and desktop pairing will be added
            in a later device-control sprint.
          </p>
        </article>

        <article className="simple-card">
          <h2>Security</h2>
          <p>
            Session management and advanced account
            security will appear here.
          </p>
        </article>
      </section>
    </main>
  )
}

export default SettingsPage