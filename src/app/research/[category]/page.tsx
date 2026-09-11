import { notFound } from "next/navigation";
import { getCategoryById } from "@/content/categories";
import { ResearchWizard } from "@/components/ResearchWizard";

interface PageProps {
  params: Promise<{ category: string }>;
}

export default async function CategoryPage({ params }: PageProps) {
  const { category: categoryId } = await params;
  const category = getCategoryById(categoryId);
  if (!category) notFound();

  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-10 sm:py-16">
      <ResearchWizard category={category} />
    </main>
  );
}
