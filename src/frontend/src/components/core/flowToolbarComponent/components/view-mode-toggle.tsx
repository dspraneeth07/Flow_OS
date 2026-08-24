import { useTranslation } from "react-i18next";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import ShadTooltip from "@/components/common/shadTooltipComponent";
import { track } from "@/customization/utils/analytics";
import { useAppViewStore } from "@/stores/appViewStore";
import useFlowStore from "@/stores/flowStore";
import { cn } from "@/utils/utils";

/**
 * View-mode switcher for the flow editor: "Canvas" (the visual graph builder —
 * advanced mode) and "App" (a clean, no-graph mini-app that runs the flow as a
 * chat or a form). Purely presentational — it drives `useAppViewStore`, and the
 * FlowPage-level `AppViewContainer` renders the actual full-screen runner. This
 * same control is shown both in the toolbar and inside the App view header, so
 * users can flip back and forth from either place.
 *
 * App view is only available once the flow has an input/output node (`hasIO`),
 * mirroring the Prayog button's requirement.
 */
export default function ViewModeToggle() {
  const { t } = useTranslation();
  const hasIO = useFlowStore((state) => state.hasIO);
  const open = useAppViewStore((state) => state.open);
  const setOpen = useAppViewStore((state) => state.setOpen);

  const segmentClass = (active: boolean) =>
    cn(
      "flex h-7 items-center gap-1.5 rounded px-2.5 text-mmd font-normal transition-colors",
      active
        ? "bg-background text-foreground shadow-sm"
        : "text-muted-foreground hover:text-foreground",
    );

  const openApp = () => {
    setOpen(true);
    track("App View Opened");
  };

  return (
    <div
      role="tablist"
      aria-label={t("misc.appView")}
      className="flex items-center gap-0.5 rounded-md bg-muted p-0.5"
    >
      <ShadTooltip content={t("misc.canvasViewTooltip")}>
        <button
          type="button"
          role="tab"
          aria-selected={!open}
          data-testid="view-mode-canvas"
          className={segmentClass(!open)}
          onClick={() => setOpen(false)}
        >
          <ForwardedIconComponent name="Workflow" className="h-4 w-4" />
          {t("misc.canvasView")}
        </button>
      </ShadTooltip>

      {hasIO ? (
        <ShadTooltip content={t("misc.appViewTooltip")}>
          <button
            type="button"
            role="tab"
            aria-selected={open}
            data-testid="view-mode-app"
            className={segmentClass(open)}
            onClick={openApp}
          >
            <ForwardedIconComponent name="AppWindow" className="h-4 w-4" />
            {t("misc.appView")}
          </button>
        </ShadTooltip>
      ) : (
        <ShadTooltip content={t("misc.appViewNeedsIO")}>
          <div
            aria-disabled="true"
            data-testid="view-mode-app-disabled"
            className={cn(segmentClass(false), "cursor-not-allowed opacity-50")}
          >
            <ForwardedIconComponent name="AppWindow" className="h-4 w-4" />
            {t("misc.appView")}
          </div>
        </ShadTooltip>
      )}
    </div>
  );
}
