import { describe, expect, it } from "vitest";
import "./test-helpers/fast-core-tools.js";
import { createChappieTools } from "./chappie-tools.js";

function readToolByName() {
  return new Map(createChappieTools().map((tool) => [tool.name, tool]));
}

describe("createChappieTools owner authorization", () => {
  it("marks owner-only core tools in raw registration", () => {
    const tools = readToolByName();
    expect(tools.get("cron")?.ownerOnly).toBe(true);
    expect(tools.get("gateway")?.ownerOnly).toBe(true);
    expect(tools.get("nodes")?.ownerOnly).toBe(true);
  });

  it("keeps canvas non-owner-only in raw registration", () => {
    const tools = readToolByName();
    expect(tools.get("canvas")).toBeDefined();
    expect(tools.get("canvas")?.ownerOnly).not.toBe(true);
  });
});
