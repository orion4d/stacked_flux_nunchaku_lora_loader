import folder_paths
import torch
import sys 

# --- DÉBUT SECTION IMPORTATION NUNCHAKU (via nodes.py de ComfyUI) ---
FluxNunchakuLoraLoader = None
nunchaku_node_found = False
try:
    import nodes 
    target_class_name_in_mappings = "NunchakuFluxLoraLoader" 
    if hasattr(nodes, 'NODE_CLASS_MAPPINGS') and target_class_name_in_mappings in nodes.NODE_CLASS_MAPPINGS:
        FluxNunchakuLoraLoader = nodes.NODE_CLASS_MAPPINGS[target_class_name_in_mappings]
        nunchaku_node_found = True
        # print(f"INFO (StackedLoader-Multi): RÉUSSI - NunchakuFluxLoraLoader trouvé via nodes.NODE_CLASS_MAPPINGS: {FluxNunchakuLoraLoader}")
    else:
        if hasattr(nodes, 'NODE_CLASS_MAPPINGS'):
            for k, v_class in nodes.NODE_CLASS_MAPPINGS.items():
                if v_class.__name__ == "NunchakuFluxLoraLoader": 
                    FluxNunchakuLoraLoader = v_class
                    nunchaku_node_found = True
                    # print(f"INFO (StackedLoader-Multi): RÉUSSI (Plan B) - NunchakuFluxLoraLoader trouvé par nom de classe sous la clé '{k}': {FluxNunchakuLoraLoader}")
                    break
            if not nunchaku_node_found:
                 print(f"AVERTISSEMENT (StackedLoader-Multi): NunchakuFluxLoraLoader non trouvé même en itérant par nom de classe.")
        else:
            print(f"AVERTISSEMENT (StackedLoader-Multi): '{target_class_name_in_mappings}' non trouvé dans nodes.NODE_CLASS_MAPPINGS (et NODE_CLASS_MAPPINGS n'existe pas).")
except ImportError:
    print("ERREUR (StackedLoader-Multi): Impossible d'importer 'nodes' de ComfyUI.")
except Exception as e:
    print(f"ERREUR (StackedLoader-Multi) lors de la tentative de récupération de NunchakuFluxLoraLoader via nodes.py: {e}")

if not nunchaku_node_found:
    print("ERREUR CRITIQUE (StackedLoader-Multi): NunchakuFluxLoraLoader n'a pas pu être obtenu. Les nœuds Stacked utiliseront une classe factice et ne fonctionneront PAS.")
    class FallbackFluxNunchakuLoraLoader:
        def load_lora(self, model, lora_name, lora_strength):
            # print("ERREUR (StackedLoader-Multi - Fallback): FallbackFluxNunchakuLoraLoader.load_lora appelée.")
            return (model,)
    FluxNunchakuLoraLoader = FallbackFluxNunchakuLoraLoader
# else:
    # print(f"INFO (StackedLoader-Multi): FluxNunchakuLoraLoader est prêt: {FluxNunchakuLoraLoader}")
# --- FIN SECTION IMPORTATION NUNCHAKU ---


