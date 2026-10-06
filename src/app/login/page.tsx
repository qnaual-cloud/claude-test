import Link from "next/link";
import { AuthForm } from "@/components/AuthForm";

interface LoginPageProps {
  searchParams: Promise<{ returnTo?: string }>;
}

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const { returnTo } = await searchParams;
  const registerHref = returnTo ? `/register?returnTo=${encodeURIComponent(returnTo)}` : "/register";

  return (
    <main className="mx-auto w-full max-w-md flex-1 px-4 py-12 sm:py-20">
      <h1 className="mb-6 text-2xl font-semibold text-foreground">Log in</h1>
      <AuthForm mode="login" returnTo={returnTo} />
      <p className="mt-6 text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link href={registerHref} className="font-medium text-accent hover:underline">
          Register
        </Link>
      </p>
    </main>
  );
}
