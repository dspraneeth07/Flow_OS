export type DarkStoreType = {
  dark: boolean;
  version: string;
  latestVersion: string;
  setDark: (dark: boolean) => void;
  refreshVersion: (v: string) => void;
  refreshLatestVersion: (v: string) => void;
};
