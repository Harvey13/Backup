import React, { useState, useEffect } from 'react';
import { Smartphone, FolderSync, Save, FileText, Plus, Play, RotateCw } from 'lucide-react';
import { FolderPair, SyncProgress } from './types';
import FolderMapping from './components/FolderMapping';
import SyncLog from './components/SyncLog';
import { calculateCRC32 } from './utils/fileUtils';

const defaultMappings: FolderPair[] = [
  {
    source: 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\DCIM\\Camera',
    destination: 'D:\\Images\\e-port huawei appareil photo N°4'
  },
  {
    source: 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\Pictures\\Screenshots',
    destination: 'D:\\Images\\e-port huawei capture d\'écran'
  },
  {
    source: 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\WhatsApp\\Media\\WhatsApp Images',
    destination: 'D:\\Images\\e-port huawei a WhatsApp images N°4'
  },
  {
    source: 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\WhatsApp\\Media\\WhatsApp Video',
    destination: 'D:\\Vidéos\\e-port huawei whatsApp vidéos'
  },
  {
    source: 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\Download',
    destination: 'D:\\Images\\e-port huawei aTéléchargements N°2'
  },
  {
    source: 'Ce PC\\HUAWEI Y7 2019\\Mémoire de stockage interne\\Pictures',
    destination: 'D:\\Images\\e-port huawei messages textos'
  },
  {
    source: 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\Pictures\\autres',
    destination: 'D:\\Images\\e-port huawei Autres'
  },
  {
    source: 'Ce PC\\HUAWEI Y7 2019\\Carte SD\\Pictures\\nikie',
    destination: 'D:\\Images\\e-port huawei Nikie'
  }
];

