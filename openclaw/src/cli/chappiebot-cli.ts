import type { Command } from "commander";
import { formatDocsLink } from "../terminal/links.js";
import { theme } from "../terminal/theme.js";
import { registerQrCli } from "./qr-cli.js";

export function registerChappiebotCli(program: Command) {
  const chappiebot = program
    .command("chappiebot")
    .description("Legacy chappiebot command aliases")
    .addHelpText(
      "after",
      () =>
        `\n${theme.muted("Docs:")} ${formatDocsLink("/cli/chappiebot", "docs.chappie.ai/cli/chappiebot")}\n`,
    );
  registerQrCli(chappiebot);
}
