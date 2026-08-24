import { useMemo, useState } from "react";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import useFlowStore from "@/stores/flowStore";
import { explainFlow } from "./explain-flow";

/**
 * "Explain this flow in plain English" — a canvas-controls button that opens
 * a popover describing, in non-technical language, what the current flow
 * does. Fully client-side and deterministic, so it works instantly for
 * everyone (no model provider / API key required).
 */
const ExplainFlowButton = () => {
  const [open, setOpen] = useState(false);
  const nodes = useFlowStore((state) => state.nodes);
  const edges = useFlowStore((state) => state.edges);

  // Recompute only while the popover is open — keeps canvas dragging cheap.
  const explanation = useMemo(() => {
    if (!open) return null;
    return explainFlow(nodes, edges);
  }, [open, nodes, edges]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          unstyled
          size="icon"
          data-testid="explain-flow-button"
          aria-label="Explain this flow in plain English"
          title="Explain this flow in plain English"
          className="group flex h-8 w-8 items-center justify-center rounded-md hover:bg-muted"
        >
          <ForwardedIconComponent
            name="ScrollText"
            className={`h-[18px] w-[18px] transition-colors ${
              open
                ? "text-foreground"
                : "text-muted-foreground group-hover:text-foreground"
            }`}
          />
        </Button>
      </PopoverTrigger>
      <PopoverContent
        side="top"
        align="center"
        sideOffset={12}
        data-testid="explain-flow-popover"
        className="w-[23rem] overflow-hidden p-0"
      >
        <div className="flex items-center gap-2 border-b border-border px-4 py-3">
          <ForwardedIconComponent
            name="ScrollText"
            className="h-4 w-4 text-muted-foreground"
          />
          <span className="text-sm font-semibold text-foreground">
            What this flow does
          </span>
        </div>

        {explanation && (
          <div className="max-h-[24rem] overflow-y-auto px-4 py-3">
            <p className="text-sm leading-relaxed text-foreground">
              {explanation.summary}
            </p>

            {explanation.steps.length > 0 && (
              <>
                <div className="mt-3 mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Step by step
                </div>
                <ol className="flex flex-col gap-2.5">
                  {explanation.steps.map((step, index) => (
                    <li key={step.id} className="flex gap-2.5">
                      <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-muted text-[11px] font-semibold text-muted-foreground">
                        {index + 1}
                      </span>
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-foreground">
                          {step.name}
                        </span>
                        <span className="text-xs leading-snug text-muted-foreground">
                          {step.detail}
                        </span>
                      </div>
                    </li>
                  ))}
                </ol>

                <div className="mt-3 border-t border-border pt-2 text-xs text-muted-foreground">
                  {explanation.componentCount} component
                  {explanation.componentCount === 1 ? "" : "s"} ·{" "}
                  {explanation.connectionCount} connection
                  {explanation.connectionCount === 1 ? "" : "s"}
                </div>
              </>
            )}
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
};

export default ExplainFlowButton;
