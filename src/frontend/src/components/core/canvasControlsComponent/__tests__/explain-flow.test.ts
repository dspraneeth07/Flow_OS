import type { AllNodeType, EdgeType } from "@/types/flow";
import { explainFlow } from "../explain-flow";

/** Minimal node factory — only the fields explainFlow reads. */
function node(
  id: string,
  type: string,
  displayName: string,
  extra: {
    baseClasses?: string[];
    isInput?: boolean;
    isOutput?: boolean;
    toolMode?: boolean;
    nodeType?: "genericNode" | "noteNode";
  } = {},
): AllNodeType {
  return {
    id,
    type: extra.nodeType ?? "genericNode",
    position: { x: 0, y: 0 },
    data: {
      id,
      type,
      node: {
        display_name: displayName,
        description: "",
        template: {},
        documentation: "",
        base_classes: extra.baseClasses ?? [],
        is_input: extra.isInput,
        is_output: extra.isOutput,
        tool_mode: extra.toolMode,
      },
    },
  } as unknown as AllNodeType;
}

function edge(source: string, target: string): EdgeType {
  return { id: `${source}->${target}`, source, target } as EdgeType;
}

describe("explainFlow", () => {
  it("reports an empty flow", () => {
    const result = explainFlow([], []);
    expect(result.isEmpty).toBe(true);
    expect(result.steps).toHaveLength(0);
    expect(result.summary).toMatch(/empty/i);
  });

  it("explains a basic chat → model → output flow in order", () => {
    const nodes = [
      node("out", "ChatOutput", "Chat Output", { isOutput: true }),
      node("model", "OpenAIModel", "OpenAI", {
        baseClasses: ["LanguageModel"],
      }),
      node("in", "ChatInput", "Chat Input", { isInput: true }),
    ];
    const edges = [edge("in", "model"), edge("model", "out")];

    const result = explainFlow(nodes, edges);

    expect(result.isEmpty).toBe(false);
    expect(result.componentCount).toBe(3);
    expect(result.connectionCount).toBe(2);
    // Topologically ordered from the input, not array order.
    expect(result.steps.map((s) => s.name)).toEqual([
      "Chat Input",
      "OpenAI",
      "Chat Output",
    ]);
    expect(result.summary).toContain("takes the message you send");
    expect(result.summary).toContain("OpenAI AI model");
    expect(result.summary).toContain("gives you the result");
  });

  it("describes a RAG flow as searching documents", () => {
    const nodes = [
      node("in", "ChatInput", "Chat Input", { isInput: true }),
      node("vs", "AstraDB", "Astra DB", { baseClasses: ["VectorStore"] }),
      node("model", "AnthropicModel", "Anthropic", {
        baseClasses: ["LanguageModel"],
      }),
      node("out", "ChatOutput", "Chat Output", { isOutput: true }),
    ];
    const result = explainFlow(nodes, [
      edge("in", "vs"),
      edge("vs", "model"),
      edge("model", "out"),
    ]);
    expect(result.summary).toContain("searches your documents");
  });

  it("prefers the agent phrasing over a plain model", () => {
    const nodes = [
      node("in", "ChatInput", "Chat Input", { isInput: true }),
      node("agent", "Agent", "Agent"),
      node("out", "ChatOutput", "Chat Output", { isOutput: true }),
    ];
    const result = explainFlow(nodes, [
      edge("in", "agent"),
      edge("agent", "out"),
    ]);
    expect(result.summary).toContain("AI agent");
  });

  it("ignores sticky notes", () => {
    const nodes = [
      node("in", "ChatInput", "Chat Input", { isInput: true }),
      node("note", "note", "Note", { nodeType: "noteNode" }),
    ];
    const result = explainFlow(nodes, []);
    expect(result.componentCount).toBe(1);
    expect(result.steps).toHaveLength(1);
  });

  it("never drops nodes even with a cycle", () => {
    const nodes = [node("a", "Loop", "Loop A"), node("b", "Loop", "Loop B")];
    const result = explainFlow(nodes, [edge("a", "b"), edge("b", "a")]);
    expect(result.steps).toHaveLength(2);
  });
});
