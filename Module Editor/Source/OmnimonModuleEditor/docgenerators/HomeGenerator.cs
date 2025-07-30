using OmnimonModuleEditor.Models;
using System.IO;

namespace OmnimonModuleEditor.docgenerators
{
    internal class HomeGenerator
    {
        public static void GenerateHomePage(string docPath, Module module, string modulePath)
        {
            string template = GeneratorUtils.GetTemplateContent("home.html");
            string content = template
                .Replace("#MODULENAME", module?.Name ?? "Unknown Module")
                .Replace("#MODULEVERSION", module?.Version ?? "1.0")
                .Replace("#MODULEDESCRIPTION", module?.Description ?? "No description available")
                .Replace("#MODULEAUTHOR", module?.Author ?? "Unknown Author")
                .Replace("#MODULENAMEFORMAT", module?.NameFormat ?? "$")
                .Replace("#MODULERULESET", module?.Ruleset ?? "Unknown")
                .Replace("#MODULEADVENTUREMODE", module?.AdventureMode == true ? "Yes" : "No")
                .Replace("#MODULEADVENTUREMODECLASS", module?.AdventureMode == true ? "boolean-true" : "boolean-false")

                // Care Meat
                .Replace("#MODULECAREMEATWEIGHTGAIN", module?.CareMeatWeightGain.ToString() ?? "0")
                .Replace("#MODULECAREMEATHUNGERGAIN", module?.CareMeatHungerGain.ToString() ?? "0")
                .Replace("#MODULECAREMEATCAREMISTAKETIME", module?.CareMeatCareMistakeTime.ToString() ?? "0")
                .Replace("#MODULECAREOVERFEEDTIMER", module?.CareOverfeedTimer.ToString() ?? "0")
                .Replace("#MODULECARECONDITIONHEART", module?.CareConditionHeart == true ? "Yes" : "No")
                .Replace("#MODULECARECONDITIONHEARTCLASS", module?.CareConditionHeart == true ? "boolean-true" : "boolean-false")
                .Replace("#MODULECARECANEATSLEEPING", module?.CareCanEatSleeping == true ? "Yes" : "No")
                .Replace("#MODULECARECANEATSLEEPINGCLASS", module?.CareCanEatSleeping == true ? "boolean-true" : "boolean-false")
                .Replace("#MODULECAREBACKTOSLEEPTIME", module?.CareBackToSleepTime.ToString() ?? "0")
                .Replace("#MODULECARESHAKENEGG", module?.CareEnableShakenEgg == true ? "Yes" : "No")
                .Replace("#MODULECARESHAKENEEGGCLASS", module?.CareEnableShakenEgg == true ? "boolean-true" : "boolean-false")

                // Care Protein
                .Replace("#MODULECAREPROTEINWEIGHTGAIN", module?.CareProteinWeightGain.ToString() ?? "0")
                .Replace("#MODULECAREPROTEINSTRENGTHGAIN", module?.CareProteinStrenghGain.ToString() ?? "0")
                .Replace("#MODULECAREPROTEINDPGAIN", module?.CareProteinDpGain.ToString() ?? "0")
                .Replace("#MODULECAREPROTEINCAREMISTAKETIME", module?.CareProteinCareMistakeTime.ToString() ?? "0")
                .Replace("#MODULECAREPROTEINOVERDOSEMAX", module?.CareProteinOverdoseMax.ToString() ?? "0")
                .Replace("#MODULECARESDISTURBANCEPENALTY", module?.CareDisturbancePenaltyMax.ToString() ?? "0")

                // Care Sleep
                .Replace("#MODULECARESLEEPCAREMISTAKE", module?.CareSleepCareMistakeTimer.ToString() ?? "0")

                // Training
                .Replace("#MODULETRAININGEFFORTGAIN", module?.TrainingEffortGain.ToString() ?? "0")
                .Replace("#MODULETRAININGSTRENGTHGAIN", module?.TrainingStrenghGain.ToString() ?? "0")
                .Replace("#MODULETRAININGWEIGHTWIN", module?.TrainingWeightWin.ToString() ?? "0")
                .Replace("#MODULETRAININGWEIGHTLOSE", module?.TrainingWeightLose.ToString() ?? "0")
                .Replace("#MODULETRAITEDEGGLEVEL", module?.TraitedEggStartingLevel.ToString() ?? "0")
                .Replace("#MODULEREVERSEATKFRAMES", module?.ReverseAtkFrames == true ? "Yes" : "No")
                .Replace("#MODULEREVERSEATKFRAMESCLASS", module?.ReverseAtkFrames == true ? "boolean-true" : "boolean-false")

                // Battle
                .Replace("#MODULEBATTLEBASESICKCHANCEWIN", module?.BattleBaseSickChanceWin.ToString() ?? "0")
                .Replace("#MODULEBATTLEBASESICKCHANCELOSE", module?.BattleBaseSickChanceLose.ToString() ?? "0")
                .Replace("#MODULEBATTLEATTRIBUTEADVANTAGE", module?.BattleAtributeAdvantage.ToString() ?? "0")
                .Replace("#MODULEBATTLEGLOBALHITPOINTS", module?.BattleGlobalHitPoints.ToString() ?? "0")
                .Replace("#MODULEBATTLESEQUENTIALROUNDS", module?.BattleSequentialRounds == true ? "Yes" : "No")
                .Replace("#MODULEBATTLESEQUENTIALROUNDSCLASS", module?.BattleSequentialRounds == true ? "boolean-true" : "boolean-false")

                // Death
                .Replace("#MODULEDEATHMAXINJURIES", module?.DeathMaxInjuries.ToString() ?? "0")
                .Replace("#MODULEDEATHCAREMISTAKE", module?.DeathCareMistake.ToString() ?? "0")
                .Replace("#MODULEDEATHSICKTIMER", module?.DeathSickTimer.ToString() ?? "0")
                .Replace("#MODULEDEATHHUNGERMISTAKE", module?.DeathHungerTimer.ToString() ?? "0")
                .Replace("#MODULEDEATHSTARVATIONCOUNT", module?.DeathStarvationCount.ToString() ?? "0")
                .Replace("#MODULEDEATHSTRENGTHTIMER", module?.DeathStrengthTimer.ToString() ?? "0")
                .Replace("#MODULEDEATHSTAGE45MISTAKE", module?.DeathStage45Mistake.ToString() ?? "0")
                .Replace("#MODULEDEATHSTAGE67MISTAKE", module?.DeathStage67Mistake.ToString() ?? "0")
                .Replace("#MODULEDEATHSAVEBYBPRESS", module?.DeathSaveByBPress.ToString() ?? "0")
                .Replace("#MODULEDEATHSAVEBYSHAKE", module?.DeathSaveByShake.ToString() ?? "0");

            string logoPath = Path.Combine(modulePath, "logo.png");
            if (File.Exists(logoPath))
            {
                File.Copy(logoPath, Path.Combine(docPath, "logo.png"), true);
            }

            File.WriteAllText(Path.Combine(docPath, "home.html"), content);
        }
    }
}
