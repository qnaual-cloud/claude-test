import Link from "next/link";
import { categories } from "@/content/categories";
import { siteConfig } from "@/content/site.config";

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-12 sm:py-20">
      <div className="mb-10 text-center">
        <h1 className="text-3xl font-semibold text-foreground sm:text-4xl">
          {siteConfig.productName}
        </h1>
        <p className="mt-3 text-base text-muted-foreground">{siteConfig.tagline}</p>
      </div>

      <div className="flex flex-col gap-3">
        {categories.map((category) => (
          <Link
            key={category.id}
            href={`/research/${category.id}`}
            className="min-h-11 rounded-xl border border-border bg-card px-5 py-4 transition-colors hover:border-accent"
          >
            <p className="text-base font-medium text-foreground">{category.label}</p>
            <p className="mt-1 text-sm text-muted-foreground">{category.description}</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
