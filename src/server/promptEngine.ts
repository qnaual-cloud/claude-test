/**
 * SERVER-ONLY. Assembles a finished prompt from a category id + user
 * answers. Imported only by API routes — never by client components.
 *
 * This is deterministic template assembly, not an AI/LLM call: there is
 * no model API cost to generate a prompt in v1.
 */

import { getCategoryById, type EntityFieldConfig, type EntityItem } from "@/content/categories";
import { categoryTemplates, SHARED_CONSTRAINTS, SHARED_FOLLOW_UP } from "./promptTemplates";

export type { EntityItem };

export interface GeneratePromptInput {
  categoryId: string;
  entity: string | EntityItem[];
  roleId?: string;
  chipIds: string[];
  outputFormatId: string;
}

export interface GeneratePromptResult {
  prompt: string;
  whyItWorks: string[];
}

export class PromptValidationError extends Error {}

const MAX_FIELD_LENGTH = 120;

function cleanText(value: string, label: string): string {
  const trimmed = value.trim();
  if (!trimmed) throw new PromptValidationError(`${label} is required.`);
  if (trimmed.length > MAX_FIELD_LENGTH) {
    throw new PromptValidationError(`${label} is too long.`);
  }
  return trimmed;
}

function buildSubject(
  entityConfig: EntityFieldConfig,
  entity: GeneratePromptInput["entity"]
): string {
  if (entityConfig.kind === "single") {
    if (typeof entity !== "string") {
      throw new PromptValidationError("Expected a single entity value.");
    }
    return cleanText(entity, entityConfig.label);
  }

  if (!Array.isArray(entity)) {
    throw new PromptValidationError("Expected a list of entities.");
  }
  if (entity.length < entityConfig.minItems || entity.length > entityConfig.maxItems) {
    throw new PromptValidationError(
      `${entityConfig.label} must have between ${entityConfig.minItems} and ${entityConfig.maxItems} entries.`
    );
  }

  return entity
    .map((item) => {
      const name = cleanText(item.name, entityConfig.itemLabel);
      if (entityConfig.hasWeight && item.weight?.trim()) {
        const weight = cleanText(item.weight, `${entityConfig.itemLabel} weight`);
        return `${name} (${weight})`;
      }
      return name;
    })
    .join(", ");
}

export function generatePrompt(input: GeneratePromptInput): GeneratePromptResult {
  const category = getCategoryById(input.categoryId);
  if (!category) throw new PromptValidationError("Unknown research category.");

  const template = categoryTemplates[input.categoryId];
  if (!template) throw new PromptValidationError("This category is not yet available.");

  const subject = buildSubject(category.entity, input.entity);

  // Role/objective step, only validated when the category defines one.
  let roleContextLine: string | undefined;
  if (category.roleStep) {
    if (!input.roleId) {
      throw new PromptValidationError("Please select an option before continuing.");
    }
    const validOption = category.roleStep.options.some((o) => o.id === input.roleId);
    if (!validOption) throw new PromptValidationError("Invalid selection.");
    roleContextLine = template.roleContext?.[input.roleId];
  }

  // Focus chips.
  const validChipIds = new Set(category.focusChips.options.map((o) => o.id));
  const chipIds = Array.from(new Set(input.chipIds));
  if (
    chipIds.length < category.focusChips.minSelect ||
    chipIds.length > category.focusChips.maxSelect
  ) {
    throw new PromptValidationError(
      `Please select between ${category.focusChips.minSelect} and ${category.focusChips.maxSelect} focus areas.`
    );
  }
  for (const id of chipIds) {
    if (!validChipIds.has(id)) throw new PromptValidationError("Invalid focus area selected.");
  }
  const requiredAnalysis = chipIds.map((id) => template.chipInstructions[id]).filter(Boolean);

  // Output format.
  const validFormat = category.outputFormats.options.some((o) => o.id === input.outputFormatId);
  if (!validFormat) throw new PromptValidationError("Please select an output format.");
  const outputInstruction = template.outputFormatInstructions[input.outputFormatId];

  const sections: string[] = [];
  sections.push(`Role: ${template.role}`);
  sections.push(`Objective: ${template.objective(subject)}`);
  if (roleContextLine) sections.push(`Context: ${roleContextLine}`);
  sections.push(
    `Required analysis:\n${requiredAnalysis.map((line) => `- ${line}`).join("\n")}`
  );
  sections.push(`Output format: ${outputInstruction}`);
  sections.push(`Constraints:\n${SHARED_CONSTRAINTS.map((line) => `- ${line}`).join("\n")}`);
  sections.push(SHARED_FOLLOW_UP);

  const prompt = sections.join("\n\n");

  const whyItWorks = [...template.whyItWorksBase];

  return { prompt, whyItWorks };
}
