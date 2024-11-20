import React from 'react';
import { Folder, ArrowRight } from 'lucide-react';
import { FolderPair } from '../types';

interface FolderMappingProps {
  mapping: FolderPair;
  onChange: (newMapping: FolderPair) => void;
  onRemove: () => void;
}

const FolderMapping: React.FC<FolderMappingProps> = ({ mapping, onChange, onRemove }) => {
  const handleSourceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({
      ...mapping,
      source: e.target.value
    });
  };

  const handleDestinationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({
      ...mapping,
      destination: e.target.value
    });
  };

  const getProgressColor = () => {
    switch (mapping.progress?.status) {
      case 'completed':
        return 'bg-green-600';
      case 'error':
        return 'bg-red-600';
      case 'syncing':
        return 'bg-indigo-600';
      default:
        return 'bg-gray-200';
    }
  };

  return (
    <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Dossier source (Smartphone)
          </label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={mapping.source}
              onChange={handleSourceChange}
              className="flex-1 p-2 border border-gray-300 rounded-md"
              placeholder="Chemin du dossier source"
            />
            <button
              onClick={() => {
                const input = document.createElement('input');
                input.type = 'file';
                input.webkitdirectory = true;
                input.onchange = (e) => {
                  const files = (e.target as HTMLInputElement).files;
                  if (files && files.length > 0) {
                    onChange({
                      ...mapping,
                      source: files[0].webkitRelativePath.split('/')[0]
                    });
                  }
                };
                input.click();
              }}
              className="p-2 bg-indigo-100 text-indigo-600 rounded-md hover:bg-indigo-200 transition-colors"
            >
              <Folder className="w-5 h-5" />
            </button>
          </div>
        </div>

        <ArrowRight className="w-6 h-6 text-gray-400 flex-shrink-0" />

        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Dossier destination (PC)
          </label>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={mapping.destination}
              onChange={handleDestinationChange}
              className="flex-1 p-2 border border-gray-300 rounded-md"
              placeholder="Chemin du dossier destination"
            />
            <button
              onClick={() => {
                const input = document.createElement('input');
                input.type = 'file';
                input.webkitdirectory = true;
                input.onchange = (e) => {
                  const files = (e.target as HTMLInputElement).files;
                  if (files && files.length > 0) {
                    onChange({
                      ...mapping,
                      destination: files[0].webkitRelativePath.split('/')[0]
                    });
                  }
                };
                input.click();
              }}
              className="p-2 bg-indigo-100 text-indigo-600 rounded-md hover:bg-indigo-200 transition-colors"
            >
              <Folder className="w-5 h-5" />
            </button>
          </div>
        </div>

        <button
          onClick={onRemove}
          className="p-2 text-red-600 hover:bg-red-50 rounded-md transition-colors"
        >
          ×
        </button>
      </div>

      {/* Progress Bar */}
      {mapping.progress && (
        <div className="mt-4">
          <div className="flex justify-between text-sm mb-1">
            <span className={`font-medium ${
              mapping.progress.status === 'error' ? 'text-red-600' :
              mapping.progress.status === 'completed' ? 'text-green-600' :
              mapping.progress.status === 'syncing' ? 'text-indigo-600' :
              'text-gray-600'
            }`}>
              {mapping.progress.status === 'error' ? 'Erreur' :
               mapping.progress.status === 'completed' ? 'Terminé' :
               mapping.progress.status === 'syncing' ? 'Synchronisation...' :
               'En attente'}
            </span>
            <span className="text-gray-600">
              {mapping.progress.current}/{mapping.progress.total} fichiers
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`${getProgressColor()} h-2 rounded-full transition-all duration-300`}
              style={{
                width: `${(mapping.progress.current / mapping.progress.total) * 100}%`
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default FolderMapping;