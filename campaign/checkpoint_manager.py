import json
import os
import datetime

import pygame

from config.loader import Loader


class CheckpointManager:
    """
    Manages game checkpoints by saving, loading, and listing them in a JSON file.
    Prevents duplicate checkpoint IDs and ensures efficient file handling.
    """

    def __init__(self, file_name="campaign/checkpoints.json"):
        """
        Initializes the CheckpointManager with a persistent file path.

        :param file_name: The filename where checkpoints are stored (default: "campaign/checkpoints.json").
        """
        self.file_path = Loader.resource_path(file_name)  # Convert to absolute path using the resource loader.

    def save_checkpoint(self, checkpoint_data):
        """
        Saves a new checkpoint or updates an existing one if the ID matches.

        - Reads existing data **only if necessary** to check for duplicate IDs.
        - Updates a checkpoint if it already exists; otherwise, appends a new one.
        - Ensures data integrity and avoids unnecessary file reads/writes.

        :param checkpoint_data: Dictionary containing checkpoint details.
        """

        existing_checkpoints = {}  # Dictionary to store checkpoints by ID

        # Check if the file exists and is not empty before attempting to read
        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    checkpoints_list = json.load(f)  # Load existing checkpoint list

                    # Convert list of checkpoints to a dictionary {id: checkpoint_data}
                    existing_checkpoints = {cp["id"]: cp for cp in checkpoints_list}

            except (json.JSONDecodeError, KeyError):
                print("Warning: Checkpoint file is corrupted. Resetting checkpoints.")
                existing_checkpoints = {}  # Reset if the file is corrupted

        # Add or update the checkpoint
        checkpoint_data["timestamp"] = datetime.datetime.now().isoformat()  # Add current timestamp
        existing_checkpoints[checkpoint_data["id"]] = checkpoint_data  # Insert/update checkpoint by ID

        # Save the updated checkpoints back to the file
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(list(existing_checkpoints.values()), f, indent=4)  # type:ignore
            # Convert dict back to list for storage
        print(f"Checkpoint '{checkpoint_data.get('id')}' saved successfully!")  # Confirmation message

    def load_checkpoints(self):
        """
        Loads and returns a list of all saved checkpoints.

        - Checks if the file exists before attempting to read.
        - Handles corrupted files gracefully by returning an empty list.

        :return: List of checkpoint dictionaries.
        """
        if os.path.exists(self.file_path) and os.path.getsize(
                self.file_path) > 0:  # Ensure the file exists and is not empty
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)  # Load and return checkpoint data
            except json.JSONDecodeError:
                print("Error: Checkpoint file is corrupted. Returning an empty list.")
                return []  # Return an empty list if JSON is invalid
        return []  # Return an empty list if the file doesn't exist or is empty

    def load_checkpoint_by_id(self, checkpoint_id):
        """
        Loads a specific checkpoint by its ID.

        - Reads the file only if necessary.
        - Searches for the checkpoint efficiently.
        - Handles missing or corrupted files gracefully.

        :param checkpoint_id: The ID of the checkpoint to load.
        :return: Dictionary containing the checkpoint data, or None if not found.
        """
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            print("No checkpoints found.")
            return None  # No checkpoint file or it's empty

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                checkpoints = json.load(f)  # Load all checkpoints

            # Search for the checkpoint with the given ID
            for checkpoint in checkpoints:
                if checkpoint.get("id") == checkpoint_id:
                    return checkpoint  # Return the found checkpoint

            print(f"Checkpoint '{checkpoint_id}' not found.")
            return None  # No matching checkpoint found

        except json.JSONDecodeError:
            print("Error: Checkpoint file is corrupted.")
            return None  # Handle corrupted file safely

    def build_checkpoint(self, json_object, player):
        """
        Constructs a checkpoint dictionary from a given JSON object.

        - Extracts ID, title, and description.
        - Captures the current player state (position, health, ammo, score).
        - Adds a timestamp for tracking.

        :param player:
        :param json_object: The JSON object containing checkpoint data.
        :return: A structured checkpoint dictionary.
        """
        return {
            "id": json_object.get("id", "default_checkpoint"),
            "title": json_object.get("title", "Checkpoint"),
            "description": json_object.get("description", ""),
            "states": {
                "player_position": {"x": player.rect.x, "y": player.rect.y},
                "player_health": player.health,
                "player_ammo": player.ammo,
                "player_score": getattr(player, "score", 0)
            },
            "timestamp": pygame.time.get_ticks()
        }

    def print_checkpoints(self):
        """
        Prints a summary of all saved checkpoints in a readable format.

        - Calls `load_checkpoints()` to retrieve the saved data.
        - Displays relevant checkpoint information including position, health, ammo, and score.
        - Handles the case where no checkpoints exist.
        """
        checkpoints = self.load_checkpoints()  # Load all saved checkpoints

        if not checkpoints:  # If no checkpoints exist, notify the user
            print("No checkpoints found!")
            return

        # Iterate through all checkpoints and print their details
        for cp in checkpoints:
            states = cp.get("states", {})  # Extract game state details
            pos = states.get("player_position",
                             {"x": "N/A", "y": "N/A"})  # Get player's position (default to "N/A" if missing)

            # Print checkpoint details in a structured format
            print(f"Checkpoint {cp.get('id')}: {cp.get('title')}\n"
                  f"  Description: {cp.get('description')}\n"
                  f"  Position: {pos}, Health: {states.get('player_health')}, "
                  f"Ammo: {states.get('player_ammo')}, Score: {states.get('player_score')}\n"
                  f"  Timestamp: {cp.get('timestamp')}\n")
