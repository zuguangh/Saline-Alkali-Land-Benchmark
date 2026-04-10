# -*- coding: utf-8 -*-

# Experimental Basic Information
experimental_info_metrics = """
Location
Latitude and Longitude: (If the text mentions a location but does not directly provide coordinates, standard latitude and longitude should be queried based on the location name)
Experiment Type: (e.g., Field experiment, Pot experiment)
Meteorological Conditions
Experiment Duration
"""

# Initial Indicators of Saline-Alkali Land
initial_metrics = """
Pre-treatment Saline-Alkali Land Type: (e.g., Coastal saline-alkali land, Soda saline-alkali land, Inland saline-alkali land)
Pre-treatment Electrical Conductivity (EC): dS·m⁻¹
Pre-treatment Total Soluble Salt Content: g·kg⁻¹ (dry soil weight), or %
Pre-treatment pH: (pH value or change)
Pre-treatment pH Measurement Method: (CaCl₂ method, 5:1 water-soil ratio, 2.5:1 water-soil ratio)
Pre-treatment Exchangeable Sodium Percentage (ESP): %
Pre-treatment Sodium Adsorption Ratio (SAR):
Pre-treatment Cation Exchange Capacity (CEC): cmol(+)/kg
Pre-treatment Sodium Ion (Na⁺) Content: mmol/L
Pre-treatment Calcium Ion (Ca²⁺) Content: mmol/L
Pre-treatment Magnesium Ion (Mg²⁺) Content: mmol/L
Pre-treatment Chloride Ion (Cl⁻) Content: mmol/L
Pre-treatment Sulfate Ion (SO₄²⁻) Content: mmol/L
Pre-treatment Bicarbonate (HCO₃⁻) Content: mmol/L
Pre-treatment Carbonate (CO₃²⁻) Content: mmol/L
Pre-treatment Soil Organic Matter (SOM) Content: g/kg
Pre-treatment Soil Texture: (sand, silt, clay) %
Pre-treatment Soil Bulk Density: g·cm⁻³
Pre-treatment Total Porosity: %
Pre-treatment Soil Temperature: ℃
Pre-treatment Calcium Carbonate (CaCO₃) Content: g·kg⁻¹
Pre-treatment Available Phosphorus (P) Content: mg/kg
Pre-treatment Available Potassium (K) Content: mg/kg
Pre-treatment Total Nitrogen (N) Content: mg/kg
Pre-treatment Ammonium Nitrogen (NH₄⁺-N) Content: mg/kg
Pre-treatment Nitrate Nitrogen (NO₃⁻-N) Content: mg/kg
Pre-treatment Trace Element Content
Pre-treatment Field Capacity (FC): % (volumetric water content)
Pre-treatment Permanent Wilting Point (PWP): % (volumetric water content)
Pre-treatment Soil Water Content (SWC): % (volumetric, v/v), or g·g⁻¹ (gravimetric)
Pre-treatment Saturated Hydraulic Conductivity (Ks): cm·d⁻¹ or mm·h⁻¹
Pre-treatment Capillary Rise Height: (Closely related to groundwater depth and salt ascent)
Pre-treatment Groundwater Depth: m
Pre-treatment Irrigation Water EC: dS/m
Pre-treatment Annual Evaporation/Precipitation Ratio
"""

# Management Measures Indicators
operation_metrics = """
Measure/Amendment: (e.g., Application of gypsum, Subsurface pipe drainage, etc. If the article has different treatments, list them as Control, Treatment 1, Treatment 2... in multiple rows)
Application Rate/Intensity: (e.g., Gypsum application rate, Subsurface pipe density, Microbial inoculant dosage, etc.)
Duration/Timing: (Application timing: Pre-sowing / Post-sowing / During growing season; Remediation period: Short-term (1 season/1 year), Medium-term (2-3 years), Long-term (5 years); Single application or continuous application (annual repetition vs. one-time amendment))
Cost
"""

