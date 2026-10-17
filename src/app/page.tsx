import Link from "next/link";
import { categories } from "@/content/categories";
import { siteConfig } from "@/content/site.config";
import { MembershipSection } from "@/components/MembershipSection";
import { BuyCreditsSection } from "@/components/BuyCreditsSection";
import { CurrencyProvider } from "@/lib/currencyContext";

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-12 sm:py-16">
      <div className="mb-10 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
          {siteConfig.productName}
        </h1>
        <p className="mt-2 text-lg font-semibold text-foreground sm:text-xl">
          {siteConfig.productHeadline}
        </p>
        <p className="mt-1 text-base font-medium text-muted-foreground sm:text-lg">
          {siteConfig.productSubtitle}
        </p>
        <Link
          href="/#professional"
          className="mt-3 inline-block text-sm text-muted-foreground hover:text-accent hover:underline"
        >
          For Professionals
        </Link>
      </div>

      <CurrencyProvider>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[280px_minmax(0,1fr)_320px] lg:items-start">
          {/* Center: introduction + Add Credits */}
          <section className="order-1 flex flex-col gap-10 lg:order-2">
            <div className="text-center lg:text-left">
              <h2 className="text-2xl font-semibold text-foreground">
                {siteConfig.homeIntro.heading}
              </h2>
              <p className="mt-3 text-base text-muted-foreground">{siteConfig.homeIntro.body}</p>
              <p className="mt-2 text-base font-medium text-foreground">
                {siteConfig.homeIntro.closing}
              </p>
            </div>
            <div id="buy-credits">
              <BuyCreditsSection />
            </div>
          </section>

          {/* Right: research tools */}
          <aside className="order-2 lg:order-3">
            <h2 className="mb-3 text-base font-semibold text-foreground">Research Tools</h2>
            <div className="flex flex-col gap-2.5">
              {categories.map((category) => (
                <Link
                  key={category.id}
                  href={`/research/${category.id}`}
                  className="min-h-11 rounded-xl border border-border bg-card px-4 py-3 transition-colors hover:border-accent"
                >
                  <p className="text-sm font-medium text-foreground">{category.label}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">{category.description}</p>
                </Link>
              ))}
            </div>
          </aside>

          {/* Left: membership */}
          <aside id="membership" className="order-3 lg:order-1">
            <MembershipSection />
          </aside>
        </div>
      </CurrencyProvider>
    </main>
  );
}