function App() {
  const [folderMappings, setFolderMappings] = useState<FolderPair[]>(() => {
    const saved = localStorage.getItem('folderMappings');
    return saved ? JSON.parse(saved) : defaultMappings;
  });
  
  const [isSyncing, setIsSyncing] = useState(false);
  const [isLogOpen, setIsLogOpen] = useState(false);
  const [syncLogs, setSyncLogs] = useState<any[]>([]);

  useEffect(() => {
    localStorage.setItem('folderMappings', JSON.stringify(folderMappings));
  }, [folderMappings]);

  const handleSaveMappings = () => {
    localStorage.setItem('folderMappings', JSON.stringify(folderMappings));
    alert('Mappings sauvegardés avec succès !');
  };

  const handleSync = async () => {
    setIsSyncing(true);
    const newLogs = [];

    try {
      for (let i = 0; i < folderMappings.length; i++) {
        const mapping = folderMappings[i];
        const sourceHandle = await window.showDirectoryPicker({
          startIn: 'desktop',
        });
        const destHandle = await window.showDirectoryPicker({
          startIn: 'desktop',
        });

        // Mettre à jour le statut
        setFolderMappings(prev => {
          const updated = [...prev];
          updated[i] = {
            ...mapping,
            progress: { current: 0, total: 0, status: 'syncing' }
          };
          return updated;
        });

        // Lister les fichiers source
        const sourceFiles = [];
        for await (const entry of sourceHandle.values()) {
          if (entry.kind === 'file') {
            sourceFiles.push(entry);
          }
        }

        // Mettre à jour le total
        setFolderMappings(prev => {
          const updated = [...prev];
          updated[i] = {
            ...mapping,
            progress: { current: 0, total: sourceFiles.length, status: 'syncing' }
          };
          return updated;
        });

        // Synchroniser les fichiers
        for (let fileIndex = 0; fileIndex < sourceFiles.length; fileIndex++) {
          const file = sourceFiles[fileIndex];
          try {
            const sourceFile = await file.getFile();
            const destFile = await destHandle.getFileHandle(file.name, { create: true });
            
            // Vérifier si le fichier existe déjà
            let shouldCopy = true;
            try {
              const existingFile = await destFile.getFile();
              const sourceCRC = await calculateCRC32(sourceFile);
              const destCRC = await calculateCRC32(existingFile);
              
              if (sourceCRC === destCRC) {
                shouldCopy = false;
              } else {
                // Créer une nouvelle version avec suffixe
                let counter = 1;
                let newName = file.name;
                while (true) {
                  try {
                    const [name, ext] = file.name.split('.');
                    newName = `${name}_${String(counter).padStart(3, '0')}.${ext}`;
                    await destHandle.getFileHandle(newName, { create: false });
                    counter++;
                  } catch {
                    break;
                  }
                }
                const newFile = await destHandle.getFileHandle(newName, { create: true });
                const writable = await newFile.createWritable();
                await writable.write(sourceFile);
                await writable.close();
                
                newLogs.push({
                  type: 'renamed',
                  originalName: file.name,
                  newName,
                  source: mapping.source,
                  destination: mapping.destination,
                  timestamp: new Date().toISOString()
                });
              }
            } catch {
              // Le fichier n'existe pas, on le copie
              const writable = await destFile.createWritable();
              await writable.write(sourceFile);
              await writable.close();
              
              newLogs.push({
                type: 'copied',
                name: file.name,
                source: mapping.source,
                destination: mapping.destination,
                timestamp: new Date().toISOString()
              });
            }

            // Mettre à jour la progression
            setFolderMappings(prev => {
              const updated = [...prev];
              updated[i] = {
                ...mapping,
                progress: {
                  current: fileIndex + 1,
                  total: sourceFiles.length,
                  status: 'syncing'
                }
              };
              return updated;
            });
          } catch (error) {
            newLogs.push({
              type: 'error',
              file: file.name,
              error: error.message,
              source: mapping.source,
              timestamp: new Date().toISOString()
            });
          }
        }

        // Marquer comme terminé
        setFolderMappings(prev => {
          const updated = [...prev];
          updated[i] = {
            ...mapping,
            progress: {
              current: sourceFiles.length,
              total: sourceFiles.length,
              status: 'completed'
            }
          };
          return updated;
        });
      }
    } catch (error) {
      console.error('Sync error:', error);
      newLogs.push({
        type: 'error',
        error: error.message,
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsSyncing(false);
      setSyncLogs(prev => [...prev, ...newLogs]);
    }
  };

  const addMapping = () => {
    setFolderMappings([...folderMappings, { source: '', destination: '' }]);
  };

  const updateMapping = (index: number, newMapping: FolderPair) => {
    const newMappings = [...folderMappings];
    newMappings[index] = newMapping;
    setFolderMappings(newMappings);
  };

  const removeMapping = (index: number) => {
    setFolderMappings(folderMappings.filter((_, i) => i !== index));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-6">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <Smartphone className="w-8 h-8 text-indigo-600" />
            <span>Synchronisation Smartphone</span>
          </h1>
          <p className="text-gray-600 mt-2">
            Configurez la synchronisation des dossiers entre votre smartphone et votre PC
          </p>
        </header>

        <div className="space-y-6">
          {folderMappings.map((mapping, index) => (
            <FolderMapping
              key={index}
              mapping={mapping}
              onChange={(newMapping) => updateMapping(index, newMapping)}
              onRemove={() => removeMapping(index)}
            />
          ))}
          
          <button
            onClick={addMapping}
            className="w-full p-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-indigo-500 hover:text-indigo-500 transition-colors flex items-center justify-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Ajouter un mapping
          </button>
        </div>

        <div className="mt-8 flex gap-4">
          <button
            onClick={handleSaveMappings}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Save className="w-5 h-5" />
            Sauvegarder les mappings
          </button>
          
          <button
            onClick={handleSync}
            disabled={isSyncing}
            className={`flex items-center gap-2 px-4 py-2 ${
              isSyncing ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'
            } text-white rounded-lg transition-colors`}
          >
            {isSyncing ? (
              <>
                <RotateCw className="w-5 h-5 animate-spin" />
                Synchronisation...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Lancer la synchronisation
              </>
            )}
          </button>

          <button
            onClick={() => setIsLogOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <FileText className="w-5 h-5" />
            Voir le journal
          </button>
        </div>
      </div>

      <SyncLog
        isOpen={isLogOpen}
        onClose={() => setIsLogOpen(false)}
        logs={syncLogs}
      />
    </div>
  );
}

export default App;