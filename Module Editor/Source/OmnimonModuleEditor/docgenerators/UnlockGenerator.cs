using OmnimonModuleEditor.Models;
using System.IO;
using System.Text;

namespace OmnimonModuleEditor.docgenerators
{
    internal class UnlockGenerator
    {
        public static void GenerateUnlocksPage(string docPath, Module module)
        {
            string template = GeneratorUtils.GetTemplateContent("unlocks.html");
            var sb = new StringBuilder();

            if (module?.Unlocks != null)
            {
                foreach (var unlock in module.Unlocks)
                {
                    string description = GenerateUnlockDescription(unlock);
                    
                    sb.AppendLine("<tr>");
                    sb.AppendLine($"  <td>{unlock.Label ?? "Unnamed"}</td>");
                    sb.AppendLine($"  <td>{unlock.Type ?? "unknown"}</td>");
                    sb.AppendLine($"  <td>{description}</td>");
                    sb.AppendLine("</tr>");
                }
            }

            string content = template.Replace("#UNLOCKSDATA", sb.ToString());
            File.WriteAllText(Path.Combine(docPath, "unlocks.html"), content);
        }

        private static string GenerateUnlockDescription(Unlock unlock)
        {
            if (unlock == null) return "Unknown unlock condition";

            switch (unlock.Type?.ToLower())
            {
                case "egg":
                    if (unlock.Version.HasValue && unlock.Version > 0)
                    {
                        return $"Unlocked when hatching an egg from version {unlock.Version} of this module.";
                    }
                    return "Unlocked when hatching any egg from this module.";

                case "evolution":
                    var evolutionDesc = new StringBuilder("Unlocked when a pet evolves");
                    
                    if (!string.IsNullOrEmpty(unlock.Name) && unlock.To != null && unlock.To.Count > 0)
                    {
                        evolutionDesc.Append($" to {string.Join(" or ", unlock.To)}");
                    }
                    else if (!string.IsNullOrEmpty(unlock.Name))
                    {
                        evolutionDesc.Append($" to {unlock.Name}");
                    }
                    
                    if (unlock.Version.HasValue && unlock.Version > 0)
                    {
                        evolutionDesc.Append($" in version {unlock.Version}");
                    }
                    
                    evolutionDesc.Append(".");
                    return evolutionDesc.ToString();

                case "adventure":
                    var adventureDesc = new StringBuilder("Unlocked by completing");
                    
                    if (unlock.Area.HasValue && unlock.Area > 0)
                    {
                        adventureDesc.Append($" area {unlock.Area}");
                    }
                    
                    adventureDesc.Append(".");
                    return adventureDesc.ToString();

                case "digidex":
                    var digidexDesc = new StringBuilder("Unlocked when");
                    
                    if (unlock.Amount > 0)
                    {
                        digidexDesc.Append($" {unlock.Amount} are");
                    }
                    else if (!string.IsNullOrEmpty(unlock.Name))
                    {
                        digidexDesc.Append($" {unlock.Name} is");
                    }
                    else
                    {
                        digidexDesc.Append(" a pet is");
                    }
                    
                    digidexDesc.Append(" registered in the Digidex");
                    
                    
                    digidexDesc.Append(".");
                    return digidexDesc.ToString();

                case "background":
                    var bgDesc = new StringBuilder("Background unlocked by");
                    
                    if (unlock.Area.HasValue && unlock.Area > 0)
                    {
                        bgDesc.Append($" completing area {unlock.Area}");
                    }

                    
                    bgDesc.Append(".");
                    return bgDesc.ToString();

                default:
                    var genericDesc = new StringBuilder($"Unlocked not yet available");
                    
                    genericDesc.Append(".");
                    return genericDesc.ToString();
            }
        }
    }
}
