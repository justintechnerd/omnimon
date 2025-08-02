using OmnimonModuleEditor.Models;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace OmnimonModuleEditor.docgenerators
{
    internal class EnemyGenerator
    {
        public static void GenerateEnemiesPage(string docPath, List<BattleEnemy> enemies, Module module, string modulePath)
        {
            string template = GeneratorUtils.GetTemplateContent("enemies.html");
            var sb = new StringBuilder();

            var enemiesByArea = enemies.GroupBy(e => e.Area).OrderBy(g => g.Key);

            foreach (var areaGroup in enemiesByArea)
            {
                sb.AppendLine("<div class=\"area-section\">");
                sb.AppendLine($"  <h2>Area {areaGroup.Key}</h2>");

                var enemiesByRound = areaGroup.GroupBy(e => e.Round).OrderBy(g => g.Key);
                var maxRound = areaGroup.Max(e => e.Round);

                foreach (var roundGroup in enemiesByRound)
                {
                    bool isBossRound = roundGroup.Key == maxRound;
                    string roundClass = isBossRound ? "round-section boss-round" : "round-section";

                    sb.AppendLine($"    <div class=\"{roundClass}\">");
                    sb.AppendLine($"      <h3>Round {roundGroup.Key}{(isBossRound ? " - Boss Round" : "")}</h3>");
                    sb.AppendLine("      <div class=\"enemies-grid\">");

                    // Group enemies by version and display them side by side
                    var enemiesByVersion = roundGroup.OrderBy(e => e.Version);

                    foreach (var enemy in enemiesByVersion)
                    {
                        string attributeColor = GeneratorUtils.GetAttributeBackgroundColor(enemy.Attribute ?? "");
                        string cardClass = isBossRound ? "enemy-card boss-enemy" : "enemy-card";

                        sb.AppendLine($"        <div class=\"{cardClass}\">");
                        sb.AppendLine("          <div class=\"enemy-sprite-container\">");
                        sb.AppendLine($"            <div class=\"enemy-sprite\" style=\"background-color:{attributeColor}\">");
                        sb.AppendLine($"              <img src=\"../monsters/{GeneratorUtils.GetPetFolderName(enemy.Name, module)}/0.png\" alt=\"{enemy.Name}\" onerror=\"this.src='../missing.png'\">");
                        sb.AppendLine("            </div>");
                        sb.AppendLine("          </div>");
                        sb.AppendLine($"          <div class=\"enemy-name\">{enemy.Name}</div>");
                        sb.AppendLine($"          <div class=\"enemy-version\">Version {enemy.Version}</div>");
                        sb.AppendLine($"          <div class=\"enemy-stats\">Power: {enemy.Power} | HP: {enemy.Hp}</div>");
                        if (!string.IsNullOrEmpty(enemy.Prize))
                            sb.AppendLine($"          <div class=\"enemy-prize\">Prize: {enemy.Prize}</div>");
                        if (!string.IsNullOrEmpty(enemy.Unlock))
                            sb.AppendLine($"          <div class=\"enemy-unlock\">Unlock: {enemy.Unlock}</div>");
                        sb.AppendLine("        </div>");
                    }

                    sb.AppendLine("      </div>");
                    sb.AppendLine("    </div>");
                }

                sb.AppendLine("</div>");
            }

            string content = template.Replace("#ENEMIESDATA", sb.ToString());
            File.WriteAllText(Path.Combine(docPath, "enemies.html"), content);
        }
    }
}
