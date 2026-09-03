import { ChatWidget } from "./components/ChatWidget";
import "./App.css";

function App() {
  const openChat = () => {
    const chatButton = document.querySelector(
      ".maiw-launcher"
    ) as HTMLButtonElement | null;

    chatButton?.click();
  };

  return (
    <main className="landing-page">
      <section className="hero-section">
        <div className="hero-badge">
          AI • SaaS • MVP Development
        </div>

        <h1>
          Build Smarter Products
          <span> with MoinSystems AI</span>
        </h1>

        <p className="hero-description">
          We build AI-powered SaaS platforms, MVPs, intelligent chatbots,
          automation workflows, and custom AI solutions for modern businesses.
        </p>

        <div className="hero-actions">
          <button
            className="primary-cta"
            onClick={openChat}
          >
            Start a Conversation
          </button>

          <a
            className="secondary-cta"
            href="#services"
          >
            Explore Services
          </a>
        </div>

        <div className="hero-trust">
          <span>AI Development</span>
          <span>SaaS Products</span>
          <span>MVP Development</span>
          <span>Automation</span>
        </div>
      </section>

      <section
        id="services"
        className="services-section"
      >
        <div className="section-heading">
          <span>What we build</span>

          <h2>
            AI solutions designed around real business needs
          </h2>

          <p>
            From idea validation to production-ready systems, our focus is
            practical AI that improves workflows, customer experiences, and
            digital products.
          </p>
        </div>

        <div className="service-grid">
          <article className="service-card">
            <div className="service-icon">
              ✦
            </div>

            <h3>
              AI Chatbots & Agents
            </h3>

            <p>
              Intelligent assistants for customer support, sales, internal
              operations, and business workflows.
            </p>
          </article>

          <article className="service-card">
            <div className="service-icon">
              ◈
            </div>

            <h3>
              AI-Powered SaaS
            </h3>

            <p>
              Modern SaaS products with authentication, dashboards, APIs,
              subscriptions, automation, and AI capabilities.
            </p>
          </article>

          <article className="service-card">
            <div className="service-icon">
              ↗
            </div>

            <h3>
              MVP Development
            </h3>

            <p>
              Turn startup ideas into functional MVPs with product planning,
              UI/UX, development, AI integration, testing, and deployment.
            </p>
          </article>

          <article className="service-card">
            <div className="service-icon">
              ⚡
            </div>

            <h3>
              AI Automation
            </h3>

            <p>
              Connect tools, data, and workflows to reduce repetitive work and
              improve operational efficiency.
            </p>
          </article>
        </div>
      </section>

      <section className="cta-section">
        <div>
          <span>
            Have an idea?
          </span>

          <h2>
            Tell us what you want to build.
          </h2>

          <p>
            Explore how MoinSystems AI can help with AI products,
            SaaS platforms, MVP development, intelligent assistants,
            and automation workflows.
          </p>
        </div>
      </section>

      <footer className="site-footer">
        <span>
          MoinSystems AI
        </span>

        <span>
          AI solutions for modern businesses.
        </span>
      </footer>

      <ChatWidget />
    </main>
  );
}

export default App;