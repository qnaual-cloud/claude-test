import Link from "next/link";
import { ForgotPasswordForm } from "@/components/ForgotPasswordForm";

interface ForgotPasswordPageProps {
  searchParams: Promise<{ returnTo?: string }>;
}

export default async function ForgotPasswordPage({ searchParams }: ForgotPasswordPageProps) {
  const { returnTo } = await searchParams;
  const loginHref = returnTo ? `/login?returnTo=${encodeURIComponent(returnTo)}` : "/login";

  return (
    <main className="mx-auto w-full max-w-md flex-1 px-4 py-12 sm:py-20">
      <h1 className="mb-2 text-2xl font-semibold text-foreground">Reset your password</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        Enter the email on your account and we&apos;ll send you a link to reset your password.
      </p>
      <ForgotPasswordForm returnTo={returnTo} />
      <p className="mt-6 text-sm text-muted-foreground">
        <Link href={loginHref} className="font-medium text-accent hover:underline">
          Back to log in
        </Link>
      </p>
    </main>
  );
}
