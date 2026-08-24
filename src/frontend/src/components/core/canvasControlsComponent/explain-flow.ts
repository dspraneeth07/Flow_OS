import type { AllNodeType, EdgeType, NodeDataType } from "@/types/flow";

/**
 * Turns a flow graph into a plain-English explanation a non-technical user
 * can understand — a one-line summary plus an ordered, "first this, then
 * that" list of what each component does.
 *
 * This is intentionally deterministic and fully client-side: it reads the
 * nodes/edges already in the store and never calls a model or the backend.
 * That means the "Explain this flow" button works instantly for everyone,
 * even before any model provider (API key) is configured.
 */

export interface ExplainStep {
  id: string;
  /** The component's display name, e.g. "Chat Input". */
  name: string;
  /** One friendly sentence describing what this step does. */
  detail: string;
}

export interface FlowExplanation {
  isEmpty: boolean;
  summary: string;
  steps: ExplainStep[];
  componentCount: number;
  connectionCount: number;
}

type Role =
  | "input"
  | "output"
  | "model"
  | "agent"
  | "prompt"
  | "vectorstore"
  | "embeddings"
  | "memory"
  | "data"
  | "tool"
  | "logic"
  | "other";

interface Classification {
  role: Role;
  detail: string;
}

/**
 * Map a single component to a role + a plain-English sentence. Detection is
 * heuristic (component type + display name + base classes) so it degrades
 * gracefully for components it has never seen (falls back to "other").
 * Order matters: more specific checks come before broader ones.
 */
function classifyNode(data: NodeDataType): Classification {
  const apiNode = data.node;
  const name = apiNode?.display_name || data.type || "Component";
  const baseClasses = (apiNode?.base_classes ?? []).join(" ").toLowerCase();
  const hay = `${data.type ?? ""} ${name} ${baseClasses}`.toLowerCase();
  const isInput = apiNode?.is_input === true;
  const isOutput = apiNode?.is_output === true;
  const toolMode = apiNode?.tool_mode === true;

  if (isOutput || /chat ?output|text ?output/.test(hay)) {
    return { role: "output", detail: "Sends the final result back to you." };
  }
  if (isInput || /chat ?input|text ?input/.test(hay)) {
    return {
      role: "input",
      detail: "Receives the message or text you send in.",
    };
  }
  if (/agent/.test(hay)) {
    return {
      role: "agent",
      detail:
        "Runs an AI agent that can reason and use tools to complete the task.",
    };
  }
  if (/prompt/.test(hay)) {
    return {
      role: "prompt",
      detail: "Builds the instructions (the prompt) that guide the AI.",
    };
  }
  if (
    baseClasses.includes("vectorstore") ||
    /vector ?store|astra|chroma|pinecone|qdrant|milvus|weaviate|pgvector|faiss|retriev/.test(
      hay,
    )
  ) {
    return {
      role: "vectorstore",
      detail: "Searches your stored documents for relevant information.",
    };
  }
  if (/embed/.test(hay)) {
    return {
      role: "embeddings",
      detail: "Turns text into numbers so it can be searched by meaning.",
    };
  }
  if (/memory|chat history|message history/.test(hay)) {
    return {
      role: "memory",
      detail: "Remembers earlier parts of the conversation.",
    };
  }
  if (
    baseClasses.includes("languagemodel") ||
    /language ?model|openai|anthropic|claude|\bgpt\b|gemini|groq|ollama|mistral|cohere|\bllm\b|chat ?model|bedrock|vertex/.test(
      hay,
    )
  ) {
    return {
      role: "model",
      detail: `Sends the text to the ${name} AI model to generate a response.`,
    };
  }
  if (
    toolMode ||
    /search|calculator|wikipedia|tavily|serp|\btool\b|api ?request|\burl\b/.test(
      hay,
    )
  ) {
    return {
      role: "tool",
      detail: `Provides a tool the AI can use: ${name}.`,
    };
  }
  if (
    /file|directory|csv|json|pdf|document|loader|ingest|webhook|\bsql\b|database/.test(
      hay,
    )
  ) {
    return {
      role: "data",
      detail: `Loads data (${name}) into the flow.`,
    };
  }
  if (/router|condition|if.?else|loop|listen|notify|branch|switch/.test(hay)) {
    return {
      role: "logic",
      detail: "Decides which path the flow should take.",
    };
  }
  return { role: "other", detail: `Processes the data (${name}).` };
}

