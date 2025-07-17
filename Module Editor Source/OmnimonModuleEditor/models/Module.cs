using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace OmnimonModuleEditor.Models
{
    public class Module
    {
        [JsonPropertyName("name")]
        public string Name { get; set; }

        [JsonPropertyName("name_format")]
        public string NameFormat { get; set; }

        [JsonPropertyName("ruleset")]
        public string Ruleset { get; set; }

        [JsonPropertyName("adventure_mode")]
        public bool AdventureMode { get; set; }

        // Care Meat
        [JsonPropertyName("care_meat_weight_gain")]
        public int CareMeatWeightGain { get; set; }

        [JsonPropertyName("care_meat_hunger_gain")]
        public int CareMeatHungerGain { get; set; }

        [JsonPropertyName("care_meat_care_mistake_time")]
        public int CareMeatCareMistakeTime { get; set; }

        [JsonPropertyName("care_overfeed_timer")]
        public int CareOverfeedTimer { get; set; }

        [JsonPropertyName("care_condition_heart")]
        public bool CareConditionHeart { get; set; }

        [JsonPropertyName("care_can_eat_sleeping")]
        public bool CareCanEatSleeping { get; set; }

        [JsonPropertyName("care_back_to_sleep_time")]
        public int CareBackToSleepTime { get; set; }

        [JsonPropertyName("care_enable_shaken_egg")]
        public bool CareEnableShakenEgg { get; set; }

        // Care Protein
        [JsonPropertyName("care_protein_weight_gain")]
        public int CareProteinWeightGain { get; set; }

        [JsonPropertyName("care_protein_strengh_gain")]
        public int CareProteinStrenghGain { get; set; }

        [JsonPropertyName("care_protein_dp_gain")]
        public int CareProteinDpGain { get; set; }

        [JsonPropertyName("care_protein_care_mistake_time")]
        public int CareProteinCareMistakeTime { get; set; }

        [JsonPropertyName("care_protein_overdose_max")]
        public int CareProteinOverdoseMax { get; set; }

        [JsonPropertyName("care_disturbance_penalty_max")]
        public int CareDisturbancePenaltyMax { get; set; }

        // Care Sleep
        [JsonPropertyName("care_sleep_care_mistake_timer")]
        public int CareSleepCareMistakeTimer { get; set; }

        // Training
        [JsonPropertyName("training_effort_gain")]
        public int TrainingEffortGain { get; set; }

        [JsonPropertyName("training_strengh_gain")]
        public int TrainingStrenghGain { get; set; }

        [JsonPropertyName("training_weight_win")]
        public int TrainingWeightWin { get; set; }

        [JsonPropertyName("training_weight_lose")]
        public int TrainingWeightLose { get; set; }

        [JsonPropertyName("traited_egg_starting_level")]
        public int TraitedEggStartingLevel { get; set; }

        [JsonPropertyName("reverse_atk_frames")]
        public bool ReverseAtkFrames { get; set; }

        // Battle
        [JsonPropertyName("battle_base_sick_chance_win")]
        public int BattleBaseSickChanceWin { get; set; }

        [JsonPropertyName("battle_base_sick_chance_lose")]
        public int BattleBaseSickChanceLose { get; set; }

        [JsonPropertyName("battle_atribute_advantage")]
        public int BattleAtributeAdvantage { get; set; }

        [JsonPropertyName("battle_global_hit_points")]
        public int BattleGlobalHitPoints { get; set; }

        [JsonPropertyName("battle_sequential_rounds")]
        public bool BattleSequentialRounds { get; set; }

        // Death
        [JsonPropertyName("death_max_injuries")]
        public int DeathMaxInjuries { get; set; }

        [JsonPropertyName("death_care_mistake")]
        public int DeathCareMistake { get; set; }

        [JsonPropertyName("death_sick_timer")]
        public int DeathSickTimer { get; set; }

        [JsonPropertyName("death_hunger_timer")]
        public int DeathHungerTimer { get; set; }

        [JsonPropertyName("death_starvation_count")]
        public int DeathStarvationCount { get; set; }

        [JsonPropertyName("death_strength_timer")]
        public int DeathStrengthTimer { get; set; }

        [JsonPropertyName("death_stage45_mistake")]
        public int DeathStage45Mistake { get; set; }

        [JsonPropertyName("death_stage67_mistake")]
        public int DeathStage67Mistake { get; set; }

        [JsonPropertyName("death_save_by_b_press")]
        public int DeathSaveByBPress { get; set; }

        [JsonPropertyName("death_save_by_shake")]
        public int DeathSaveByShake { get; set; }

        [JsonPropertyName("unlocks")]
        public List<Unlock> Unlocks { get; set; }

        [JsonPropertyName("backgrounds")]
        public List<Background> Backgrounds { get; set; }
    }

    public class Unlock
    {
        [JsonPropertyName("name")]
        public string Name { get; set; }

        [JsonPropertyName("type")]
        public string Type { get; set; }

        [JsonPropertyName("version")]
        public int? Version { get; set; }

        [JsonPropertyName("label")]
        public string Label { get; set; }

        [JsonPropertyName("area")]
        public int? Area { get; set; }

        [JsonPropertyName("to")]
        public string To { get; set; }
        [JsonPropertyName("amount")]
        public int? Amount { get; set; }
    }

    public class Background
    {
        [JsonPropertyName("name")]
        public string Name { get; set; }

        [JsonPropertyName("day_night")]
        public bool DayNight { get; set; }

        [JsonPropertyName("label")]
        public string Label { get; set; }
    }

    public enum RulesetType
    {
        dmc,
        penc,
        dmx
    }
}