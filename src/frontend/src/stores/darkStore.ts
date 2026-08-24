import { create } from "zustand";
import type { DarkStoreType } from "../types/zustand/dark";

export const useDarkStore = create<DarkStoreType>((set) => ({
  dark: (() => {
    const stored = window.localStorage.getItem("isDark");
    if (stored !== null) return JSON.parse(stored);
    return true;
  })(),
  version: "",
  latestVersion: "",
  refreshLatestVersion: (v: string) => {
    set(() => ({ latestVersion: v }));
  },
  setDark: (dark) => {
    set(() => ({ dark: dark }));
    window.localStorage.setItem("isDark", dark.toString());
  },
  refreshVersion: (v) => {
    set(() => ({ version: v }));
  },
}));