/**
 * Order components the way data actually flows through them (sources first,
 * following the connections) using a stable topological sort. Ties and any
 * leftover nodes from cycles fall back to their original order so nothing is
 * ever dropped.
 */
function orderNodeIds(nodes: AllNodeType[], edges: EdgeType[]): string[] {
  const ids = nodes.map((n) => n.id);
  const idSet = new Set(ids);
  const origIndex = new Map(ids.map((id, i) => [id, i]));
  const indegree = new Map(ids.map((id) => [id, 0]));
  const adjacency = new Map<string, string[]>(ids.map((id) => [id, []]));

  for (const edge of edges) {
    if (idSet.has(edge.source) && idSet.has(edge.target)) {
      adjacency.get(edge.source)?.push(edge.target);
      indegree.set(edge.target, (indegree.get(edge.target) ?? 0) + 1);
    }
  }

  const bySourceOrder = (a: string, b: string) =>
    (origIndex.get(a) ?? 0) - (origIndex.get(b) ?? 0);

  const queue = ids.filter((id) => (indegree.get(id) ?? 0) === 0);
  const order: string[] = [];
  const placed = new Set<string>();

  while (queue.length > 0) {
    queue.sort(bySourceOrder);
    const id = queue.shift() as string;
    if (placed.has(id)) continue;
    order.push(id);
    placed.add(id);
    for (const next of adjacency.get(id) ?? []) {
      indegree.set(next, (indegree.get(next) ?? 0) - 1);
      if ((indegree.get(next) ?? 0) === 0 && !placed.has(next)) {
        queue.push(next);
      }
    }
  }

  // Append anything left behind by a cycle, preserving original order.
  for (const id of ids) {
    if (!placed.has(id)) order.push(id);
  }
  return order;
}

/** Join clauses into one readable sentence fragment. */
function joinClauses(clauses: string[]): string {
  return clauses.join(", ");
}

/**
 * Build the full plain-English explanation for a flow.
 */
export function explainFlow(
  nodes: AllNodeType[],
  edges: EdgeType[],
): FlowExplanation {
  // Sticky notes are annotations, not part of the data flow.
  const components = nodes.filter((n) => n.type !== "noteNode");

  if (components.length === 0) {
    return {
      isEmpty: true,
      summary:
        "This flow is empty. Add components from the sidebar to get started.",
      steps: [],
      componentCount: 0,
      connectionCount: 0,
    };
  }

  const byId = new Map(components.map((n) => [n.id, n]));
  const validConnections = edges.filter(
    (e) => byId.has(e.source) && byId.has(e.target),
  ).length;

  const order = orderNodeIds(components, edges);

  const roles = new Set<Role>();
  let modelName: string | null = null;
  const steps: ExplainStep[] = [];

  for (const id of order) {
    const node = byId.get(id);
    if (!node) continue;
    const data = node.data as NodeDataType;
    const name = data.node?.display_name || data.type || "Component";
    const classification = classifyNode(data);
    roles.add(classification.role);
    if (classification.role === "model" && modelName === null) {
      modelName = name;
    }
    steps.push({ id, name, detail: classification.detail });
  }

  // Compose a single summary sentence from the roles that are present.
  const clauses: string[] = [];
  if (roles.has("input")) clauses.push("takes the message you send");
  if (roles.has("data")) {
    clauses.push(roles.has("input") ? "reads your data" : "loads your data");
  }
  if (roles.has("vectorstore")) {
    clauses.push("searches your documents for relevant information");
  }
  if (roles.has("agent")) {
    clauses.push("runs an AI agent that can use tools to work out an answer");
  } else if (roles.has("model")) {
    clauses.push(`sends it to the ${modelName} AI model`);
  } else if (roles.has("prompt")) {
    clauses.push("builds a prompt for the AI");
  }
  if (roles.has("output")) clauses.push("and gives you the result");

  const summary =
    clauses.length > 0
      ? `This flow ${joinClauses(clauses)}.`
      : `This flow connects ${components.length} component${
          components.length === 1 ? "" : "s"
        } together.`;

  return {
    isEmpty: false,
    summary,
    steps,
    componentCount: components.length,
    connectionCount: validConnections,
  };
}
