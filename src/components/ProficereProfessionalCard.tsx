import { siteConfig } from "@/content/site.config";

/**
 * A plain enquiry CTA, not a priced membership tier — deliberately no
 * price and no "unlimited" promise. Opens the visitor's email client via
 * `mailto:`; the recipient address is centralized in site.config.ts.
 */
export function ProficereProfessionalCard() {
  const { heading, audience, body, buttonLabel, email, subject } = siteConfig.professionalContact;
  const mailtoHref = `mailto:${email}?subject=${encodeURIComponent(subject)}`;

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-border bg-card p-5">
      <div>
        <p className="text-sm font-semibold tracking-wide text-foreground uppercase">{heading}</p>
        <p className="mt-1 text-sm text-muted-foreground">{audience}</p>
        <p className="mt-2 text-sm text-foreground">{body}</p>
      </div>
      <a
        href={mailtoHref}
        className="inline-flex min-h-9 w-fit items-center justify-center rounded-lg border border-accent px-4 py-2 text-sm font-medium text-accent hover:bg-accent/10"
      >
        {buttonLabel}
      </a>
    </div>
  );
}
