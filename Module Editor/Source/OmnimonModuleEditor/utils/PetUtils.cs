using OmnimonModuleEditor.Models;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Text.Json;
using System.Windows.Forms;

namespace OmnimonModuleEditor.Utils
{
    public static class PetUtils
    {
        public static string AttributeEnumToJson(AttributeEnum attr)
        {
            switch (attr)
            {
                case AttributeEnum.DATA: return "Da";
                case AttributeEnum.VIRUS: return "Vi";
                case AttributeEnum.VACCINE: return "Va";
                case AttributeEnum.FREE:
                default: return "";
            }
        }

        public static AttributeEnum JsonToAttributeEnum(string value)
        {
            switch (value)
            {
                case "Da": return AttributeEnum.DATA;
                case "Vi": return AttributeEnum.VIRUS;
                case "Va": return AttributeEnum.VACCINE;
                case "": default: return AttributeEnum.FREE;
            }
        }

        public static Color GetAttributeColor(string attr)
        {
            switch (attr)
            {
                case "Da": return Color.FromArgb(66, 165, 245);      // Data
                case "Va": return Color.FromArgb(102, 187, 106);     // Vaccine
                case "Vi": return Color.FromArgb(237, 83, 80);       // Virus
                case "": return Color.FromArgb(171, 71, 188);        // Free
                default: return Color.FromArgb(171, 71, 188);        // Free (fallback)
            }
        }

        public static List<Pet> LoadPetsFromJson(string modulePath)
        {
            var pets = new List<Pet>();
            string monsterPath = Path.Combine(modulePath, "monster.json");
            if (File.Exists(monsterPath))
            {
                try
                {
                    string json = File.ReadAllText(monsterPath);
                    using (JsonDocument doc = JsonDocument.Parse(json))
                    {
                        var root = doc.RootElement;
                        if (root.TryGetProperty("monster", out var monstersElement))
                        {
                            pets = JsonSerializer.Deserialize<List<Pet>>(monstersElement.GetRawText());
                        }
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show(
                        string.Format(Properties.Resources.ErrorLoadingMonster, ex.Message),
                        Properties.Resources.Error,
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error);
                }
            }
            return pets;
        }

        public static void SortPets(this List<Pet> pets)
        {
            if (pets == null) return;
            pets.Sort((a, b) =>
            {
                int cmp = a.Version.CompareTo(b.Version);
                if (cmp != 0) return cmp;
                cmp = a.Stage.CompareTo(b.Stage);
                if (cmp != 0) return cmp;
                return string.Compare(a.Name, b.Name, StringComparison.OrdinalIgnoreCase);
            });
        }

        public static Pet ClonePet(Pet pet)
        {
            if (pet == null) return null;
            return new Pet
            {
                Name = pet.Name,
                Stage = pet.Stage,
                Version = pet.Version,
                Special = pet.Special,
                SpecialKey = pet.SpecialKey,
                Sleeps = pet.Sleeps,
                Wakes = pet.Wakes,
                AtkMain = pet.AtkMain,
                AtkAlt = pet.AtkAlt,
                Time = pet.Time,
                PoopTimer = pet.PoopTimer,
                Energy = pet.Energy,
                MinWeight = pet.MinWeight,
                Stomach = pet.Stomach,
                HungerLoss = pet.HungerLoss,
                StrengthLoss = pet.StrengthLoss,
                HealDoses = pet.HealDoses,
                Power = pet.Power,
                Attribute = pet.Attribute,
                ConditionHearts = pet.ConditionHearts,
                JogressAvaliable = pet.JogressAvaliable,
                Hp = pet.Hp,
                Evolve = pet.Evolve != null ? new List<Evolution>(pet.Evolve) : null
            };
        }

        /// <summary>
        /// Loads all pet sprites for a given pet.
        /// </summary>
        public static List<Image> LoadPetSprites(string modulePath, Module module, Pet pet, int spriteCount = 15)
        {
            var sprites = new List<Image>();
            if (pet == null || module == null) return sprites;

            string nameFormat = module?.NameFormat ?? "_";
            string safePetName = pet.Name.Replace(':', '_');
            string folderName = nameFormat.Replace("$", safePetName);

            for (int i = 0; i < spriteCount; i++)
            {
                string spritePath = Path.Combine(modulePath, "monsters", folderName, $"{i}.png");
                if (File.Exists(spritePath))
                {
                    try
                    {
                        using (var fs = new FileStream(spritePath, FileMode.Open, FileAccess.Read, FileShare.Read))
                        {
                            var img = Image.FromStream(fs);
                            sprites.Add(new Bitmap(img));
                        }
                    }
                    catch
                    {
                        sprites.Add(null);
                    }
                }
                else
                {
                    sprites.Add(null);
                }
            }
            return sprites;
        }

        public static Dictionary<int, Image> LoadAtkSprites(string modulePath)
        {
            Dictionary<int, Image> atkSprites = new Dictionary<int, Image>();
            // Caminho do fallback: ...\resources\atk
            string modulesDir = Path.GetDirectoryName(modulePath.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
            string rootDir = Path.GetDirectoryName(modulesDir); //go to the root directory
            string resourcesAtk = Path.Combine(rootDir, "resources", "atk");

            // Novo: caminho do módulo
            string moduleAtk = Path.Combine(modulePath, "atk");
            bool moduleAtkExists = Directory.Exists(moduleAtk);

            for (int i = 1; i <= 117; i++)
            {
                string path = null;
                if (moduleAtkExists)
                {
                    string customPath = Path.Combine(moduleAtk, $"{i}.png");
                    if (File.Exists(customPath))
                        path = customPath;
                }
                if (path == null)
                {
                    string fallbackPath = Path.Combine(resourcesAtk, $"{i}.png");
                    if (File.Exists(fallbackPath))
                        path = fallbackPath;
                }

                if (path != null)
                {
                    try
                    {
                        atkSprites[i] = Image.FromFile(path);
                    }
                    catch { atkSprites[i] = null; }
                }
                else
                {
                    atkSprites[i] = null;
                }
            }
            return atkSprites;
        }
    }
}