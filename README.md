# Application de synchronisation Smartphone-PC

Cette application permet de synchroniser facilement les fichiers entre votre smartphone et votre PC.

## Fonctionnalités

- Interface graphique intuitive
- Configuration des dossiers source (smartphone) et destination (PC)
- Sauvegarde des configurations
- Vérification des doublons par CRC32
- Barre de progression pour chaque dossier
- Journal détaillé des opérations
- Gestion automatique des conflits de noms

## Installation

1. Téléchargez la dernière version depuis la section "Releases"
2. Décompressez l'archive
3. Lancez `SyncSmartphone.exe`

## Utilisation

1. Connectez votre smartphone au PC en mode "Transfert de fichiers" (MTP)
2. Dans l'application :
   - Configurez les dossiers source (smartphone) et destination (PC)
   - Cliquez sur "Synchroniser" pour démarrer la copie
   - Consultez le journal pour voir les détails des opérations

## Configuration

Les mappings de dossiers sont sauvegardés dans `%USERPROFILE%\.sync_smartphone\mappings.json`