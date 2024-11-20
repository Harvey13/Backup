const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  selectFolder: () => ipcRenderer.invoke('select-folder'),
  saveMappings: (mappings) => ipcRenderer.invoke('save-mappings', mappings),
  loadMappings: () => ipcRenderer.invoke('load-mappings'),
  syncFolders: (mappings) => ipcRenderer.invoke('sync-folders', mappings),
  getSyncLog: () => ipcRenderer.invoke('get-sync-log'),
  clearSyncLog: () => ipcRenderer.invoke('clear-sync-log'),
  onProgressUpdate: (callback) => {
    ipcRenderer.on('sync-progress-update', (event, data) => callback(data));
  },
  removeProgressListener: () => {
    ipcRenderer.removeAllListeners('sync-progress-update');
  }
});