# Crop Growth Indicators
crop_growth_metrics = """
Experimental Crop Name(s): (Crop 1: Sorghum; Crop 2: Wheat; If multiple crops, list separately)
Seed Pre-treatment: (Whether crop seeds were pre-treated)
Genotype/Cultivar
Trait: (Salt tolerance)
Photosynthetic Rate (Pn): µmol CO₂·m⁻²·s⁻¹ (If dynamic data exists, describe in multiple rows)
Respiration Rate
Stomatal Conductance (gs): mol H₂O·m⁻²·s⁻¹
Transpiration Rate (Tr): mmol·m⁻²·s⁻¹ or mol·m⁻²·s⁻¹
Chlorophyll Content
Water Use Efficiency (WUE, Pn/gs): μmol CO₂·mol⁻¹ H₂O
Specific Leaf Area (SLA)
Leaf Area
Plant Height
Root Length Density (RLD): cm·cm⁻³ or m·m⁻³
Root Length: cm or m
Root Surface Area: cm²·plant⁻¹ or m²·m⁻³ (soil volume)
Root Volume: cm³·plant⁻¹
Root Diameter: mm
Proline, Soluble Sugar Content: μmol·g⁻¹ FW (Fresh Weight)
Specific Root Length (SRL)
Root:Shoot Ratio, Root:Stem:Leaf Ratio
Crop Water Use Efficiency (CWUE)
Crop Nutrient Content
Crop Salt Content: g/kg
"""

# Treatment Effectiveness, Yield and Cost Indicators
effectiveness_metrics = """
Post-treatment Biomass: g/plant, g/m², kg·ha⁻¹ or g·plant⁻¹
Post-treatment Yield: t/ha, kg·ha⁻¹ or g·plant⁻¹
Post-treatment Saline-Alkali Land Type: (e.g., Coastal, Soda, Inland, etc.)
Post-treatment Electrical Conductivity (EC): dS·m⁻¹
Post-treatment Total Soluble Salt Content: g·kg⁻¹ (dry soil weight), or %
Post-treatment pH: (pH value or change)
Post-treatment pH Measurement Method: (CaCl₂ method, 5:1 water-soil ratio, 2.5:1 water-soil ratio)
Post-treatment Exchangeable Sodium Percentage (ESP): %
Post-treatment Sodium Adsorption Ratio (SAR):
Post-treatment Cation Exchange Capacity (CEC): cmol(+)/kg
Post-treatment Sodium Ion (Na⁺) Content: mmol/L
Post-treatment Calcium Ion (Ca²⁺) Content: mmol/L
Post-treatment Magnesium Ion (Mg²⁺) Content: mmol/L
Post-treatment Chloride Ion (Cl⁻) Content: mmol/L
Post-treatment Sulfate Ion (SO₄²⁻) Content: mmol/L
Post-treatment Bicarbonate (HCO₃⁻) Content: mmol/L
Post-treatment Carbonate (CO₃²⁻) Content: mmol/L
Post-treatment Soil Organic Matter (SOM) Content: g/kg
Post-treatment Soil Texture: (sand, silt, clay) %
Post-treatment Soil Bulk Density: g·cm⁻³
Post-treatment Total Porosity: %
Post-treatment Soil Temperature: ℃
Post-treatment Calcium Carbonate (CaCO₃) Content: g·kg⁻¹
Post-treatment Available Phosphorus (P) Content: mg/kg
Post-treatment Available Potassium (K) Content: mg/kg
Post-treatment Total Nitrogen (N) Content: mg/kg
Post-treatment Ammonium Nitrogen (NH₄⁺-N) Content: mg/kg
Post-treatment Nitrate Nitrogen (NO₃⁻-N) Content: mg/kg
Post-treatment Trace Element Content
Post-treatment Field Capacity (FC): % (volumetric water content)
Post-treatment Permanent Wilting Point (PWP): % (volumetric water content)
Post-treatment Soil Water Content (SWC): % (volumetric, v/v), or g·g⁻¹ (gravimetric)
Post-treatment Saturated Hydraulic Conductivity (Ks): cm·d⁻¹ or mm·h⁻¹
Post-treatment Capillary Rise Height: (Closely related to groundwater depth and salt ascent)
Post-treatment Groundwater Depth: m
Post-treatment Irrigation Water EC: dS/m
Post-treatment Annual Evaporation/Precipitation Ratio
"""

