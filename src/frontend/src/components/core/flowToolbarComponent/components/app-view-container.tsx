import { lazy, Suspense, useEffect } from "react";
import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import ShadTooltip from "@/components/common/shadTooltipComponent";
import { Button } from "@/components/ui/button";
import { useAppViewStore } from "@/stores/appViewStore";
import useFlowStore from "@/stores/flowStore";
import useFlowsManagerStore from "@/stores/flowsManagerStore";
import ViewModeToggle from "./view-mode-toggle";

// Lazy-load the heavy full-screen runner so it is only fetched the first time
// a user opens App view — keeps the main editor bundle lean.
const CustomIOModal = lazy(() =>
  import("@/customization/components/custom-new-modal").then((module) => ({
    default: module.CustomIOModal,
  })),
);

/**
 * The "App view" overlay — a full-screen, no-graph presentation of the current
 * flow, rendered via a portal to `document.body` so it reliably covers the
 * whole editor (escaping the ReactFlow canvas' stacking/overflow context).
 *
 * It reuses the exact runner shown on the shared `/playground/:id` page: the
 * IOModal in `isPlayground` (full-screen) mode. Crucially, that mode renders a
 * plain fill-parent `<div>` (not a self-contained modal), so it MUST be given a
 * full-screen container — which is what this component provides, mirroring the
 * PlaygroundPage wrapper. We do NOT pass `playgroundPage` because that flag is
 * for the public, unauthenticated page (it swaps to public build endpoints);
 * in-editor we want the normal authenticated run.
 */
export default function AppViewContainer() {
  const { t } = useTranslation();
  const open = useAppViewStore((state) => state.open);
  const setOpen = useAppViewStore((state) => state.setOpen);
  const hasIO = useFlowStore((state) => state.hasIO);
  const flowName = useFlowsManagerStore((state) => state.currentFlow?.name);

  // Close on Escape for a familiar "get me back to the canvas" gesture.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, setOpen]);

  // If the flow loses its input/output nodes, App view can no longer run — fall
  // back to the canvas instead of showing a broken runner.
  useEffect(() => {
    if (open && !hasIO) setOpen(false);
  }, [open, hasIO, setOpen]);

  // Reset when the editor unmounts (e.g. navigating to another flow) so a stale
  // "open" flag never resurfaces on the next flow.
  useEffect(() => {
    return () => setOpen(false);
  }, [setOpen]);

  if (!open || !hasIO) return null;

  return createPortal(
    <div
      data-testid="app-view-overlay"
      className="fixed inset-0 z-[60] flex flex-col bg-background"
    >
      <header className="flex h-12 shrink-0 items-center justify-between border-b border-border px-3">
        <div className="flex min-w-0 items-center gap-2">
          <ForwardedIconComponent
            name="AppWindow"
            className="h-4 w-4 shrink-0 text-muted-foreground"
          />
          <span className="truncate text-sm font-medium text-foreground">
            {flowName || t("misc.appView")}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <ViewModeToggle />
          <ShadTooltip content={t("misc.canvasViewTooltip")}>
            <Button
              unstyled
              size="icon"
              data-testid="app-view-close"
              aria-label={t("misc.canvasView")}
              className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground"
              onClick={() => setOpen(false)}
            >
              <ForwardedIconComponent name="X" className="h-4 w-4" />
            </Button>
          </ShadTooltip>
        </div>
      </header>

      <div className="flex min-h-0 flex-1 flex-col">
        <Suspense
          fallback={
            <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
              <ForwardedIconComponent
                name="Loader2"
                className="mr-2 h-4 w-4 animate-spin"
              />
              {t("misc.appView")}…
            </div>
          }
        >
          <CustomIOModal open={open} setOpen={setOpen} isPlayground>
            <></>
          </CustomIOModal>
        </Suspense>
      </div>
    </div>,
    document.body,
  );
}
