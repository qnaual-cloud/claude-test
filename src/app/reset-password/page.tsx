import { ResetPasswordForm } from "@/components/ResetPasswordForm";

interface ResetPasswordPageProps {
  searchParams: Promise<{ returnTo?: string }>;
}

export default async function ResetPasswordPage({ searchParams }: ResetPasswordPageProps) {
  const { returnTo } = await searchParams;

  return (
    <main className="mx-auto w-full max-w-md flex-1 px-4 py-12 sm:py-20">
      <h1 className="mb-2 text-2xl font-semibold text-foreground">Set a new password</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Choose a new password for your account.
      </p>
      <ResetPasswordForm returnTo={returnTo} />
    </main>
  );
}