# Comprehensive Benefit Indicators
comprehensive_metrics = """
Crop Yield Increase Rate: (%)
Soil Salinity/Alkalinity Reduction Rate: (%)
Amendment Input-Output Ratio: (Economic benefit)
Soil Organic Carbon (SOC) Increment: (Carbon sequestration effect)
Microbial Quantity and Diversity
"""

english_metrics_list = [
    experimental_info_metrics,
    initial_metrics,
    operation_metrics,
    crop_growth_metrics,
    effectiveness_metrics,
    comprehensive_metrics,
]

english_all_metrics = []
for metrics in english_metrics_list:
    english_all_metrics.extend(metrics.strip().split("\n"))


# RAG Generation Prompt for Large Language Models
english_rag_prompt_template = """
You are an agricultural expert. Please strictly extract relevant indicators for saline-alkali land remediation based on the following context. Requirements:

Must extract information strictly based on the context. Any form of fabrication, inference, or supplementation is strictly prohibited.

For tabular data, completely extract all relevant values (if multiple rows exist, retain all).

For indicators not explicitly mentioned, return "Not provided". Do not provide other explanations.

The output format must be JSON, with key-value pairs strictly corresponding to the following indicator list.

Indicator list to extract:

{metrics}

Context: {context}

Output Example 1:
"Location": "Shengda Forest Farm, Dongying District, Dongying City",
"Latitude and Longitude": "38.92°N, 121.23°E",
"Experiment Type": "Field experiment",
"Meteorological Conditions": "Temperate monsoon climate, average annual temperature 12.8°C, accumulated temperature 4300°C, annual sunshine hours 2315.7h, precipitation 555.9mm (65% in summer), frost-free period 206d",
"Experiment Duration": "5 years (September 2019 - May 2024)"

Output Example 2:
"Pre-treatment Saline-Alkali Land Type": "Coastal saline-alkali wasteland",
"Pre-treatment Electrical Conductivity (EC)": "2.4 dS·m⁻¹",
"Pre-treatment Total Soluble Salt Content": "2.4 g·kg⁻¹",
"Pre-treatment pH": "8.6",
"Pre-treatment pH Measurement Method": "5:1 water-soil ratio",
"Pre-treatment Exchangeable Sodium Percentage (ESP)": "9.04%",
"Pre-treatment Sodium Adsorption Ratio (SAR)": "0~20cm soil layer: 20.86; 20~40cm soil layer: 14.58",
"Pre-treatment Cation Exchange Capacity (CEC)": "12.34 cmol(+)/kg",
"Pre-treatment Sodium Ion (Na⁺) Content": "5.67 mmol/L",
"Pre-treatment Calcium Ion (Ca²⁺) Content": "8.90 mmol/L",
"Pre-treatment Magnesium Ion (Mg²⁺) Content": "1.23 mmol/L",
"Pre-treatment Chloride Ion (Cl⁻) Content": "4.56 mmol/L",
"Pre-treatment Sulfate Ion (SO₄²⁻) Content": "7.89 mmol/L",
"Pre-treatment Bicarbonate (HCO₃⁻) Content": "0.09-0.10 mmol/L",
"Pre-treatment Carbonate (CO₃²⁻) Content": "0.12 mmol/L",
"Pre-treatment Soil Organic Matter (SOM) Content": "1.56 g/kg",
"Pre-treatment Soil Texture": "Clay 62.96%, Silt 26.78%, Sand 10.26%",
"Pre-treatment Soil Bulk Density": "1.25 g·cm⁻³",
"Pre-treatment Total Porosity": "50%",
"Pre-treatment Soil Temperature": "25℃",
"Pre-treatment Calcium Carbonate (CaCO₃) Content": "5.67 g·kg⁻¹",
"Pre-treatment Available Phosphorus (P) Content": "10 mg/kg",
"Pre-treatment Available Potassium (K) Content": "20 mg/kg",
"Pre-treatment Total Nitrogen (N) Content": "0.15 mg/kg",
"Pre-treatment Ammonium Nitrogen (NH₄⁺-N) Content": "0.05 mg/kg",
"Pre-treatment Nitrate Nitrogen (NO₃⁻-N) Content": "0.10 mg/kg",
"Pre-treatment Trace Element Content": "Not provided",
"Pre-treatment Field Capacity (FC)": "30%",
"Pre-treatment Permanent Wilting Point (PWP)": "0~20cm 9.49%; 20~40cm 8.39%; 40~60cm 9.43%; 60~80cm 6.40%; 80~100cm 6.00%",
"Pre-treatment Soil Water Content (SWC)": "Pre-sowing average for 0~100cm: 11.83-12.30%",
"Pre-treatment Saturated Hydraulic Conductivity (Ks)": "1.0 cm·d⁻¹",
"Pre-treatment Capillary Rise Height": "Not provided",
"Pre-treatment Groundwater Depth": "2.0 m",
"Pre-treatment Irrigation Water EC": "1.5 dS/m",
"Pre-treatment Annual Evaporation/Precipitation Ratio": "3.33:1"

Output Example 3:
"Measure/Amendment": "Control (CK - Bare land); Treatment 1 (T1 - Sesbania cannabina planting and incorporation); Treatment 2 (T2 - Sweet clover planting and incorporation); Treatment 3 (T3 - Sorghum-sudangrass hybrid planting and incorporation); Treatment 4 (T4 - 'Chaomu No.1' Barnyard millet planting and incorporation)",
"Application Rate/Intensity": "Amendment application: Phosphogypsum (by-product of phosphate fertilizer industry) + Compound fertilizer (N:P₂O₅:K₂O=12:8:10)
1. Phosphogypsum: Application rate 45.000 t·ha⁻¹ (equivalent to 50 g per pot)
2. Compound fertilizer: Application rate 0.900 t·ha⁻¹ (amount per pot not mentioned)
Water treatment: Set 7 soil water content gradients (based on saturated water holding capacity)
Treatment 1: 90% SWHC
Treatment 2: 80% SWHC
Treatment 3: 70% SWHC
Treatment 4: 60% SWHC
Treatment 5: 50% SWHC
Treatment 6: 40% SWHC
Treatment 7: 30% SWHC",
"Duration/Timing": "Phosphogypsum and compound fertilizer were applied once and mixed with soil before wheat transplanting (pre-sowing application); Water treatments started after wheat establishment and normal growth began, controlled by quantitative watering every two days using the weighing method.",
"Cost": "CK (Treatment 1): Formula fertilizer cost 40kg×3.05 yuan/kg + Water-soluble fertilizer cost 5kg×9.5 yuan/kg = 122 + 47.5 = 169.5;
Treatment 2: Humic acid controlled-release fertilizer cost 40kg×3.20 yuan/kg + Water-soluble fertilizer cost 5kg×9.5 yuan/kg = 128 + 47.5 = 175.5;
Treatment 3: Humic acid controlled-release fertilizer cost 40kg×3.20 yuan/kg + Soil amendment cost 40kg×1.73 yuan/kg + Water-soluble fertilizer cost 5kg×9.5 yuan/kg = 128 + 69.2 + 47.5 = 244.7;
Treatment 4: Humic acid controlled-release fertilizer cost 40kg×3.20 yuan/kg + Soil amendment cost 60kg×1.73 yuan/kg + Water-soluble fertilizer cost 5kg×9.5 yuan/kg = 128 + 103.8 + 47.5 = 279.3"

Output Example 4:
"Experimental Crop Name(s)": "Halogen glomeratus; Suaeda salsa; Puccinellia distans; Alfalfa; Hairy vetch; Common vetch; Sweet sorghum; Barley; Oat",
"Seed Pre-treatment": "No",
"Genotype/Cultivar": "Alfalfa (Adina), Hairy vetch (Turkmen), Common vetch (Longjian 2), Sweet sorghum (Dali Shi), Barley (Ganpi 4), Oat (Baiyan 2)",
"Trait": "All are salt-tolerant plants, among which T1, T2, T3 are highly salt-tolerant halophytes, T4-T9 are salt-tolerant forage/crops.",
"Photosynthetic Rate (Pn)": "Halogen glomeratus: 15.2 µ",
"Respiration Rate": "Not provided",
"Stomatal Conductance (gs)": "Halogen glomeratus: 0.25 mol H₂O·m⁻²·s⁻¹",
"Transpiration Rate (Tr)": "Halogen glomeratus: 4.5 mmol·m⁻²·s⁻¹",
"Chlorophyll Content": "7 days: Saline soil CK: G+B20: increased by 34.77% compared to CK (75 mmol/L, 21 days)",
"Water Use Efficiency (WUE, Pn/gs)": "Halogen glomeratus: 63.2 μmol CO₂·mol⁻¹ H₂O",
"Specific Leaf Area (SLA)": "Not provided",
"Leaf Area": "Halogen glomeratus: 45.6 cm²",
"Plant Height": "Halogen glomeratus: 96.0-242.0 cm",
"Root Length Density (RLD)": "Halogen glomeratus: 1.25 cm·cm⁻³",
"Root Length": "Halogen glomeratus: 12.5 m",
"Root Surface Area": "Halogen glomeratus: 2500 cm²·plant⁻¹",
"Root Volume": "Halogen glomeratus: 15 cm³·plant⁻¹",
"Root Diameter": "Halogen glomeratus: 1.5 mm",
"Proline, Soluble Sugar Content": "Soluble sugar content: Treatment 1 - Treatment 7: 0.062, 0.068, 0.078, 0.109, 0.098, 0.125, 0.197",
"Specific Root Length (SRL)": "Halogen glomeratus: 100 m·g⁻¹",
"Root:Shoot Ratio, Root:Stem:Leaf Ratio": "Halogen glomeratus: Root:Shoot ratio 0.25; Root:Stem:Leaf ratio 0.30",
"Crop Water Use Efficiency (CWUE)": "20%",
"Crop Nutrient Content": "Not provided",
"Crop Salt Content": "Yield per plant S1 vs S0 ↑6.0%; At maturity FGD0-30 vs FGD0 (S1) ↑9.1%; No yield data for S3"

Output Example 5:
"Post-treatment Biomass": "Annual dry matter yield (2023 data) B0AH: 6.52 t/ha; B1AH: 7.22 t/ha; B2AH: 9.16 t/ha; B3AH: 7.42 t/ha",
"Post-treatment Yield": "Alfalfa: 40.0 t/ha (Reclamation area 1, 2020-2023) Wheat: 3.75 t/ha (Reclamation area 2, 2020-2023)",
"Post-treatment Saline-Alkali Land Type": "Slightly saline-alkali land",
"Post-treatment Electrical Conductivity (EC)": "1.2 dS·m⁻¹",
"Post-treatment Total Soluble Salt Content": "1.2 g·kg⁻¹",
"Post-treatment pH": "7.8",
"Post-treatment pH Measurement Method": "5:1 water-soil ratio",
"Post-treatment Exchangeable Sodium Percentage (ESP)": "6.5%",
"Post-treatment Sodium Adsorption Ratio (SAR)": "0~20cm soil layer: 15.00; 20~40cm soil layer: 10.00; 40~60cm soil layer: 5.00",
"Post-treatment Cation Exchange Capacity (CEC)": "14.00 cmol(+)/kg",
"Post-treatment Sodium Ion (Na⁺) Content": "4.00 mmol/L",
"Post-treatment Calcium Ion (Ca²⁺) Content": "10.00 mmol/L",
"Post-treatment Magnesium Ion (Mg²⁺) Content": "1.50 mmol/L",
"Post-treatment Chloride Ion (Cl⁻) Content": "3.50 mmol/L",
"Post-treatment Sulfate Ion (SO₄²⁻) Content": "6.50 mmol/L",
"Post-treatment Bicarbonate (HCO₃⁻) Content": "0.08 mmol/L",
"Post-treatment Carbonate (CO₃²⁻) Content": "0.10 mmol/L",
"Post-treatment Soil Organic Matter (SOM) Content": "2.00 g/kg",
"Post-treatment Soil Texture": "Clay 60.00%, Silt 30.00%, Sand 10.00%",
"Post-treatment Soil Bulk Density": "1.20 g·cm⁻³",
"Post-treatment Total Porosity": "52%",
"Post-treatment Soil Temperature": "24℃",
"Post-treatment Calcium Carbonate (CaCO₃) Content": "6.00 g·kg⁻¹",
"Post-treatment Available Phosphorus (P) Content": "15 mg/kg",
"Post-treatment Available Potassium (K) Content": "25 mg/kg",
"Post-treatment Total Nitrogen (N) Content": "0.20 mg/kg",
"Post-treatment Ammonium Nitrogen (NH₄⁺-N) Content": "0.07 mg/kg",
"Post-treatment Nitrate Nitrogen (NO₃⁻-N) Content": "0.13 mg/kg",
"Post-treatment Trace Element Content": "Not provided",
"Post-treatment Field Capacity (FC)": "32%",
"Post-treatment Permanent Wilting Point (PWP)": "0~20cm 10.00%; 20~40cm 9.00%; 40~60cm 8.00%; 60~80cm 7.00%; 80~100cm 6.50%",
"Post-treatment Soil Water Content (SWC)": "Pre-sowing average for 0~100cm: 13.00%",
"Post-treatment Saturated Hydraulic Conductivity (Ks)": "1.5 cm·d⁻¹",
"Post-treatment Capillary Rise Height": "Not provided",
"Post-treatment Groundwater Depth": "2.5 m",
"Post-treatment Irrigation Water EC": "1.0 dS/m",
"Post-treatment Annual Evaporation/Precipitation Ratio": "3.00:1"

Output Example 6:
"Crop Yield Increase Rate": "CK (Treatment 1): 0; Treatment 2: 6.62%; Treatment 3: 16.78%; Treatment 4: 20.52%",
"Soil Salinity/Alkalinity Reduction Rate": "Soil salinity (harvest, 194 days after sowing): CK: 0 (decreased to 44.54% of initial value, but CK had no treatment, calculated relative to initial value); Various combined treatments: all calculated as (Initial value - Harvest value) / Initial value × 100%. Since initial value was 1.25 g/kg, harvest values ranged from 1.6-3.8 g/kg (regreening period), later decreased to 44.54% of initial value, thus reduction rate is (1.25 - 1.25×44.54%)/1.25×100% = 55.46%; Soil alkalinity (pH): CK: 0; LDLG, LDMG, LDHG, etc.: 2.23-5.87% reduction",
"Amendment Input-Output Ratio": "Treatment 2: 98.6 yuan/mu ÷ 6 yuan/mu ≈ 16.43; Treatment 3: 249.9 yuan/mu ÷ 75.2 yuan/mu ≈ 3.32; Treatment 4: 305.6 yuan/mu ÷ 109.8 yuan/mu ≈ 2.78",
"Soil Organic Carbon (SOC) Increment": "0.365-0.73 g/kg (0~20cm soil layer)",
"Microbial Quantity and Diversity": "Bacterial absolute abundance (16S rRNA gene copy number): CK 5.80×10⁸; T1 1.16×10⁹; T2 1.32×10⁹; T3 1.58×10⁹; T4 1.79×10⁹. Bacterial α-diversity indices: (Chao1 index, Shannon index, Simpson index, Coverage) CK 957.19±70.66b 9.10±0.09c 0.0029±0.01a 0.9998; T1 1057.25±18.49ab 9.23±0.01b 0.0027±0.00bc 0.9997; T2 1111.96±55.81ab 9.25±0.02ab 0.0028±0.00ab 0.9997; T3 1110.15±62.43ab 9.32±0.09a 0.0025±0.00c 0.9997; T4 1161.73±38.90a 9.32±0.03a 0.0025±0.00c 0.9997. Bacterial community structure: Lysobacter, Sphingomonas, Luteimonas, Pelagibius, Nitrospira."


Please strictly extract information objectively based on the context. If contextual information is needed to understand certain indicators, please extract and return the explanatory information related to the indicators along with them.

Please strictly ensure that the number and order of extracted indicators correspond exactly to the given indicator list.

Please return directly in JSON format, without any other explanations, and do not add identifiers like ```json at the beginning.
"""


