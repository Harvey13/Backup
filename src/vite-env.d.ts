/// <reference types="vite/client" />

interface Window {
  electron?: {
    selectFolder: () => Promise<string>;
    saveMappings: (mappings: FolderPair[]) => Promise<boolean>;
    loadMappings: () => Promise<FolderPair[]>;
    syncFolders: (mappings: FolderPair[]) => Promise<boolean>;
    getSyncLog: () => Promise<any[]>;
    clearSyncLog: () => Promise<boolean>;
    onProgressUpdate: (callback: (data: { mappingIndex: number, progress: any }) => void) => void;
    removeProgressListener: () => void;
  };
}