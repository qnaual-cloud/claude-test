/**
 * Minimal, dependency-free renderer for a constrained markdown subset
 * (#/##/### headings, **bold**, "- "/"* " bullet lists, "1. " numbered
 * lists, blank-line-separated paragraphs). Parses into React elements
 * directly — never dangerouslySetInnerHTML — so there's no injection
 * risk from model output. Good enough for the prose research results
 * (Summary / Full Report / Memo); not a general markdown parser.
 */

function renderInline(text: string, keyPrefix: string) {
  const parts = text.split(/(\*\*.+?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
      return <strong key={`${keyPrefix}-${i}`}>{part.slice(2, -2)}</strong>;
    }
    return <span key={`${keyPrefix}-${i}`}>{part}</span>;
  });
}

function isListLine(line: string): "bullet" | "numbered" | null {
  if (/^[-*]\s+/.test(line)) return "bullet";
  if (/^\d+\.\s+/.test(line)) return "numbered";
  return null;
}

export function MarkdownLite({ text }: { text: string }) {
  const blocks = text.trim().split(/\n\s*\n/);

  return (
    <div className="flex flex-col gap-4">
      {blocks.map((block, blockIndex) => {
        const lines = block.split("\n").filter((l) => l.trim().length > 0);
        if (lines.length === 0) return null;

        const headingMatch = lines.length === 1 && lines[0].match(/^(#{1,3})\s+(.*)/);
        if (headingMatch) {
          const level = headingMatch[1].length;
          const content = renderInline(headingMatch[2], `h-${blockIndex}`);
          if (level === 1) {
            return (
              <h2 key={blockIndex} className="text-xl font-semibold text-foreground">
                {content}
              </h2>
            );
          }
          if (level === 2) {
            return (
              <h3 key={blockIndex} className="text-lg font-semibold text-foreground">
                {content}
              </h3>
            );
          }
          return (
            <h4 key={blockIndex} className="text-base font-semibold text-foreground">
              {content}
            </h4>
          );
        }

        const listKind = isListLine(lines[0]);
        if (listKind && lines.every((l) => isListLine(l) === listKind)) {
          const items = lines.map((l) => l.replace(/^[-*]\s+/, "").replace(/^\d+\.\s+/, ""));
          const Tag = listKind === "bullet" ? "ul" : "ol";
          return (
            <Tag
              key={blockIndex}
              className={`flex flex-col gap-1.5 pl-5 text-sm leading-relaxed text-foreground ${
                listKind === "bullet" ? "list-disc" : "list-decimal"
              }`}
            >
              {items.map((item, i) => (
                <li key={i}>{renderInline(item, `li-${blockIndex}-${i}`)}</li>
              ))}
            </Tag>
          );
        }

        return (
          <p key={blockIndex} className="text-sm leading-relaxed text-foreground">
            {renderInline(lines.join(" "), `p-${blockIndex}`)}
          </p>
        );
      })}
    </div>
  );
}
