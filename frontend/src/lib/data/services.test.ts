import { test, expect } from "vitest";
import { getServices, getService } from "./services";

test("services accessors return well-formed data", () => {
  const all = getServices();
  expect(all.length).toBeGreaterThan(0);
  expect(all[0]).toHaveProperty("slug");
  expect(all[0]).toHaveProperty("category");
  const slugs = new Set(all.map((s) => s.slug));
  expect(slugs.size).toBe(all.length);
  expect(getService("pacs-membership")).toBeDefined();
  expect(getService("nope")).toBeUndefined();
});
