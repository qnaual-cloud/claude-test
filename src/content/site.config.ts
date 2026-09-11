/**
 * Site-wide branding and copy config.
 *
 * This file is safe to import from client components — it contains no
 * prompt templates or proprietary question logic, only branding/UI copy.
 * Edit these values (and redeploy) to change branding without touching
 * any component code.
 */

export const siteConfig = {
  productName: "AI Investment Research Assistant",
  tagline: "Tell us what you want to research. We'll build the prompt.",

  /**
   * Small, removable credit line shown in the footer during testing.
   * Change or delete this single value whenever branding changes.
   */
  footerCredit: "by DigitalAIbyNaual",

  earlyAccess: {
    heading:
      "Want early access to new research tools and features? Join the early-access list.",
    placeholder: "you@example.com",
    submitLabel: "Join the list",
    successMessage: "You're on the list — thanks for your interest.",
    errorMessage: "Something went wrong. Please try again.",
  },

  feedback: {
    prompt: "Was this prompt useful?",
    thanks: "Thanks for the feedback.",
  },

  whyItWorksLabel: "Why this prompt works",
} as const;
