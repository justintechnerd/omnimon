using System.Text.Json.Serialization;

namespace OmnimonModuleEditor.Models
{
    public class Evolution
    {
        [JsonPropertyName("to")]
        public string To { get; set; }

        [JsonPropertyName("condition_hearts")]
        public int[] ConditionHearts { get; set; }

        [JsonPropertyName("training")]
        public int[] Training { get; set; }

        [JsonPropertyName("battles")]
        public int[] Battles { get; set; }

        [JsonPropertyName("win_ratio")]
        public int[] WinRatio { get; set; }

        [JsonPropertyName("mistakes")]
        public int[] Mistakes { get; set; }

        [JsonPropertyName("level")]
        public int[] Level { get; set; }

        [JsonPropertyName("overfeed")]
        public int[] Overfeed { get; set; }

        [JsonPropertyName("sleep_disturbances")]
        public int[] SleepDisturbances { get; set; }

        [JsonPropertyName("area")]
        public int? Area { get; set; }

        [JsonPropertyName("stage")]
        public int? Stage { get; set; }

        [JsonPropertyName("version")]
        public int? Version { get; set; }

        [JsonPropertyName("attribute")]
        public string Attribute { get; set; }

        [JsonPropertyName("jogress")]
        public string Jogress { get; set; }
        [JsonPropertyName("jogress_prefix")]
        public bool? JogressPrefix { get; set; }

        [JsonPropertyName("special_encounter")]
        public bool? SpecialEncounter { get; set; }

        [JsonPropertyName("stage-5")]
        public int[] Stage5 { get; set; }

        [JsonPropertyName("item")]
        public string Item { get; set; }
        [JsonPropertyName("time_range")]
        public string[] TimeRange { get; set; }
    }
}