import Link from "next/link";
import { AuthForm } from "@/components/AuthForm";

export default function RegisterPage() {
  return (
    <main className="mx-auto w-full max-w-md flex-1 px-4 py-12 sm:py-20">
      <h1 className="mb-2 text-2xl font-semibold text-foreground">Register</h1>
      <p className="mb-6 text-sm text-muted-foreground">
        New accounts start with 5 free Run Analysis credits.
      </p>
      <AuthForm mode="register" />
      <p className="mt-6 text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-accent hover:underline">
          Log in
        </Link>
      </p>
    </main>
  );
}
