import React from 'react';
import { FileText, X } from 'lucide-react';

interface LogEntry {
  type: 'renamed' | 'copied' | 'error';
  originalName?: string;
  newName?: string;
  name?: string;
  source: string;
  destination?: string;
  error?: string;
  timestamp: string;
}

interface SyncLogProps {
  isOpen: boolean;
  onClose: () => void;
  logs: LogEntry[];
}

const SyncLog: React.FC<SyncLogProps> = ({ isOpen, onClose, logs }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-3/4 max-w-4xl max-h-[80vh] flex flex-col">
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Journal de synchronisation
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-4 overflow-y-auto flex-1">
          {logs.length === 0 ? (
            <p className="text-gray-500 text-center">Aucune entrée dans le journal</p>
          ) : (
            <div className="space-y-2">
              {logs.map((log, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${
                    log.type === 'error' ? 'bg-red-50' :
                    log.type === 'renamed' ? 'bg-yellow-50' :
                    'bg-green-50'
                  }`}
                >
                  <div className="flex justify-between text-sm">
                    <span className={`font-medium ${
                      log.type === 'error' ? 'text-red-700' :
                      log.type === 'renamed' ? 'text-yellow-700' :
                      'text-green-700'
                    }`}>
                      {log.type === 'error' ? 'Erreur' :
                       log.type === 'renamed' ? 'Fichier renommé' :
                       'Fichier copié'}
                    </span>
                    <span className="text-gray-500">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>
                  
                  {log.type === 'error' ? (
                    <p className="mt-1 text-red-600">{log.error}</p>
                  ) : log.type === 'renamed' ? (
                    <>
                      <p className="mt-1">
                        Original: <span className="font-medium">{log.originalName}</span>
                      </p>
                      <p>
                        Nouveau: <span className="font-medium">{log.newName}</span>
                      </p>
                    </>
                  ) : (
                    <p className="mt-1">
                      Fichier: <span className="font-medium">{log.name}</span>
                    </p>
                  )}
                  
                  <p className="text-sm text-gray-500 mt-1">
                    Source: {log.source}
                  </p>
                  {log.destination && (
                    <p className="text-sm text-gray-500">
                      Destination: {log.destination}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SyncLog;