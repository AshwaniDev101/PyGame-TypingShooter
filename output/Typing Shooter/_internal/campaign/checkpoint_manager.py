import json
import os
import datetime
import pygame

from config.loader import Loader

class CheckpointManager:
    # Manages game checkpoints by saving, loading, and listing them in a JSON file.
    def __init__(self, file_name="campaign/checkpoints.json"):
        # Store both the relative filename and its absolute path.
        self.file_name = file_name
        self.file_path = Loader.resource_path(file_name)

    def save_checkpoint(self, checkpoint_id, player):
        # Build checkpoint data using the player's current state.
        checkpoint_data = {
            "id": checkpoint_id,
            "states": {
                "player_x": player.rect.x,
                "player_health": player.health,
                "player_ammo": player.ammo,
            },
            "timestamp": datetime.datetime.now().isoformat()
        }

        existing_checkpoints = {}

        # Load existing checkpoints if the file exists and is not empty.
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            try:
                checkpoints_list = Loader.load_json(self.file_name)
                # Convert the list of checkpoints to a dict keyed by id.
                for cp in checkpoints_list:
                    cp_id = cp.get("id")
                    try:
                        cp_id = int(cp_id)
                    except (ValueError, TypeError):
                        pass
                    existing_checkpoints[cp_id] = cp
            except (json.JSONDecodeError, KeyError):
                print("Warning: Checkpoint file is corrupted. Resetting checkpoints.")
                existing_checkpoints = {}

        # Ensure the checkpoint id is an int if possible.
        try:
            checkpoint_id = int(checkpoint_id)
        except (ValueError, TypeError):
            pass
        checkpoint_data["id"] = checkpoint_id

        # Insert or update the checkpoint.
        existing_checkpoints[checkpoint_id] = checkpoint_data

        # Save the updated checkpoints back to the file.
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(list(existing_checkpoints.values()), f, indent=4)
        print(f"Checkpoint '{checkpoint_data.get('id')}' saved successfully!")

    def json_file_load_checkpoints(self):
        # Loads and returns a list of all saved checkpoints.
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            try:
                return Loader.load_json(self.file_name)
            except json.JSONDecodeError:
                print("Error: Checkpoint file is corrupted. Returning an empty list.")
                return []
        return []

    def load_checkpoint_by_id(self, checkpoint_id):
        # Loads a specific checkpoint by its id.
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            print("No checkpoints found.")
            return None

        try:
            checkpoints = Loader.load_json(self.file_name)
            try:
                checkpoint_id = int(checkpoint_id)
            except (ValueError, TypeError):
                pass

            for checkpoint in checkpoints:
                cp_id = checkpoint.get("id")
                try:
                    cp_id = int(cp_id)
                except (ValueError, TypeError):
                    pass
                if cp_id == checkpoint_id:
                    return checkpoint

            print(f"Checkpoint '{checkpoint_id}' not found.")
            return None

        except json.JSONDecodeError:
            print("Error: Checkpoint file is corrupted.")
            return None

    # def build_checkpoint(self, json_object, player):
    #     # Constructs a checkpoint dictionary from a given JSON object and player state.
    #     checkpoint_id = json_object.get("id", 0)
    #     try:
    #         checkpoint_id = int(checkpoint_id)
    #     except (ValueError, TypeError):
    #         pass
    #
    #     return {
    #         "id": checkpoint_id,
    #         "states": {
    #             "player_position": {"x": player.rect.x, "y": player.rect.y},
    #             "player_health": player.health,
    #             "player_ammo": player.ammo,
    #             "player_score": getattr(player, "score", 0)
    #         },
    #         "timestamp": pygame.time.get_ticks()
    #     }

    def get_list_of_unlocked_checkpoints(self):
        checkpoints = self.json_file_load_checkpoints()
        checkpoint_list = []


        for cp in checkpoints:

            checkpoint_list.append(int(cp.get('id')))


        return  checkpoint_list

    def delete_all_except_checkpoint_1(self):
        # Load existing checkpoints
        checkpoints = self.json_file_load_checkpoints()

        # Filter only checkpoint with id = 1
        filtered_checkpoints = [cp for cp in checkpoints if cp.get("id") == 1]

        # Save back only the remaining checkpoint
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(filtered_checkpoints, f, indent=4)

        print("Deleted all checkpoints except checkpoint with id = 1.")

    def print_checkpoints(self):
        # Prints a summary of all saved checkpoints.
        checkpoints = self.json_file_load_checkpoints()

        if not checkpoints:
            print("No checkpoints found!")
            return

        for cp in checkpoints:
            states = cp.get("states", {})
            print(f"Checkpoint {cp.get('id')}\n"
                  f"  States: {states}\n"
                  f"  Timestamp: {cp.get('timestamp')}\n")


