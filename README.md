# ComfyUI Stacked FLUX Nunchaku LoRA Loaders

Ce dépôt contient un ensemble de nœuds personnalisés pour [ComfyUI](https://github.com/comfyanonymous/ComfyUI) qui permettent d'appliquer plusieurs LoRAs FLUX en série à un modèle, en utilisant la logique de chargement du pack [ComfyUI-nunchaku](https://github.com/mit-han-lab/ComfyUI-nunchaku).

Cela simplifie les workflows en réduisant le nombre de nœuds nécessaires pour appliquer une chaîne de LoRAs.

## Fonctionnalités

*   Charge et applique séquentiellement plusieurs LoRAs à des modèles FLUX.
*   Utilise le chargeur LoRA éprouvé du pack ComfyUI-nunchaku.
*   Interrupteur "Master Enabled" pour activer/désactiver rapidement tous les LoRAs du stack.
*   Interrupteurs individuels pour chaque LoRA dans le stack.
*   Proposé en variantes avec différents nombres de slots LoRA (x3, x5, x10).

## Nœuds Disponibles

*   **Stack FLUX Nunchaku LoRAs (x3)**: Permet d'empiler jusqu'à 3 LoRAs.
*   **Stack FLUX Nunchaku LoRAs (x5)**: Permet d'empiler jusqu'à 5 LoRAs.
*   **Stack FLUX Nunchaku LoRAs (x10)**: Permet d'empiler jusqu'à 10 LoRAs.

Chaque nœud se trouve dans la catégorie `loaders/nunchaku_stackers` après installation.

## Installation

1.  **Prérequis :**
    *   Assurez-vous d'avoir [ComfyUI](https://github.com/comfyanonymous/ComfyUI) installé et fonctionnel.
    *   Vous devez avoir le pack de nœuds [ComfyUI-nunchaku](https://github.com/mit-han-lab/ComfyUI-nunchaku) installé, car ce stacker dépend de son chargeur LoRA FLUX. Vous pouvez l'installer via le [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) ou manuellement.

2.  **Installation de ce pack de nœuds :**
    *   **Avec ComfyUI Manager (Recommandé) :**
        1.  Ouvrez le ComfyUI Manager.
        2.  Cliquez sur "Install Custom Nodes".
        3.  Recherchez `[Nom de votre dépôt GitHub, par ex. ComfyUI-FluxLoraStacker]` et installez-le.
        4.  Redémarrez ComfyUI.
    *   **Manuellement :**
        1.  Naviguez jusqu'au répertoire `ComfyUI/custom_nodes/`.
        2.  Clonez ce dépôt :
            ```bash
            git clone https://github.com/[VotreNomUtilisateurGitHub]/[NomDeVotreDepotGitHub].git MyFluxStackers
            ```
            (Remplacez `MyFluxStackers` par le nom de dossier souhaité si vous préférez, mais le `__init__.py` est configuré pour un dossier de ce nom ou un nom similaire qui contient `stacked_flux_nunchaku_lora_loader.py`.)
        3.  Redémarrez ComfyUI.

## Utilisation

1.  Chargez votre modèle FLUX de base.
2.  Ajoutez l'un des nœuds "Stack FLUX Nunchaku LoRAs (xN)" depuis le menu `loaders/nunchaku_stackers`.
3.  Connectez la sortie `MODEL` de votre chargeur de checkpoint à l'entrée `model` du nœud stacker.
4.  Utilisez l'interrupteur "Master Enabled" pour contrôler globalement l'application des LoRAs de ce stack.
5.  Pour chaque slot LoRA :
    *   Sélectionnez un `lora_name` dans la liste déroulante.
    *   Ajustez `lora_strength`.
    *   Utilisez l'interrupteur `enabled_i` pour activer ou désactiver ce LoRA spécifique dans la pile.
6.  Connectez la sortie `MODÈLE` du nœud stacker à l'entrée `model` de votre KSampler (ou d'un autre nœud LoRA stacker si vous enchaînez plusieurs stacks).

Les LoRAs sont appliqués dans l'ordre, du LoRA 1 au LoRA N.

Ce pack de nœuds personnalisés pour ComfyUI n'a pas de dépendances Python directes
Dépendances principales (à installer séparément dans ComfyUI) :
ComfyUI (https://github.com/comfyanonymous/ComfyUI)
ComfyUI-nunchaku (https://github.com/mit-han-lab/ComfyUI-nunchaku)

