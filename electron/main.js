const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const Store = require('electron-store');
const fs = require('fs/promises');
const crypto = require('crypto');

const store = new Store();
let syncLog = [];
let mainWindow;

async function calculateCRC32(filePath) {
  try {
    const fileBuffer = await fs.readFile(filePath);
    return crypto.createHash('crc32').update(fileBuffer).digest('hex');
  } catch (error) {
    console.error('Error calculating CRC:', error);
    return null;
  }
}

async function getUniqueFileName(basePath, originalName) {
  let counter = 1;
  let fileName = originalName;
  let filePath = path.join(basePath, fileName);

  while (await fs.access(filePath).then(() => true).catch(() => false)) {
    const ext = path.extname(originalName);
    const name = path.basename(originalName, ext);
    fileName = `${name}_${String(counter).padStart(3, '0')}${ext}`;
    filePath = path.join(basePath, fileName);
    counter++;
  }

  return fileName;
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

function updateProgress(mappingIndex, current, total, status = 'syncing') {
  if (mainWindow) {
    mainWindow.webContents.send('sync-progress-update', {
      mappingIndex,
      progress: { current, total, status }
    });
  }
}

ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory']
  });
  return result.filePaths[0];
});

ipcMain.handle('save-mappings', async (event, mappings) => {
  store.set('folderMappings', mappings);
  return true;
});

ipcMain.handle('load-mappings', async () => {
  return store.get('folderMappings');
});

ipcMain.handle('get-sync-log', () => {
  return syncLog;
});

ipcMain.handle('clear-sync-log', () => {
  syncLog = [];
  return true;
});

ipcMain.handle('sync-folders', async (event, mappings) => {
  syncLog = [];
  
  for (let mappingIndex = 0; mappingIndex < mappings.length; mappingIndex++) {
    const mapping = mappings[mappingIndex];
    try {
      await fs.mkdir(mapping.destination, { recursive: true });
      const files = await fs.readdir(mapping.source);
      
      // Initialiser la progression
      updateProgress(mappingIndex, 0, files.length, 'syncing');
      
      for (let fileIndex = 0; fileIndex < files.length; fileIndex++) {
        const file = files[fileIndex];
        const sourcePath = path.join(mapping.source, file);
        const destPath = path.join(mapping.destination, file);
        
        try {
          // Vérifier si le fichier existe déjà
          const fileExists = await fs.access(destPath).then(() => true).catch(() => false);
          
          if (fileExists) {
            // Calculer les CRC
            const sourceCRC = await calculateCRC32(sourcePath);
            const destCRC = await calculateCRC32(destPath);
            
            if (sourceCRC !== destCRC) {
              // Les fichiers sont différents, créer une nouvelle version
              const newFileName = await getUniqueFileName(mapping.destination, file);
              const newDestPath = path.join(mapping.destination, newFileName);
              await fs.copyFile(sourcePath, newDestPath);
              
              syncLog.push({
                type: 'renamed',
                originalName: file,
                newName: newFileName,
                source: sourcePath,
                destination: newDestPath,
                timestamp: new Date().toISOString()
              });
            }
          } else {
            // Le fichier n'existe pas, copie simple
            await fs.copyFile(sourcePath, destPath);
            syncLog.push({
              type: 'copied',
              name: file,
              source: sourcePath,
              destination: destPath,
              timestamp: new Date().toISOString()
            });
          }
          
          // Mettre à jour la progression
          updateProgress(mappingIndex, fileIndex + 1, files.length, 'syncing');
        } catch (error) {
          console.error(`Error processing file ${file}:`, error);
          syncLog.push({
            type: 'error',
            source: sourcePath,
            error: error.message,
            timestamp: new Date().toISOString()
          });
        }
      }
      
      // Marquer comme terminé
      updateProgress(mappingIndex, files.length, files.length, 'completed');
    } catch (error) {
      console.error(`Error syncing ${mapping.source}:`, error);
      syncLog.push({
        type: 'error',
        source: mapping.source,
        error: error.message,
        timestamp: new Date().toISOString()
      });
      updateProgress(mappingIndex, 0, 1, 'error');
    }
  }
  return true;
});