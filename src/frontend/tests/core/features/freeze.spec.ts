import { expect, test } from "../../fixtures";
import { addFlowToTestOnEmptyFlowOS } from "../../utils/add-flow-to-test-on-empty-flowos";
import { addLegacyComponents } from "../../utils/add-legacy-components";
import { awaitBootstrapTest } from "../../utils/await-bootstrap-test";

import { TEXTS } from "../../utils/constants/texts";

test(
  "user must be able to freeze a component",
  { tag: ["@release", "@workspace", "@components"] },

  async ({ page }) => {
    await awaitBootstrapTest(page);

    const firstRunFlowOS = await page
      .getByTestId("empty-project-description")
      .count();

    if (firstRunFlowOS > 0) {
      await addFlowToTestOnEmptyFlowOS(page);
    }

    await page.getByTestId("blank-flow").click();

    await addLegacyComponents(page);

    await page.getByTestId("sidebar-search-input").click();
    await page.getByTestId("sidebar-search-input").fill(TEXTS.searchTextInput);
    await page.waitForSelector('[data-testid="input_outputText Input"]', {
      timeout: 1000,
    });

    await page
      .getByTestId("input_outputText Input")
      .dragTo(page.locator('//*[@id="react-flow-id"]'), {
        targetPosition: { x: 100, y: 100 },
      });

    await page.getByTestId("textarea_str_input_value").fill("hello world");

    await page.getByTestId("div-generic-node").getByRole("button").click();

    await page.waitForSelector('[data-testid="div-generic-node"]', {
      timeout: 10000,
    });

    await page.getByTestId("output-inspection-output text-textinput").click();

    const firstOutputText = await page
      .getByPlaceholder(TEXTS.placeholderEmpty)
      .textContent();

    expect(firstOutputText).toBe("hello world");

    await page.getByText(TEXTS.close).last().click();

    await page.getByTestId("textarea_str_input_value").fill("goodbye world");

    await page.getByTestId("div-generic-node").click();

    await page.waitForSelector('[data-testid="freeze-all-button-modal"]', {
      timeout: 1000,
    });

    await page.getByTestId("freeze-all-button-modal").click();

    await page.waitForSelector('[data-testid="icon-FreezeAll"]', {
      timeout: 1000,
    });
    await page.locator('//*[@id="icon-FreezeAll"]');

    await expect(page.getByTestId("icon-FreezeAll")).toBeVisible();

    await page.waitForTimeout(5000);

    await page.keyboard.press("Escape");

    await page.getByTestId("div-generic-node").getByRole("button").click();

    await page.getByTestId("output-inspection-output text-textinput").click();

    const secondOutputText = await page
      .getByPlaceholder(TEXTS.placeholderEmpty)
      .textContent();

    expect(secondOutputText).toBe("goodbye world");
  },
);
