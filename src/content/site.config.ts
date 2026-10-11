/**
 * Site-wide branding and copy config.
 *
 * This file is safe to import from client components — it contains no
 * prompt templates or proprietary question logic, only branding/UI copy.
 * Edit these values (and redeploy) to change branding without touching
 * any component code.
 */

export const siteConfig = {
  productName: "PROFICERE",
  /** Shown directly under the PROFICERE title, above productSubtitle. */
  productHeadline: "From investment research to meeting-ready briefs.",
  productSubtitle: "AI Investment Research Assistant",
  tagline: "AI-powered investment research for investors, asset managers, and family offices.",

  /** The homepage hero copy, shown below the PROFICERE title. Edit freely. */
  homeIntro: {
    heading: "Speed. Simplicity. Focus.",
    body: "From company analysis and valuation to market insights, access focused, AI-powered research in one place, without writing a single prompt.",
    closing: "Do your research. Get straight to what matters.",
  },

  /**
   * The "Proficere Professional" enquiry card shown under the standard
   * membership plans. No price — this is a contact/enquiry CTA only, not
   * another paid subscription, and doesn't advertise any feature that
   * isn't built yet.
   * `email` is the one place to change the business contact address.
   */
  professionalContact: {
    heading: "PROFICERE PROFESSIONAL",
    audience: "For asset managers, family offices and investment teams.",
    body: "Need higher research volumes or AI workflows tailored to your investment research, reporting and client meetings?",
    buttonLabel: "Discuss Your Requirements",
    email: "support@digitalaibynaual.com",
    subject: "Proficere Professional Enquiry",
  },

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

  /** Shown when Run Analysis is attempted with 0 credits left. Edit freely. */
  outOfCredits: {
    title: "Continue Your Research",
    body: "You've used all of your available credits. Choose an option below to keep going.",
    buyCreditsLabel: "Add Credits",
    viewMembershipsLabel: "View Memberships",
  },

  /** Shown when "Generate Prompt" is attempted while logged out. Edit freely. */
  authRequired: {
    title: "Register or Log In to Continue",
    body: "Your research prompt is ready to generate — register or log in to reveal it and run the analysis. Your selections are saved, so you won't need to start over.",
    registerLabel: "Register",
    loginLabel: "Log In",
  },
} as const;