# Classe de base pour la logique (pour éviter la duplication de code)
class BaseStackedFluxNunchakuLoRALoader:
    # MAX_LORAS sera défini par les sous-classes
    CATEGORY = "loaders/nunchaku_stackers" 
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "apply_stacked_loras"

    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "model": ("MODEL",),
                "master_enabled": ("BOOLEAN", {"default": True, "label_on": "All LoRAs Active", "label_off": "Bypass All LoRAs"}),
            }
        }
        lora_names_list = folder_paths.get_filename_list("loras")
        lora_names_with_none = ["None"] + lora_names_list
        effective_lora_list = lora_names_list if lora_names_list else ["None"]

        inputs["required"]["lora_name_1"] = (effective_lora_list, )
        inputs["required"]["lora_strength_1"] = ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01})
        inputs["required"]["enabled_1"] = ("BOOLEAN", {"default": True})

        inputs["optional"] = {} 
        # cls.MAX_LORAS doit être défini dans la sous-classe
        for i in range(2, cls.MAX_LORAS + 1): 
            inputs["optional"][f"lora_name_{i}"] = (lora_names_with_none, {"default": "None"})
            inputs["optional"][f"lora_strength_{i}"] = ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01})
            inputs["optional"][f"enabled_{i}"] = ("BOOLEAN", {"default": False})
        return inputs

    def _log_lora_list(self, model, stage_name=""):
        try:
            if hasattr(model, 'model') and \
               hasattr(model.model, 'diffusion_model') and \
               hasattr(model.model.diffusion_model, 'loras'):
                lora_info = model.model.diffusion_model.loras
                # print(f"DEBUG (StackedLoader {self.TITLE}) {stage_name}: Liste LoRAs: {lora_info}")
            # else:
                # print(f"DEBUG (StackedLoader {self.TITLE}) {stage_name}: Structure de modèle inattendue pour logger les LoRAs.")
        except Exception as e:
            print(f"DEBUG (StackedLoader {self.TITLE}) {stage_name}: Exception log loras: {e}")

    def apply_stacked_loras(self, model, master_enabled, **kwargs): 
        # print(f"\n--- DEBUG (StackedLoader {self.TITLE}): Début de apply_stacked_loras ---")
        # print(f"DEBUG (StackedLoader {self.TITLE}): Master Enabled: {master_enabled}")

        if not master_enabled:
            # print(f"INFO (StackedLoader {self.TITLE}): Master enable est OFF. Tous les LoRAs dans ce stack sont bypassés.")
            return (model,) 
        
        if not nunchaku_node_found or FluxNunchakuLoraLoader is None or (isinstance(FluxNunchakuLoraLoader, type) and FluxNunchakuLoraLoader.__name__ == 'FallbackFluxNunchakuLoraLoader'):
            print(f"ERREUR CRITIQUE (StackedLoader {self.TITLE}) dans apply_stacked_loras: Le vrai NunchakuLoader n'est pas disponible.")
            return (model,)
        
        try:
            nunchaku_loader_instance = FluxNunchakuLoraLoader()
            # print(f"DEBUG (StackedLoader {self.TITLE}): Instance de Nunchaku loader créée: {type(nunchaku_loader_instance)}")
        except Exception as e:
             print(f"ERREUR CRITIQUE (StackedLoader {self.TITLE}) lors de l'instanciation de FluxNunchakuLoraLoader: {e}")
             return (model,)

        current_model = model
        # print(f"DEBUG (StackedLoader {self.TITLE}): Modèle initial ID: {id(current_model)}")
        self._log_lora_list(current_model, "Initial")

        lora_name_1 = kwargs.get('lora_name_1')
        lora_strength_1 = kwargs.get('lora_strength_1', 1.0)
        enabled_1 = kwargs.get('enabled_1', True) 
        
        if enabled_1 and lora_name_1 and lora_name_1 != "None": 
            # print(f"\nDEBUG (StackedLoader {self.TITLE}): Application du LoRA 1:")
            # print(f"  Name: {lora_name_1}, Strength: {lora_strength_1}, Enabled: {enabled_1}")
            model_before_call_id = id(current_model)
            try:
                (current_model,) = nunchaku_loader_instance.load_lora(
                    model=current_model,
                    lora_name=lora_name_1,
                    lora_strength=lora_strength_1
                )
                # print(f"DEBUG (StackedLoader {self.TITLE}): LoRA 1 - Modèle après appel ID: {id(current_model)}. Modèle avant ID: {model_before_call_id}. Identiques: {id(current_model) == model_before_call_id}")
                self._log_lora_list(current_model, "Après LoRA 1")
            except Exception as e:
                print(f"ERREUR (StackedLoader {self.TITLE}) lors de l'appel à load_lora pour LoRA 1 ({lora_name_1}): {e}")
        # elif lora_name_1 and lora_name_1 != "None" and not enabled_1:
             # print(f"DEBUG (StackedLoader {self.TITLE}): Skipping FLUX LoRA 1 (individually disabled): {lora_name_1}")

        # La boucle utilise self.MAX_LORAS qui est spécifique à chaque sous-classe
        for i in range(2, self.MAX_LORAS + 1): 
            lora_name = kwargs.get(f'lora_name_{i}')
            current_lora_strength = kwargs.get(f'lora_strength_{i}', 1.0)
            enabled = kwargs.get(f'enabled_{i}', False) 

            if enabled and lora_name and lora_name != "None": 
                # print(f"\nDEBUG (StackedLoader {self.TITLE}): Application du LoRA {i}:")
                # print(f"  Name: {lora_name}, Strength: {current_lora_strength}, Enabled: {enabled}")
                model_before_call_id = id(current_model)
                try:
                    (current_model,) = nunchaku_loader_instance.load_lora(
                        model=current_model, 
                        lora_name=lora_name,
                        lora_strength=current_lora_strength
                    )
                    # print(f"DEBUG (StackedLoader {self.TITLE}): LoRA {i} - Modèle après appel ID: {id(current_model)}. Modèle avant ID: {model_before_call_id}. Identiques: {id(current_model) == model_before_call_id}")
                    self._log_lora_list(current_model, f"Après LoRA {i}")
                except Exception as e:
                    print(f"ERREUR (StackedLoader {self.TITLE}) lors de l'appel à load_lora pour LoRA {i} ({lora_name}): {e}")
            # elif lora_name and lora_name != "None" and not enabled:
                 # print(f"DEBUG (StackedLoader {self.TITLE}): Skipping FLUX LoRA {i} (individually disabled): {lora_name}")

        # print(f"--- DEBUG (StackedLoader {self.TITLE}): Fin de apply_stacked_loras ---")
        return (current_model,)

# Variante pour 3 LoRAs
class StackedFluxNunchakuLoRALoader3(BaseStackedFluxNunchakuLoRALoader):
    MAX_LORAS = 3
    TITLE = "Stack FLUX Nunchaku LoRAs (x3)"

# Variante pour 5 LoRAs
class StackedFluxNunchakuLoRALoader5(BaseStackedFluxNunchakuLoRALoader):
    MAX_LORAS = 5
    TITLE = "Stack FLUX Nunchaku LoRAs (x5)"

# Variante pour 10 LoRAs
class StackedFluxNunchakuLoRALoader10(BaseStackedFluxNunchakuLoRALoader):
    MAX_LORAS = 10
    TITLE = "Stack FLUX Nunchaku LoRAs (x10)"


NODE_CLASS_MAPPINGS = {
    "StackedFluxNunchakuLoRALoader3": StackedFluxNunchakuLoRALoader3,
    "StackedFluxNunchakuLoRALoader5": StackedFluxNunchakuLoRALoader5,
    "StackedFluxNunchakuLoRALoader10": StackedFluxNunchakuLoRALoader10,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "StackedFluxNunchakuLoRALoader3": "Stack FLUX Nunchaku LoRAs (x3)",
    "StackedFluxNunchakuLoRALoader5": "Stack FLUX Nunchaku LoRAs (x5)",
    "StackedFluxNunchakuLoRALoader10": "Stack FLUX Nunchaku LoRAs (x10)",
}

print("INFO (StackedLoader-Multi): Chargement des nœuds Stacked FLUX Nunchaku LoRA Loader (variantes x3, x5, x10).")
# J'ai commenté la plupart des print de débogage pour alléger la console.
# Vous pouvez les décommenter si besoin.