# Large Model Training QA Pair Generation Prompt
english_alpaca_prompt_template = """
Please based on the following information extracted from the paper, understand and integrate the various indicator information, create a question-answer pair suitable for training large models in the llama factory framework in Alpaca format.
Only extract informative indicators; skip indicators that are not mentioned or not clearly mentioned.
Please generate a JSON object containing "instruction", "input", "output".

Paper information:
{paper_info_str}

Please ensure:
1. instruction is a clear question or instruction, asking for management measures given the saline-alkali land conditions.
2. input is optional contextual information, representing soil indicators before treatment of saline-alkali land and information such as planted crops. The format is plain text, do not include any JSON format content.
3. output is a detailed response to the instruction, including the management measures taken and costs, soil indicators after treatment, crop yield, and other management effects. The format is plain text, do not include any JSON format content. It can include some thinking and reasoning process, the tone should be advisory, not too rigid. Note: For some indicators that use referential information such as Reagent 1, Reagent 2, T1, T2, etc., please understand them in the context of other indicators, then replace the referential information with its original information (e.g., replace T1 with desulfurization gypsum improvement, T2 with wheat straw biochar, etc.) to facilitate subsequent semantic understanding.
4. Strictly follow the paper information for objective extraction, no additional explanations needed.

Please directly return the JSON format, do not include any other explanations, and do not add identifiers like ```json at the beginning.
"""

