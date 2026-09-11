import { siteConfig } from "@/content/site.config";

export function Footer() {
  return (
    <footer className="mt-auto py-6 text-center">
      <p className="text-[11px] text-muted-foreground/70">{siteConfig.footerCredit}</p>
    </footer>
  );
}
