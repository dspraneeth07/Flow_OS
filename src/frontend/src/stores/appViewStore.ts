import { create } from "zustand";

/**
 * Drives the flow editor's "App view" (no-canvas mode). The toolbar toggle
 * flips `open`; the FlowPage-level overlay (`AppViewContainer`) reads it and
 * renders the full-screen runner. Kept as its own tiny store so the toggle and
 * the overlay — which live in different parts of the tree — stay in sync.
 */
interface AppViewState {
  open: boolean;
  setOpen: (open: boolean) => void;
}

export const useAppViewStore = create<AppViewState>((set) => ({
  open: false,
  setOpen: (open) => set({ open }),
}));