# Large Model Multi-turn Training QA Pair Generation Prompt
english_sharegpt_prompt_template = """
# Role Setting
You are a saline-alkali land management expert with extensive knowledge and practical experience in soil improvement.

# Task Objective
Based on the provided saline-alkali land indicator data, generate a multi-turn dialogue question-answer pair in ShareGPT format that can be directly used for large model training.

# Dialogue Flow Requirements
1. **First Round**: User provides partial soil indicator information (select a few key indicators)
2. **Second Round**: AI asks for missing key information (e.g., crop type, specific amendment preferences, etc.)
3. **Third Round**: User supplements the required information
4. **Fourth Round**: 
    If the information provided by the user is relatively complete, then AI gives complete management recommendations, including:
    - Recommended specific measures
    - Predicted management effects
    - Expected crop yield
    - Soil improvement effects
    If the information is still incomplete, then AI continues to ask for missing key indicators until there is enough information to provide recommendations.

# Data Extraction Principles
- Selectively use indicators from the input data, do not list all data
- Focus on: salt content, pH value, organic matter, electrical conductivity EC value, crop type, management measures, management effects, etc.
- For missing data, reasonably ask or skip in the dialogue
- Ensure the dialogue content is natural and smooth, conforming to real communication scenarios

# Input Data
{paper_info_str}

# Output Format Requirements
Please directly return the JSON format, do not include any other explanations, and do not add identifiers like ```json at the beginning.
Output example:
{{
"conversations": [
    {{
    "from": "human",
    "value": "Initial soil indicator information provided by the user"
    }},
    {{
    "from": "gpt",
    "value": "AI asks for missing key information"
    }},
    {{
    "from": "human",
    "value": "Detailed information supplemented by the user"
    }},
    {{
    "from": "gpt",
    "value": "Reasoning process: Briefly analyze soil problems\nRecommended measures: Specific management plan\nPredicted after treatment: Yield, soil improvement effects, and other specific data"
    }}
]
}}
"""