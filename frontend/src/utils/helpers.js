import clsx from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges Tailwind classes conditionally.
 * - Uses `clsx` for conditional classes
 * - Uses `twMerge` to resolve conflicting Tailwind styles
 *
 * @param {...any} classes - Class names to merge
 * @returns {string} Merged class names
 */
export function cn(...classes) {
  return twMerge(clsx(classes));
}
