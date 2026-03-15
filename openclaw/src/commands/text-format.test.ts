import { describe, expect, it } from "vitest";
import { shortenText } from "./text-format.js";

describe("shortenText", () => {
  it("returns original text when it fits", () => {
    expect(shortenText("chappie", 16)).toBe("chappie");
  });

  it("truncates and appends ellipsis when over limit", () => {
    expect(shortenText("chappie-status-output", 10)).toBe("chappie-…");
  });

  it("counts multi-byte characters correctly", () => {
    expect(shortenText("hello🙂world", 7)).toBe("hello🙂…");
  });
});
