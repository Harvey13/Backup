export interface FolderPair {
  source: string;
  destination: string;
  progress?: {
    current: number;
    total: number;
    status: 'pending' | 'syncing' | 'completed' | 'error';
  };
}

export interface SyncProgress {
  total: number;
  current: number;
  currentFile: string;
}