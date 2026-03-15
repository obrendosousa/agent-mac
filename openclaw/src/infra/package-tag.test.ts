import { describe, expect, it } from "vitest";
import { normalizePackageTagInput } from "./package-tag.js";

describe("normalizePackageTagInput", () => {
  const packageNames = ["chappie", "@chappie/plugin"] as const;

  it("returns null for blank inputs", () => {
    expect(normalizePackageTagInput(undefined, packageNames)).toBeNull();
    expect(normalizePackageTagInput("   ", packageNames)).toBeNull();
  });

  it("strips known package-name prefixes before returning the tag", () => {
    expect(normalizePackageTagInput("chappie@beta", packageNames)).toBe("beta");
    expect(normalizePackageTagInput("@chappie/plugin@2026.2.24", packageNames)).toBe("2026.2.24");
    expect(normalizePackageTagInput("chappie@   ", packageNames)).toBeNull();
  });

  it("treats exact known package names as an empty tag", () => {
    expect(normalizePackageTagInput("chappie", packageNames)).toBeNull();
    expect(normalizePackageTagInput(" @chappie/plugin ", packageNames)).toBeNull();
  });

  it("returns trimmed raw values when no package prefix matches", () => {
    expect(normalizePackageTagInput(" latest ", packageNames)).toBe("latest");
    expect(normalizePackageTagInput("@other/plugin@beta", packageNames)).toBe("@other/plugin@beta");
    expect(normalizePackageTagInput("chappieer@beta", packageNames)).toBe("chappieer@beta");
  });
});
