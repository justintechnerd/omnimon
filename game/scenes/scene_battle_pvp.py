"""
Scene Battle PvP
A scene for network battles against other Omnimon devices.
"""
import pygame
from components.window_background import WindowBackground
from core import game_globals, runtime_globals
from core.combat.battle_encounter import BattleEncounter
from core.combat.sim import models as sim_models
from core.utils.scene_utils import change_scene
import game.core.constants as constants

class SceneBattlePvP:
    """
    Scene for PvP network battles using simulation data.
    """

    def __init__(self) -> None:
        """
        Initializes the PvP battle scene.
        """
        self.background = WindowBackground()
        self.battle_encounter = None
        
        runtime_globals.game_console.log("[SceneBattlePvP] Initializing PvP battle scene...")
        
        # Get PvP battle data from runtime globals
        if hasattr(runtime_globals, 'pvp_battle_data') and runtime_globals.pvp_battle_data:
            try:
                pvp_data = runtime_globals.pvp_battle_data
                self.is_host = pvp_data.get('is_host', False)
                self.my_pets = pvp_data.get('my_pets', [])
                self.my_team_data = pvp_data.get('my_team_data', [])
                self.enemy_team_data = pvp_data.get('enemy_team_data', [])
                self.simulation_data = pvp_data.get('simulation_data', {})
                self.module_name = pvp_data.get('module', 'DMC')
                
                # Validate required data
                if not self.my_pets:
                    runtime_globals.game_console.log("[SceneBattlePvP] No my_pets data found")
                    change_scene("game")
                    return
                    
                if not self.enemy_team_data:
                    runtime_globals.game_console.log("[SceneBattlePvP] No enemy_team_data found")
                    change_scene("game")
                    return
                    
                if not self.simulation_data:
                    runtime_globals.game_console.log("[SceneBattlePvP] No simulation_data found")
                    change_scene("game")
                    return
                
                runtime_globals.game_console.log(f"[SceneBattlePvP] PvP data loaded:")
                runtime_globals.game_console.log(f"  - Is Host: {self.is_host}")
                runtime_globals.game_console.log(f"  - My pets: {len(self.my_pets)}")
                runtime_globals.game_console.log(f"  - Enemy team data: {len(self.enemy_team_data)}")
                runtime_globals.game_console.log(f"  - Module: {self.module_name}")
                
                # Create battle encounter for PvP
                self.setup_pvp_battle()
                
                runtime_globals.game_console.log(f"[SceneBattlePvP] PvP battle scene initialized successfully")
                
            except Exception as e:
                runtime_globals.game_console.log(f"[SceneBattlePvP] Error initializing PvP data: {e}")
                import traceback
                runtime_globals.game_console.log(f"[SceneBattlePvP] Traceback: {traceback.format_exc()}")
                change_scene("game")
        else:
            runtime_globals.game_console.log("[SceneBattlePvP] No PvP battle data found, returning to game")
            change_scene("game")

    def setup_pvp_battle(self) -> None:
        """Sets up the PvP battle encounter with simulation data."""
        try:
            runtime_globals.game_console.log("[SceneBattlePvP] Setting up PvP battle encounter...")
            # Create battle encounter in PvP mode
            self.battle_encounter = BattleEncounter(
                self.module_name, 
                area=0, 
                round=0, 
                version=1, 
                pvp_mode=True
            )
            
            runtime_globals.game_console.log(f"[SceneBattlePvP] Battle encounter created for module: {self.module_name}")
            
            if self.is_host:
                # Host: use my_team_data vs enemy_team_data (already correctly ordered)
                runtime_globals.game_console.log("[SceneBattlePvP] Setting up as host")
                self.battle_encounter.setup_pvp_teams(self.my_pets, self.enemy_team_data)
            else:
                # Non-host: keep teams arranged so the battle engine has local pets as team1.
                # Use the BattleEncounter helper to prime the enemy (team2) to fire first
                # so the host team's actions are processed on the first update.
                runtime_globals.game_console.log("[SceneBattlePvP] Setting up as non-host; priming enemy to attack first")
                self.battle_encounter.setup_pvp_teams(self.my_pets, self.enemy_team_data)
                # Use centralized priming to avoid direct manipulation of GameBattle internals
                self.battle_encounter.prime_enemy_first()
            
            # Set the simulation data
            # Try to use original battle log object first (for host)
            original_battle_log = runtime_globals.pvp_battle_data.get('original_battle_log', None)
            if original_battle_log is not None:
                runtime_globals.game_console.log("[SceneBattlePvP] Using original battle log object")
                self.battle_encounter.global_battle_log = original_battle_log
            else:
                # Fallback to serialized data (for non-host)
                battle_log = self.simulation_data.get('battle_log', {})
                runtime_globals.game_console.log("[SceneBattlePvP] Using serialized battle log data")

                # Check if host pre-swapped the battle log for non-host devices
                pre_swapped = bool(self.simulation_data.get('pre_swapped', False))
                if not self.is_host and pre_swapped:
                    runtime_globals.game_console.log("[SceneBattlePvP] Received pre-swapped battle log from host; deserializing directly")
                    try:
                        from core.combat.sim.models import battle_result_from_serialized
                        self.battle_encounter.global_battle_log = battle_result_from_serialized(battle_log)
                    except Exception as e:
                        runtime_globals.game_console.log(f"[SceneBattlePvP] Failed to deserialize pre-swapped battle log: {e}")
                        self.battle_encounter.global_battle_log = battle_log
                else:
                    # For host or cases where swapping wasn't done, use as-is
                    runtime_globals.game_console.log("[SceneBattlePvP] Using battle log as-is (host or no pre-swap)")
                    try:
                        from core.combat.sim.models import battle_result_from_serialized
                        self.battle_encounter.global_battle_log = battle_result_from_serialized(battle_log)
                    except Exception as e:
                        runtime_globals.game_console.log(f"[SceneBattlePvP] Failed to deserialize battle log: {e}")
                        self.battle_encounter.global_battle_log = battle_log
                
            # The simulation payload's victory_status was produced from the
            # simulator using the canonical device labels (device1=device that
            # ran the sim, i.e. the host). For non-host clients we need to 
            # invert the Victory/Defeat value so it represents the local 
            # player's perspective (team1 is local on both devices).
            self.battle_encounter.victory_status = self.simulation_data.get('victory_status', 'Victory')

            # For client: if this device is the non-host, flip Victory/Defeat
            # so the local player's result is correct. Also handle older
            # messages that might still carry "device1"/"device2" values.
            if not self.is_host:
                vs = self.battle_encounter.victory_status
                if isinstance(vs, str):
                    if vs.lower() in ("device1", "device2"):  # legacy shape
                        # If host reported device1/device2, swap the labels
                        self.battle_encounter.victory_status = "device2" if vs == "device1" else "device1"
                    elif vs == "Victory":
                        # Host said Victory -> host (device1) won -> local player lost
                        self.battle_encounter.victory_status = "Defeat"
                    elif vs == "Defeat":
                        # Host said Defeat -> host lost -> local player won
                        self.battle_encounter.victory_status = "Victory"
                # If battle log was pre-swapped, the victory status should match the swapped perspective
                pre_swapped = bool(self.simulation_data.get('pre_swapped', False))
                if pre_swapped:
                    # Battle log was pre-swapped, so victory status should already be from client perspective
                    # Override the inversion above
                    self.battle_encounter.victory_status = self.simulation_data.get('victory_status', 'Victory')
            
            # Log battle data info
            if hasattr(self.battle_encounter.global_battle_log, 'battle_log'):
                log_length = len(self.battle_encounter.global_battle_log.battle_log)
            elif isinstance(self.battle_encounter.global_battle_log, list):
                log_length = len(self.battle_encounter.global_battle_log)
            elif isinstance(self.battle_encounter.global_battle_log, dict) and 'battle_log' in self.battle_encounter.global_battle_log:
                log_length = len(self.battle_encounter.global_battle_log['battle_log'])
            else:
                log_length = 0
                
            runtime_globals.game_console.log(f"[SceneBattlePvP] Loaded {log_length} battle log entries")
            runtime_globals.game_console.log(f"[SceneBattlePvP] Victory status: {self.battle_encounter.victory_status}")
            
            # Process results for animations (but skip XP/level ups in PvP mode)
            if hasattr(self.battle_encounter, 'process_battle_results'):
                self.battle_encounter.process_battle_results()
            
            # Skip to battle phase
            self.battle_encounter.phase = "battle"
            self.battle_encounter.frame_counter = 0
            
            runtime_globals.game_console.log("[SceneBattlePvP] Battle setup completed successfully")
                
        except Exception as e:
            runtime_globals.game_console.log(f"[SceneBattlePvP] Error setting up PvP battle: {e}")
            import traceback
            runtime_globals.game_console.log(f"[SceneBattlePvP] Traceback: {traceback.format_exc()}")
            change_scene("game")

    def swap_battle_log_devices(self, battle_log_dict):
        """Swaps device1/device2 in battle log for client perspective."""
        try:
            swapped_log = battle_log_dict.copy()
            
            # Swap winner
            if swapped_log.get('winner') == 'device1':
                swapped_log['winner'] = 'device2'
            elif swapped_log.get('winner') == 'device2':
                swapped_log['winner'] = 'device1'
            
            # Swap final device states
            if 'device1_final' in swapped_log and 'device2_final' in swapped_log:
                temp = swapped_log['device1_final']
                swapped_log['device1_final'] = swapped_log['device2_final']
                swapped_log['device2_final'] = temp
            
            # Swap battle log entries
            if 'battle_log' in swapped_log:
                for turn_log in swapped_log['battle_log']:
                    # Swap device status
                    if 'device1_status' in turn_log and 'device2_status' in turn_log:
                        temp = turn_log['device1_status']
                        turn_log['device1_status'] = turn_log['device2_status']
                        turn_log['device2_status'] = temp
                    
                    # Swap attack device references
                    if 'attacks' in turn_log:
                        for attack in turn_log['attacks']:
                            if attack.get('device') == 'device1':
                                attack['device'] = 'device2'
                            elif attack.get('device') == 'device2':
                                attack['device'] = 'device1'
            
            return swapped_log
        except Exception as e:
            runtime_globals.game_console.log(f"[SceneBattlePvP] Error swapping battle log: {e}")
            return battle_log_dict  # Return original on error

    def deserialize_battle_result(self, serialized: dict) -> sim_models.BattleResult:
        """Convert a serialized battle result dict into sim_models.BattleResult dataclass.

        This reconstructs DigimonStatus, AttackLog, TurnLog and BattleResult instances.
        Packet hex strings will be converted back to bytes when possible.
        """
        # Helper to restore DigimonStatus
        def make_status(d):
            return sim_models.DigimonStatus(name=d.get('name', ''), hp=int(d.get('hp', 0)), alive=bool(d.get('alive', False)))

        # Helper to restore AttackLog
        def make_attack(d):
            return sim_models.AttackLog(
                turn=int(d.get('turn', 0)),
                device=d.get('device', ''),
                attacker=int(d.get('attacker', -1)),
                defender=int(d.get('defender', -1)),
                hit=bool(d.get('hit', False)),
                damage=int(d.get('damage', 0))
            )

        # Helper to restore TurnLog
        def make_turn(t):
            device1 = [make_status(s) for s in t.get('device1_status', [])]
            device2 = [make_status(s) for s in t.get('device2_status', [])]
            attacks = [make_attack(a) for a in t.get('attacks', [])]
            return sim_models.TurnLog(turn=int(t.get('turn', 0)), device1_status=device1, device2_status=device2, attacks=attacks)

        # Reconstruct packets: convert hex strings back to bytes where applicable
        def restore_packets(packet_lists):
            restored = []
            for pkt_list in packet_lists or []:
                new_list = []
                for pkt in pkt_list:
                    if isinstance(pkt, str):
                        try:
                            new_list.append(bytes.fromhex(pkt))
                        except Exception:
                            new_list.append(pkt)
                    else:
                        new_list.append(pkt)
                restored.append(new_list)
            return restored

        winner = serialized.get('winner', 'draw')
        device1_final = [make_status(s) for s in serialized.get('device1_final', [])]
        device2_final = [make_status(s) for s in serialized.get('device2_final', [])]
        battle_log = [make_turn(t) for t in serialized.get('battle_log', [])]
        device1_packets = restore_packets(serialized.get('device1_packets', []))
        device2_packets = restore_packets(serialized.get('device2_packets', []))

        return sim_models.BattleResult(
            winner=winner,
            device1_final=device1_final,
            device2_final=device2_final,
            battle_log=battle_log,
            device1_packets=device1_packets,
            device2_packets=device2_packets
        )

    def update(self) -> None:
        """
        Updates the PvP battle scene.
        """
        if self.battle_encounter:
            self.battle_encounter.update()
            
            # Check if battle is complete
            if self.battle_encounter.phase == "result" or self.battle_encounter.phase == "clear":
                # Battle completed, check for return to game
                pass

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the PvP battle scene.
        """
        self.background.draw(surface)
        if self.battle_encounter:
            self.battle_encounter.draw(surface)

    def handle_event(self, input_action) -> None:
        """
        Handles keyboard and GPIO button inputs for the PvP battle scene.
        """
        if self.battle_encounter:
            self.battle_encounter.handle_event(input_action)
            
            # Check for battle completion and return to game
            if self.battle_encounter.phase in ["result", "clear", "finished"]:
                if input_action == "A" or input_action == "B" or input_action == "START":
                    runtime_globals.game_console.log("[SceneBattlePvP] PvP battle completed, returning to game")
                    # Clear PvP data
                    if hasattr(runtime_globals, 'pvp_battle_data'):
                        delattr(runtime_globals, 'pvp_battle_data')
                    change_scene("game")
        else:
            # If no battle encounter, return to game on any input
            if input_action:
                runtime_globals.game_console.log("[SceneBattlePvP] No battle encounter, returning to game")
                if hasattr(runtime_globals, 'pvp_battle_data'):
                    delattr(runtime_globals, 'pvp_battle_data')
                change_scene("game")
