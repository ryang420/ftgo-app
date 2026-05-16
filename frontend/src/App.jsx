function App() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(251,146,60,0.24),_transparent_28%),linear-gradient(135deg,_#111111_0%,_#1c1917_52%,_#292524_100%)] px-6 py-12 text-sand">
      <div className="mx-auto flex min-h-[calc(100vh-6rem)] max-w-6xl items-center">
        <section className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:gap-16">
          <div className="space-y-6">
            <p className="text-sm uppercase tracking-[0.35em] text-orange-300/80">
              FTGO Frontend
            </p>
            <h1 className="font-display text-5xl font-semibold leading-tight sm:text-6xl">
              React + Tailwind scaffold for the FTGO microservices workspace.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-stone-300">
              The frontend project is initialized as an isolated Vite app so we can
              add views, API clients, and local development wiring without touching
              the existing Python service layout.
            </p>
            <div className="flex flex-wrap gap-3 text-sm text-stone-200">
              <span className="rounded-full border border-white/15 bg-white/5 px-4 py-2">
                React 18
              </span>
              <span className="rounded-full border border-white/15 bg-white/5 px-4 py-2">
                Vite 5
              </span>
              <span className="rounded-full border border-white/15 bg-white/5 px-4 py-2">
                Tailwind CSS 3
              </span>
            </div>
          </div>

          <aside className="rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-card backdrop-blur">
            <p className="text-sm uppercase tracking-[0.3em] text-orange-200/75">
              Next steps
            </p>
            <ul className="mt-6 space-y-4 text-sm leading-7 text-stone-200">
              <li>Connect the API gateway as the first backend entrypoint.</li>
              <li>Add route structure for restaurant browsing and order flows.</li>
              <li>Introduce shared query hooks once the API contracts settle.</li>
            </ul>
          </aside>
        </section>
      </div>
    </main>
  );
}

export default App;
