#!/usr/bin/env python3
"""
Generate Additional Plain-Language Reports

Generates three additional reports from the analysis data:
1. SIMPLE_REPORT_{Name}.md - Quick reference, 10 sections
2. COMPLETE_EASY_REPORT_{Name}.md - Full plain-language for common person
3. SWOT_REPORT_{Name}.md - SWOT genetic analysis (shareable)
"""

from datetime import datetime
from pathlib import Path
from collections import defaultdict


# =============================================================================
# KNOWLEDGE BASE — Plain language interpretations for each gene/status
# =============================================================================

GENE_KNOWLEDGE = {
    # DRUG METABOLISM — HIGH IMPACT
    ("DPYD", "intermediate"): {
        "title": "DPYD Gene — Chemotherapy Sensitivity",
        "simple": "The body breaks down certain cancer drugs (5-FU, capecitabine) slower than normal",
        "risk": "Serious toxicity if given standard doses of these chemotherapy drugs",
        "action": "If cancer treatment is ever needed, the dose of fluoropyrimidine drugs must be reduced by 50%. Always inform oncologists about this variant",
        "food": None,
        "swot": "weakness",
        "severity": "Critical if needed",
        "manageable": "No fix — must reduce dose. Lifelong alert",
    },
    ("HLA-B", "carrier"): {
        "title": "HLA-B Gene — Abacavir Allergy",
        "simple": "Carrier of HLA-B*5701, which causes severe allergic reaction to the HIV drug abacavir",
        "risk": "Life-threatening hypersensitivity reaction",
        "action": "Abacavir must NEVER be prescribed. This should be noted in all medical records",
        "food": None,
        "swot": "weakness",
        "severity": "Life-threatening if given",
        "manageable": "No fix — drug must never be given",
    },
    ("CYP2C19", "intermediate"): {
        "title": "CYP2C19 Gene — Blood Thinner Response",
        "simple": "The body is an intermediate metabolizer of certain drugs. The blood thinner clopidogrel (Plavix) will be less effective",
        "risk": "Reduced effectiveness of clopidogrel if ever prescribed",
        "action": "If a blood thinner is needed, doctors should consider alternatives like prasugrel or ticagrelor instead of clopidogrel",
        "food": None,
        "swot": "weakness",
        "severity": "High if needed",
        "manageable": "Use alternative blood thinners",
    },
    ("CYP2C19", "rapid"): {
        "title": "CYP2C19 Gene — Rapid Drug Metabolism",
        "simple": "The body breaks down PPIs (acid reflux drugs) and some antidepressants faster than normal",
        "risk": "Standard doses of PPIs may not work well enough",
        "action": "If prescribed omeprazole or similar, may need higher dose. Inform prescribers about CYP2C19 status",
        "food": None,
        "swot": "neutral",
        "severity": "Moderate",
        "manageable": "Adjust dose with doctor",
    },

    # CARDIOVASCULAR
    ("APOE", "e4_carrier"): {
        "title": "APOE Gene — Cholesterol & Brain Health",
        "simple": "Carries one copy of the APOE e4 variant. Associated with higher cholesterol levels, increased heart disease risk, and higher Alzheimer's risk later in life",
        "risk": "Moderate — increased cardiovascular and Alzheimer's risk",
        "action": "Heart-healthy diet from childhood, regular cholesterol monitoring, stay physically active, cognitive engagement throughout life",
        "food": "Eat more fish, nuts, olive oil, vegetables. Eat less fried food, ghee/butter, red meat",
        "swot": "weakness",
        "severity": "Moderate-High (long-term)",
        "manageable": "Partially — diet, exercise, monitoring",
    },
    ("AGT", "elevated"): {
        "title": "AGT Gene — Blood Pressure",
        "simple": "Higher levels of angiotensinogen protein, which raises blood pressure",
        "risk": "Moderate — increased hypertension risk",
        "action": "Limit salt intake, regular blood pressure monitoring, maintain healthy weight, DASH-style diet",
        "food": "Reduce salt in cooking. Use herbs/spices instead. Eat potassium-rich foods: bananas, coconut water, spinach",
        "swot": "weakness",
        "severity": "Moderate",
        "manageable": "Yes — low salt, exercise, monitoring",
    },
    ("ACE", "low"): {
        "title": "ACE Gene — Blood Pressure Protection",
        "simple": "Lower ACE enzyme activity — naturally tends toward lower blood pressure and better endurance",
        "risk": "Positive finding — lower BP tendency",
        "action": "This is beneficial. Good for endurance sports",
        "food": None,
        "swot": "strength",
        "severity": None,
        "manageable": None,
    },
    ("ADRB1", "heterozygous"): {
        "title": "ADRB1 Gene — Beta-Blocker Response",
        "simple": "Intermediate response to beta-blocker medications",
        "risk": "Informational only",
        "action": "Standard beta-blocker dosing likely appropriate",
        "food": None,
        "swot": "neutral",
        "severity": None,
        "manageable": None,
    },

    # NUTRITION & VITAMINS
    ("TCF7L2", "increased"): {
        "title": "TCF7L2 Gene — Diabetes Risk",
        "simple": "1.4 times higher risk of developing Type 2 diabetes compared to average",
        "risk": "Moderate",
        "action": "Limit refined carbohydrates and sugar, regular physical activity, annual fasting glucose or HbA1c testing in adulthood",
        "food": "Limit sweets, sugary drinks, white rice, maida. Choose whole grains, millets, brown rice",
        "swot": "weakness",
        "severity": "Moderate",
        "manageable": "Yes — low sugar, exercise",
    },
    ("FTO", "increased"): {
        "title": "FTO Gene — Weight Management",
        "simple": "1.3 times higher tendency toward weight gain",
        "risk": "Low to moderate",
        "action": "Higher protein diet, regular physical activity, monitor weight from childhood",
        "food": "Higher protein diet helps feel full longer. Don't use food as reward",
        "swot": "weakness",
        "severity": "Low-Moderate",
        "manageable": "Yes — diet and exercise",
    },
    ("BCMO1", "reduced"): {
        "title": "BCMO1 Gene — Vitamin A Conversion",
        "simple": "About 30% reduced ability to convert beta-carotene (from carrots, sweet potato) into active vitamin A",
        "risk": "Low-moderate",
        "action": "Include preformed vitamin A sources: eggs, dairy, liver, fatty fish. Don't rely only on plant sources",
        "food": "Eggs, dairy, ghee, fish for direct Vitamin A. Still eat carrots for other benefits",
        "swot": "weakness",
        "severity": "Low-Moderate",
        "manageable": "Yes — eat eggs, dairy, fish",
    },

    # METHYLATION
    ("MTRR", "significantly_reduced"): {
        "title": "MTRR Gene — Vitamin B12 Processing",
        "simple": "The body recycles vitamin B12 less efficiently. May have functional B12 deficiency even if blood levels appear normal",
        "risk": "Moderate",
        "action": "Use methylcobalamin form of B12, eat B12-rich foods (meat, fish, eggs, dairy), test Serum B12 + MMA",
        "food": "Eggs, milk, curd, fish, meat for B12. If supplementing, use methylcobalamin (NOT cyanocobalamin)",
        "swot": "weakness",
        "severity": "Moderate",
        "manageable": "Yes — methylcobalamin supplement",
    },
    ("MTHFR", "reduced"): {
        "title": "MTHFR Gene — Folate Processing",
        "simple": "Mildly reduced ability to process folic acid into its active form (methylfolate)",
        "risk": "Low (one copy affected)",
        "action": "Eat folate-rich foods (leafy greens, lentils, beans). If supplementing, methylfolate is preferred over folic acid",
        "food": "Leafy greens (spinach, methi), lentils, beans. Use methylfolate if supplementing",
        "swot": "weakness",
        "severity": "Low",
        "manageable": "Yes — diet and methylfolate",
    },
    ("PEMT", "reduced"): {
        "title": "PEMT Gene — Choline Requirement",
        "simple": "Higher dietary choline requirement due to reduced PEMT enzyme activity",
        "risk": "Low-moderate",
        "action": "Increase choline-rich foods: eggs (especially yolks), liver, beef, fish",
        "food": "Eggs are the best source — 2 eggs per day. Also: liver, chicken, fish, soybeans",
        "swot": "weakness",
        "severity": "Low-Moderate",
        "manageable": "Yes — eat eggs daily",
    },

    # DETOXIFICATION
    ("GSTP1", "significantly_reduced"): {
        "title": "GSTP1 Gene — Glutathione Function",
        "simple": "Reduced glutathione conjugation (Phase II detox). Body is less efficient at clearing toxins",
        "risk": "Moderate",
        "action": "May benefit from NAC or glutathione support. Eat sulphur-rich vegetables",
        "food": "Broccoli, cauliflower, cabbage, garlic, onion — help the body make glutathione",
        "swot": "weakness",
        "severity": "Moderate",
        "manageable": "Yes — antioxidant-rich diet",
    },
    ("SOD2", "low_activity"): {
        "title": "SOD2 Gene — Antioxidant Defense",
        "simple": "Lower activity of the mitochondrial antioxidant enzyme SOD2",
        "risk": "Moderate",
        "action": "Antioxidant-rich diet: berries, green tea, colourful vegetables",
        "food": "Berries, pomegranate, green tea, colourful vegetables",
        "swot": "weakness",
        "severity": "Moderate",
        "manageable": "Yes — antioxidant diet",
    },
    ("NAT2", "intermediate"): {
        "title": "NAT2 Gene — Drug Processing",
        "simple": "Intermediate acetylator — moderate metabolism of NAT2-processed drugs",
        "risk": "Informational",
        "action": "Standard drug dosing generally appropriate",
        "food": None,
        "swot": "neutral",
        "severity": None,
        "manageable": None,
    },

    # INFLAMMATION
    ("IL6", "high"): {
        "title": "IL-6 Gene — Inflammation",
        "simple": "Higher baseline levels of the inflammatory marker IL-6. Body runs 'hotter' with more inflammation",
        "risk": "Moderate",
        "action": "Anti-inflammatory diet (omega-3, colorful vegetables, turmeric), adequate sleep, regular exercise",
        "food": "Fatty fish (salmon, sardines), turmeric with black pepper, colorful vegetables. Avoid processed foods",
        "swot": "weakness",
        "severity": "Moderate",
        "manageable": "Yes — diet, sleep, omega-3",
    },

    # NEUROTRANSMITTERS
    ("COMT", "intermediate"): {
        "title": "COMT Gene — Brain Chemistry",
        "simple": "Balanced dopamine clearance — the 'Goldilocks' brain profile. Handles stress well without being anxious",
        "risk": "Positive finding",
        "action": "This is beneficial. Good balance of stress response and focus",
        "food": None,
        "swot": "strength",
        "severity": None,
        "manageable": None,
    },

    # CAFFEINE
    ("CYP1A2", "fast"): {
        "title": "CYP1A2 Gene — Caffeine Metabolism",
        "simple": "Fast caffeine metabolizer. Clears caffeine quickly. Lower cardiovascular risk from coffee",
        "risk": "Positive finding",
        "action": "Coffee/tea is generally safe and may be protective for the heart",
        "food": None,
        "swot": "strength",
        "severity": None,
        "manageable": None,
    },
    ("ADORA2A", "intermediate"): {
        "title": "ADORA2A Gene — Caffeine Sensitivity",
        "simple": "Intermediate caffeine-anxiety response",
        "risk": "Informational",
        "action": "Moderate caffeine intake is fine",
        "food": None,
        "swot": "neutral",
        "severity": None,
        "manageable": None,
    },
    ("ADORA2A", "normal"): {
        "title": "ADORA2A Gene — Caffeine Sensitivity",
        "simple": "Normal caffeine sensitivity",
        "risk": "Informational",
        "action": "No special precautions needed",
        "food": None,
        "swot": "neutral",
        "severity": None,
        "manageable": None,
    },

    # FITNESS
    ("ACTN3", "mixed"): {
        "title": "ACTN3 Gene — Muscle Type",
        "simple": "Mixed muscle fiber type — good for both power and endurance activities. Can excel at any sport",
        "risk": "Positive finding",
        "action": "Train for both power and endurance based on goals",
        "food": None,
        "swot": "strength",
        "severity": None,
        "manageable": None,
    },
    ("ADRB2", "heterozygous"): {
        "title": "ADRB2 Gene — Exercise Response",
        "simple": "Intermediate exercise response",
        "risk": "Informational",
        "action": "Standard exercise recommendations apply",
        "food": None,
        "swot": "neutral",
        "severity": None,
        "manageable": None,
    },

    # ALCOHOL
    ("ADH1B", "slow"): {
        "title": "ADH1B Gene — Alcohol Metabolism",
        "simple": "Slower alcohol metabolism. Alcohol effects last longer",
        "risk": "Low",
        "action": "Moderate alcohol consumption. Effects last longer than average",
        "food": None,
        "swot": "neutral",
        "severity": None,
        "manageable": None,
    },

    # AUTOIMMUNE
    ("STAT4", "increased"): {
        "title": "STAT4 Gene — Autoimmune Risk",
        "simple": "Slightly increased risk of rheumatoid arthritis and lupus",
        "risk": "Low",
        "action": "Be aware if joint pain or unusual symptoms appear",
        "food": None,
        "swot": "weakness",
        "severity": "Low",
        "manageable": "Monitor symptoms",
    },
    ("PTPN22", "normal"): {
        "title": "PTPN22 Gene — Autoimmune Baseline",
        "simple": "Normal autoimmune risk — the biggest autoimmune risk gene is completely clear",
        "risk": "Positive finding",
        "action": "No special precautions needed",
        "food": None,
        "swot": "strength",
        "severity": None,
        "manageable": None,
    },

    # LONGEVITY
    ("TP53", "arg72"): {
        "title": "TP53 Gene — Cancer Protection",
        "simple": "Standard cancer screening appropriate for age. Normal TP53 function",
        "risk": "Informational",
        "action": "Standard cancer screening by age",
        "food": None,
        "swot": "neutral",
        "severity": None,
        "manageable": None,
    },

    # DRUG METABOLISM — OTHER
    ("CYP3A5", "intermediate"): {
        "title": "CYP3A5 Gene — Drug Metabolism",
        "simple": "Intermediate CYP3A5 expression — normal drug processing for most medicines",
        "risk": "Informational",
        "action": "Standard dosing for most drugs",
        "food": None,
        "swot": "neutral",
        "severity": None,
        "manageable": None,
    },

    # =========================================================================
    # INDIAN CARRIER SCREENING — Knowledge entries
    # =========================================================================

    ("HBB", "carrier"): {
        "title": "HBB Gene — Beta-Thalassemia Carrier",
        "simple": "Carrier of beta-thalassemia trait. The person has ONE copy of a thalassemia mutation. No disease symptoms, but can pass to children",
        "risk": "If BOTH parents are carriers: 25% chance of thalassemia major in each child",
        "action": "MANDATORY partner screening with HPLC. Genetic counseling before pregnancy. If both carriers, prenatal diagnosis (CVS at 11-12 weeks) available",
        "food": "Carrier often has low MCV/MCH on CBC — this is NOT iron deficiency. Do not give iron unless ferritin is actually low",
        "swot": "weakness",
        "severity": "Critical for family planning",
        "manageable": "No fix for carrier status — manage through partner screening and counseling",
    },
    ("HBB", "carrier_HbE"): {
        "title": "HBB Gene — Hemoglobin E Carrier",
        "simple": "Carrier of Hemoglobin E variant. Common in NE India. Mild or no anemia. But HbE + beta-thal partner = severe disease in child",
        "risk": "If partner has beta-thalassemia trait: child can have HbE/beta-thal (severe)",
        "action": "Partner must be tested for beta-thalassemia. HbE alone is mild",
        "food": None,
        "swot": "weakness",
        "severity": "Moderate — depends on partner status",
        "manageable": "Partner screening essential",
    },
    ("HBB", "carrier_HbS"): {
        "title": "HBB Gene — Sickle Cell Trait",
        "simple": "Carrier of sickle cell trait (HbAS). No disease. Provides malaria protection. Common in tribal populations of central India",
        "risk": "If both parents HbAS: 25% chance of sickle cell disease in each child",
        "action": "Partner screening. Avoid extreme dehydration. Inform doctors before surgery (rare complications under anesthesia)",
        "food": None,
        "swot": "weakness",
        "severity": "Low for carrier, critical for family planning",
        "manageable": "Partner screening and genetic counseling",
    },
    ("G6PD", "carrier_female"): {
        "title": "G6PD Gene — G6PD Deficiency Carrier (Female)",
        "simple": "Female carrier of G6PD deficiency. Usually no symptoms due to X-inactivation. If baby is MALE, 50% chance of G6PD deficiency",
        "risk": "Male child has 50% chance of full G6PD deficiency. Affected males must avoid certain drugs and fava beans",
        "action": "Newborn screening for G6PD. Drug avoidance card for affected child: primaquine, dapsone, nitrofurantoin, sulfonamides, mothballs (naphthalene)",
        "food": "Affected individuals must AVOID: fava beans (broad beans), tonic water. No mothballs in home",
        "swot": "weakness",
        "severity": "Moderate — manageable with awareness",
        "manageable": "Yes — avoid trigger drugs and foods. Educate family",
    },
    ("G6PD", "deficient"): {
        "title": "G6PD Gene — G6PD Deficiency",
        "simple": "G6PD enzyme deficiency confirmed. Red blood cells break down (hemolysis) when exposed to certain drugs, infections, or foods",
        "risk": "Hemolytic crisis with trigger drugs or fava beans. Neonatal jaundice common",
        "action": "Drug avoidance card essential. Alert neonatologist for early jaundice monitoring. Avoid: primaquine, dapsone, nitrofurantoin, methylene blue, naphthalene",
        "food": "AVOID fava beans. Avoid mothballs. No herbal medicines without checking first",
        "swot": "weakness",
        "severity": "High — but fully manageable",
        "manageable": "Yes — drug and food avoidance list. Lifelong awareness",
    },
    ("GJB2 (Connexin 26)", "carrier"): {
        "title": "GJB2 Gene — Hearing Loss Carrier",
        "simple": "Carrier of the most common genetic hearing loss mutation in India (W24X). Normal hearing. But if both parents are carriers: 25% chance of profound hearing loss in child",
        "risk": "Congenital deafness if both parents are carriers",
        "action": "Partner screening for GJB2. Newborn hearing test (OAE/BERA) at birth. If child is affected: cochlear implant evaluation before 12 months for best speech outcome",
        "food": None,
        "swot": "weakness",
        "severity": "High for family planning",
        "manageable": "Early intervention (cochlear implant) gives excellent outcomes",
    },
    ("UGT1A1", "reduced"): {
        "title": "UGT1A1 Gene — Neonatal Jaundice Risk",
        "simple": "Reduced bilirubin processing enzyme. Newborn may develop more significant jaundice after birth",
        "risk": "Higher risk of neonatal hyperbilirubinemia requiring phototherapy",
        "action": "Alert neonatologist at delivery. Early bilirubin monitoring (within 24 hrs). Low threshold for phototherapy",
        "food": None,
        "swot": "weakness",
        "severity": "Moderate — treatable with phototherapy",
        "manageable": "Yes — early monitoring and phototherapy",
    },
    ("UGT1A1", "gilbert_syndrome"): {
        "title": "UGT1A1 Gene — Gilbert Syndrome / Severe Neonatal Jaundice Risk",
        "simple": "Significantly reduced bilirubin processing. High risk of severe neonatal jaundice",
        "risk": "May need extended phototherapy or exchange transfusion in severe cases",
        "action": "ALERT neonatologist before delivery. Plan for early and frequent bilirubin checks. Keep baby well-hydrated with frequent feeds",
        "food": None,
        "swot": "weakness",
        "severity": "High in newborn period — treatable",
        "manageable": "Yes — with early monitoring and phototherapy",
    },

    # INDIAN NUTRITION — Knowledge entries
    ("LCT/MCM6", "lactose_intolerant"): {
        "title": "Lactose Intolerance Gene",
        "simple": "Cannot digest milk sugar (lactose). Very common in India (60-80% of population). Not an illness — it's the normal human default",
        "risk": "Bloating, gas, diarrhea from milk. Does NOT mean avoid all dairy",
        "action": "Use curd/yoghurt (fermented = lower lactose) instead of plain milk. Paneer and ghee are fine (low lactose). If pregnant, ensure calcium from curd, ragi, sesame, greens",
        "food": "OK: Curd, paneer, ghee, aged cheese. LIMIT: Plain milk, ice cream, kulfi. FOR CALCIUM: ragi, sesame seeds, amaranth, dark greens",
        "swot": "weakness",
        "severity": "Low — just dietary adjustment",
        "manageable": "Yes — curd instead of milk, calcium-rich foods",
    },
    ("GC (VDBP)", "low_binding"): {
        "title": "Vitamin D Binding Protein — Low Efficiency",
        "simple": "Vitamin D transport in blood is less efficient. Combined with Indian lifestyle (less sun exposure, darker skin): very high risk of Vitamin D deficiency",
        "risk": "Critical during pregnancy — Vitamin D deficiency affects fetal bone development, immune system, and brain development",
        "action": "Supplement 2000 IU Vitamin D3 daily during pregnancy (minimum). Check 25-OH Vitamin D levels every trimester. Target: >30 ng/mL",
        "food": "Egg yolks, fatty fish, fortified milk. But supplementation is essential — food alone is not enough for this genotype",
        "swot": "weakness",
        "severity": "Moderate-High during pregnancy",
        "manageable": "Yes — Vitamin D3 supplementation",
    },
    ("TMPRSS6", "low_iron"): {
        "title": "TMPRSS6 Gene — Iron Absorption Difficulty",
        "simple": "Body absorbs iron less efficiently from food. Combined with Indian vegetarian diet: high risk of iron deficiency anemia",
        "risk": "Iron deficiency anemia — affects fetal brain development, maternal health, increases preterm birth risk",
        "action": "Iron supplementation during pregnancy (as per OB-GYN). Monitor serum ferritin (not just hemoglobin). Eat iron-rich foods with Vitamin C. Avoid tea/coffee with meals",
        "food": "Iron-rich: jaggery, green leafy (spinach, methi), ragi, dates, beetroot. Eat with lemon/amla for absorption. Avoid tea 1hr before/after meals",
        "swot": "weakness",
        "severity": "Moderate-High during pregnancy",
        "manageable": "Yes — supplementation + diet",
    },
    ("MTHFR", "reduced"): {
        "title": "MTHFR Gene — Folate Processing",
        "simple": "Mildly reduced ability to process folic acid into its active form (methylfolate)",
        "risk": "Low (one copy affected)",
        "action": "Eat folate-rich foods (leafy greens, lentils, beans). If supplementing, methylfolate is preferred over folic acid",
        "food": "Leafy greens (spinach, methi), lentils, beans. Use methylfolate if supplementing",
        "swot": "weakness",
        "severity": "Low",
        "manageable": "Yes — diet and methylfolate",
    },
    ("MTHFR", "mildly_reduced"): {
        "title": "MTHFR A1298C Gene — Folate Processing",
        "simple": "Mildly reduced folate metabolism at a second MTHFR position. India has high neural tube defect rates (4-11 per 1000 births), so folate optimization matters",
        "risk": "Low to moderate, especially combined with other MTHFR variants",
        "action": "Use methylfolate 800mcg during pregnancy (not regular folic acid). Start 3 months before conception",
        "food": "Spinach, methi, lentils, moong dal, beans, fortified cereals",
        "swot": "weakness",
        "severity": "Low-Moderate",
        "manageable": "Yes — methylfolate supplementation",
    },
}


def _get_knowledge(gene, status):
    """Get knowledge base entry for a gene/status combo, with fallback."""
    key = (gene, status)
    if key in GENE_KNOWLEDGE:
        return GENE_KNOWLEDGE[key]
    return None


def _safe_name(name):
    """Convert subject name to safe filename part."""
    if not name:
        return "Subject"
    return name.replace(" ", "_").replace("/", "_")


def _categorize_findings(findings):
    """Categorize findings by importance."""
    critical = [f for f in findings if f['magnitude'] >= 3]
    moderate = [f for f in findings if f['magnitude'] == 2]
    low = [f for f in findings if f['magnitude'] <= 1]
    return critical, moderate, low


def _get_drug_warnings(findings, pharmgkb):
    """Extract drug warnings from findings and PharmGKB."""
    must_avoid = []
    dose_adjust = []
    monitor = []

    for f in findings:
        gene = f['gene']
        status = f['status']
        if gene == 'HLA-B' and status == 'carrier':
            must_avoid.append({
                'drug': 'Abacavir (HIV drug)',
                'reason': 'HLA-B*5701 carrier — severe allergic reaction risk'
            })
        elif gene == 'DPYD' and f['magnitude'] >= 3:
            dose_adjust.append({
                'drug': '5-FU / Capecitabine (chemo)',
                'adjustment': '50% dose reduction',
                'reason': 'DPYD intermediate metabolizer'
            })
        elif gene == 'CYP2C19' and status == 'intermediate':
            dose_adjust.append({
                'drug': 'Clopidogrel (blood thinner)',
                'adjustment': 'Use alternative drug',
                'reason': 'CYP2C19 intermediate — drug less effective'
            })
        elif gene == 'CYP2C19' and status == 'rapid':
            dose_adjust.append({
                'drug': 'Omeprazole / PPIs (acid reflux)',
                'adjustment': 'May need higher dose',
                'reason': 'CYP2C19*17 rapid metabolizer'
            })

    for p in pharmgkb:
        if 'warfarin' in p.get('drugs', '').lower():
            dose_adjust.append({
                'drug': 'Warfarin (blood thinner)',
                'adjustment': 'Dose adjustment needed',
                'reason': f"{p['gene']} variant affects dosing"
            })
            break

    for p in pharmgkb:
        drug = p.get('drugs', '')
        gene = p.get('gene', '')
        if gene in ('DPYD', 'HLA-B', 'CYP2C19', 'VKORC1', ''):
            continue
        monitor.append({
            'drug': drug,
            'note': f"{gene} variant — may affect response"
        })

    return must_avoid, dose_adjust, monitor


# =============================================================================
# SIMPLE REPORT GENERATOR
# =============================================================================

def generate_simple_report(health_results, disease_findings, disease_stats,
                           output_dir, subject_name):
    """Generate SIMPLE_REPORT_{name}.md"""
    findings = health_results['findings']
    pharmgkb = health_results['pharmgkb_findings']
    summary = health_results['summary']
    safe = _safe_name(subject_name)
    now = datetime.now().strftime("%d %B %Y")

    critical, moderate, low = _categorize_findings(findings)
    must_avoid, dose_adjust, monitor = _get_drug_warnings(findings, pharmgkb)

    r = []
    r.append(f"# Genetic Health Report\n")
    r.append(f"**Name:** {subject_name or 'Subject'}")
    r.append(f"**Date:** {now}")
    r.append(f"**Total Variants Analyzed:** {summary['total_snps']:,}")
    r.append(f"\n---\n")

    # SECTION 1: Overall
    r.append("## Overall Result\n")
    path_count = len(disease_findings.get('pathogenic', [])) if disease_findings else 0
    if path_count == 0 or all(f.get('stars', 0) == 0 for f in disease_findings.get('pathogenic', [])):
        r.append("The genetic analysis did not find any high-confidence disease-causing variants. This is a reassuring result.\n")
    else:
        r.append(f"The analysis found {path_count} potentially significant variant(s). Review the details below.\n")

    # SECTION 2: Critical Drug Reactions
    r.append("---\n\n## SECTION 1: Critical Drug Reactions\n")
    r.append("**This is the most important section. Keep this information for life.**\n")

    if must_avoid:
        r.append("### MUST AVOID\n")
        r.append("| Medicine | Reason |")
        r.append("|----------|--------|")
        for d in must_avoid:
            r.append(f"| **{d['drug']}** | {d['reason']} |")
        r.append("")

    if dose_adjust:
        r.append("### DOSE ADJUSTMENT NEEDED\n")
        r.append("| Medicine | Adjustment | Reason |")
        r.append("|----------|-----------|--------|")
        for d in dose_adjust:
            r.append(f"| **{d['drug']}** | {d['adjustment']} | {d['reason']} |")
        r.append("")

    if monitor:
        r.append("### MONITOR CLOSELY\n")
        r.append("| Medicine | Note |")
        r.append("|----------|------|")
        for d in monitor:
            r.append(f"| {d['drug']} | {d['note']} |")
        r.append("")

    # SECTION 3-6: Findings by category
    categories = defaultdict(list)
    for f in findings:
        cat = f['category']
        categories[cat].append(f)

    section_num = 2
    for cat_name, cat_label in [
        ("Cardiovascular", "Heart & Blood Pressure"),
        ("Nutrition", "Sugar, Weight & Nutrition"),
        ("Methylation", "Vitamins & Methylation"),
        ("Detoxification", "Detoxification & Antioxidants"),
        ("Inflammation", "Inflammation"),
        ("Neurotransmitters", "Brain Chemistry"),
        ("Fitness", "Fitness & Muscles"),
        ("Caffeine Response", "Caffeine"),
        ("Autoimmune", "Autoimmune"),
        ("Alcohol", "Alcohol"),
        ("Longevity", "Longevity"),
    ]:
        if cat_name in categories:
            section_num += 1
            r.append(f"---\n\n## SECTION {section_num}: {cat_label}\n")
            for f in categories[cat_name]:
                kb = _get_knowledge(f['gene'], f['status'])
                if kb:
                    r.append(f"### {kb['title']}\n")
                    r.append(f"- **What it means:** {kb['simple']}")
                    r.append(f"- **Genotype:** {f['genotype']} at {f['rsid']}")
                    r.append(f"- **Action:** {kb['action']}")
                    if kb.get('food'):
                        r.append(f"- **Food tip:** {kb['food']}")
                    r.append("")
                else:
                    r.append(f"### {f['gene']} ({f['rsid']})\n")
                    r.append(f"- **Genotype:** {f['genotype']} | **Status:** {f['status']}")
                    r.append(f"- {f['description']}")
                    r.append("")

    # Disease Screening
    section_num += 1
    r.append(f"---\n\n## SECTION {section_num}: Disease Screening\n")
    if disease_findings:
        total_clinvar = disease_stats.get('total_clinvar', 0)
        r.append(f"Checked against **{total_clinvar:,}** known disease variants.\n")

        real_pathogenic = [f for f in disease_findings.get('pathogenic', [])
                          if f.get('stars', 0) >= 2]
        if not real_pathogenic:
            r.append("**Result: No high-confidence disease-causing variants found.**\n")
        else:
            for f in real_pathogenic:
                r.append(f"- **{f.get('condition', 'Unknown')}** — {f.get('rsid', '')} ({f.get('stars', 0)} star confidence)")

        protective = disease_findings.get('protective', [])
        if protective:
            r.append("\n### Protective Variants\n")
            for f in protective:
                r.append(f"- {f.get('condition', 'Unknown condition')} — protective")
    else:
        r.append("Disease screening data not available.\n")

    # Recommended Tests
    section_num += 1
    r.append(f"\n---\n\n## SECTION {section_num}: Recommended Tests\n")
    r.append("| Test | Why | How Often |")
    r.append("|------|-----|-----------|")

    test_added = set()
    for f in findings:
        gene = f['gene']
        if gene == 'MTRR' and 'B12' not in test_added:
            r.append("| Serum B12 + MMA | MTRR — check true B12 status | Annually |")
            test_added.add('B12')
        elif gene == 'AGT' and 'BP' not in test_added:
            r.append("| Blood Pressure | AGT — hypertension risk | Regular monitoring |")
            test_added.add('BP')
        elif gene == 'TCF7L2' and 'Sugar' not in test_added:
            r.append("| Fasting Glucose or HbA1c | TCF7L2 — diabetes risk | Annually |")
            test_added.add('Sugar')
        elif gene == 'APOE' and 'Lipid' not in test_added:
            r.append("| Lipid Panel (cholesterol) | APOE e4 — cardiovascular risk | Annually |")
            test_added.add('Lipid')
        elif gene in ('MTRR', 'MTHFR') and 'Homocysteine' not in test_added:
            r.append("| Homocysteine | MTRR + MTHFR — methylation status | Baseline |")
            test_added.add('Homocysteine')
    r.append("")

    # Supplement Guide
    section_num += 1
    r.append(f"---\n\n## SECTION {section_num}: Supplement Guide\n")
    r.append("| Supplement | Amount | Why |")
    r.append("|------------|--------|-----|")
    supp_added = set()
    for f in findings:
        gene = f['gene']
        if gene == 'MTRR' and 'B12' not in supp_added:
            r.append("| Methylcobalamin (B12) | 1000-5000 mcg sublingual | MTRR — impaired B12 recycling |")
            supp_added.add('B12')
        elif gene == 'IL6' and 'Omega3' not in supp_added:
            r.append("| Omega-3 Fish Oil (EPA/DHA) | 2-3 g daily | IL-6 — higher inflammation |")
            supp_added.add('Omega3')
        elif gene == 'PEMT' and 'Choline' not in supp_added:
            r.append("| Phosphatidylcholine or Eggs | 250-500 mg or 2 eggs/day | PEMT — higher choline need |")
            supp_added.add('Choline')
        elif gene == 'BCMO1' and 'VitA' not in supp_added:
            r.append("| Vitamin A (retinol or cod liver oil) | 2500-5000 IU | BCMO1 — poor plant conversion |")
            supp_added.add('VitA')
    r.append("")

    # Diet Guidelines
    section_num += 1
    r.append(f"---\n\n## SECTION {section_num}: Diet Guidelines\n")
    r.append("**Eat More:** Eggs (with yolks), fatty fish, leafy greens, colourful vegetables, curd/yoghurt, nuts, dal/lentils\n")
    r.append("**Eat Less:** White sugar/sweets, white rice/maida, excessive salt, deep fried foods, processed/packaged foods\n")

    # Disclaimer
    r.append("---\n\n## Important Disclaimer\n")
    r.append("This report is for **informational purposes only**. It is NOT a medical diagnosis.")
    r.append("Always consult qualified healthcare professionals before making medical decisions.\n")
    r.append(f"---\n\n*Generated: {now}*\n")

    output_path = Path(output_dir) / f"SIMPLE_REPORT_{safe}.md"
    output_path.write_text("\n".join(r))
    return output_path


# =============================================================================
# COMPLETE EASY REPORT GENERATOR
# =============================================================================

def generate_complete_easy_report(health_results, disease_findings, disease_stats,
                                   output_dir, subject_name):
    """Generate COMPLETE_EASY_REPORT_{name}.md"""
    findings = health_results['findings']
    pharmgkb = health_results['pharmgkb_findings']
    summary = health_results['summary']
    safe = _safe_name(subject_name)
    now = datetime.now().strftime("%d %B %Y")

    critical, moderate, low = _categorize_findings(findings)
    must_avoid, dose_adjust, monitor = _get_drug_warnings(findings, pharmgkb)

    r = []
    r.append(f"# Complete Genetic Report — Easy to Read\n")
    r.append(f"**Name:** {subject_name or 'Subject'}")
    r.append(f"**Date:** {now}")
    r.append(f"**Test Type:** DNA Sequencing")
    r.append(f"**Total DNA Points Checked:** {summary['total_snps']:,}")
    r.append(f"\n---\n")

    # Intro
    r.append("## What Is This Report?\n")
    r.append("We took the DNA test file and checked it against medical databases to find out:")
    r.append("- Will certain medicines be **dangerous**?")
    r.append("- Is there any **disease risk** hidden in the DNA?")
    r.append("- What **vitamins and food** will the body need more of?")
    r.append("- How does the body handle **everyday things** like caffeine, inflammation, blood pressure?\n")
    r.append(f"This report found **{len(findings)} meaningful changes** out of {summary['total_snps']:,} checked.\n")

    # BIG PICTURE
    r.append("---\n\n## THE BIG PICTURE\n")
    r.append("### The Good News\n")

    real_pathogenic = []
    if disease_findings:
        real_pathogenic = [f for f in disease_findings.get('pathogenic', [])
                          if f.get('stars', 0) >= 2]

    if not real_pathogenic:
        r.append("- **No serious genetic disease was found**")

    protective = disease_findings.get('protective', []) if disease_findings else []
    if protective:
        for p in protective:
            r.append(f"- **Protective variant found** — {p.get('condition', 'disease resistance')}")

    strengths = [f for f in findings if _get_knowledge(f['gene'], f['status']) and
                 _get_knowledge(f['gene'], f['status'])['swot'] == 'strength']
    for s in strengths:
        kb = _get_knowledge(s['gene'], s['status'])
        r.append(f"- {kb['simple']}")

    r.append("\n### What Needs Attention\n")
    if must_avoid or dose_adjust:
        r.append(f"- **{len(must_avoid) + len(dose_adjust)} medicine warnings** — certain drugs should be avoided or adjusted")
    weakness_count = len([f for f in findings if _get_knowledge(f['gene'], f['status']) and
                          _get_knowledge(f['gene'], f['status'])['swot'] == 'weakness'])
    if weakness_count:
        r.append(f"- **{weakness_count} genetic variants** need long-term lifestyle management")

    # PART 1: Medicine Warnings
    r.append("\n---\n\n## PART 1: Medicine Warnings\n")
    r.append("**This is the most important section. Keep this information for life.**\n")

    if must_avoid:
        r.append("### DANGER — Never Give These Medicines\n")
        r.append("| Medicine | Used For | Why It's Dangerous |")
        r.append("|----------|---------|-------------------|")
        for d in must_avoid:
            r.append(f"| **{d['drug']}** | See note | {d['reason']} |")
        r.append("")

    if dose_adjust:
        r.append("### CAUTION — These Medicines Need Dose Changes\n")
        r.append("| Medicine | Adjustment | Reason |")
        r.append("|----------|-----------|--------|")
        for d in dose_adjust:
            r.append(f"| **{d['drug']}** | {d['adjustment']} | {d['reason']} |")
        r.append("")

    if monitor:
        r.append("### MONITOR — Watch for Side Effects\n")
        r.append("| Medicine | Note |")
        r.append("|----------|------|")
        for d in monitor:
            r.append(f"| {d['drug']} | {d['note']} |")
        r.append("")

    r.append("### What Should You Do?\n")
    r.append("1. **Print the medicine table above**")
    r.append("2. **Keep it in the medical file forever**")
    r.append("3. **Show it to EVERY doctor** before any medicine is prescribed")
    r.append("4. **Before any surgery or hospital stay**, tell the doctors about these drug sensitivities\n")

    # PART 2: Disease Screening
    r.append("---\n\n## PART 2: Disease Screening Results\n")
    if disease_findings:
        total_clinvar = disease_stats.get('total_clinvar', 0)
        r.append(f"We checked the DNA against **{total_clinvar:,} known disease-causing variants**.\n")

        if not real_pathogenic:
            r.append("### Result: No Confirmed Disease Found\n")
            r.append("| What We Looked For | Result |")
            r.append("|-------------------|--------|")
            r.append("| Serious genetic diseases | **None found** |")

            carriers = disease_findings.get('carrier', []) if 'carrier' in disease_findings else []
            r.append(f"| Carrier status | **{len(carriers)} found** |" if carriers else "| Carrier status | **None found** |")
            r.append(f"| Protective variants | **{len(protective)} found** |")
            r.append("")

        low_conf = [f for f in disease_findings.get('pathogenic', []) if f.get('stars', 0) < 2]
        if low_conf:
            r.append(f"\n*Note: {len(low_conf)} low-confidence variants were flagged but are likely not clinically significant (0/4 confidence stars — common population variants).*\n")

        if protective:
            r.append("\n### Protective Variants\n")
            for p in protective:
                r.append(f"- **{p.get('condition', 'Unknown')}** — protective variant found")
    else:
        r.append("Disease screening data not available.\n")

    # PARTS 3-6: Categorized findings
    part_configs = [
        ("PART 3", "Heart & Blood Pressure", ["Cardiovascular"]),
        ("PART 4", "Sugar & Weight", ["Nutrition"]),
        ("PART 5", "Vitamins & Nutrition", ["Methylation"]),
        ("PART 6", "Body's Defense System", ["Detoxification", "Inflammation"]),
    ]

    for part_label, part_title, cats in part_configs:
        part_findings = [f for f in findings if f['category'] in cats]
        if part_findings:
            r.append(f"\n---\n\n## {part_label}: {part_title}\n")
            for f in part_findings:
                kb = _get_knowledge(f['gene'], f['status'])
                if kb:
                    r.append(f"### {kb['title']}\n")
                    r.append(f"- **What it means:** {kb['simple']}")
                    r.append(f"- **Genotype:** `{f['genotype']}` at {f['rsid']} | Impact: {f['magnitude']}/6")
                    r.append(f"- **Action:** {kb['action']}")
                    if kb.get('food'):
                        r.append(f"- **Food tip:** {kb['food']}")
                    r.append("")
                else:
                    r.append(f"### {f['gene']} ({f['rsid']})\n")
                    r.append(f"- {f['description']}")
                    r.append(f"- Genotype: `{f['genotype']}` | Impact: {f['magnitude']}/6\n")

    # PART 7: Other findings
    other_cats = ["Drug Metabolism", "Neurotransmitters", "Caffeine Response", "Fitness",
                  "Alcohol", "Autoimmune", "Longevity"]
    other_findings = [f for f in findings if f['category'] in other_cats and f['magnitude'] <= 1]
    if other_findings:
        r.append("\n---\n\n## PART 7: Other Findings\n")
        r.append("| Area | Finding | What It Means |")
        r.append("|------|---------|--------------|")
        for f in other_findings:
            kb = _get_knowledge(f['gene'], f['status'])
            desc = kb['simple'] if kb else f['description']
            r.append(f"| **{f['category']}** | {f['gene']} ({f['status']}) | {desc} |")
        r.append("")

    # PART 8: Tests
    r.append("\n---\n\n## PART 8: What Tests to Get\n")
    r.append("| Test | Why | How Often |")
    r.append("|------|-----|-----------|")
    test_added = set()
    for f in findings:
        gene = f['gene']
        if gene == 'MTRR' and 'B12' not in test_added:
            r.append("| Vitamin B12 + MMA | Check real B12 levels (MTRR gene) | Once a year |")
            test_added.add('B12')
        elif gene == 'AGT' and 'BP' not in test_added:
            r.append("| Blood Pressure | Monitor for hypertension (AGT gene) | Every doctor visit |")
            test_added.add('BP')
        elif gene == 'TCF7L2' and 'Sugar' not in test_added:
            r.append("| Fasting Sugar or HbA1c | Check for diabetes risk (TCF7L2 gene) | Once a year |")
            test_added.add('Sugar')
        elif gene == 'APOE' and 'Lipid' not in test_added:
            r.append("| Lipid Profile (Cholesterol) | Check heart health (APOE e4) | Once a year |")
            test_added.add('Lipid')
        elif gene in ('MTRR', 'MTHFR') and 'Homo' not in test_added:
            r.append("| Homocysteine | Check methylation health | Baseline once |")
            test_added.add('Homo')
    r.append("")

    # PART 9: Food Guide
    r.append("\n---\n\n## PART 9: Simple Food Guide\n")
    r.append("### Eat Every Day")
    r.append("- **Eggs** (with yolk) — B12, choline, vitamin A, protein")
    r.append("- **Fish** (salmon, sardine, mackerel) — omega-3 for inflammation + heart")
    r.append("- **Leafy greens** (spinach, methi, palak) — folate")
    r.append("- **Colourful vegetables** — antioxidants")
    r.append("- **Curd/Yoghurt** — B12, gut health")
    r.append("- **Nuts & Seeds** — healthy fats, minerals")
    r.append("- **Dal/Lentils** — protein, folate, fibre\n")
    r.append("### Eat Less")
    r.append("- **White sugar, sweets, sugary drinks** — diabetes risk")
    r.append("- **White rice, maida** — switch to brown rice, millets, whole wheat")
    r.append("- **Excessive salt** — blood pressure risk")
    r.append("- **Deep fried foods, excessive ghee** — cholesterol risk")
    r.append("- **Processed/packaged foods** — inflammation\n")

    # PART 10: One-Page Summary
    r.append("\n---\n\n## PART 10: Summary\n")
    r.append("### 3 Things to Remember for Life\n")
    if must_avoid:
        r.append(f"1. **NEVER give {must_avoid[0]['drug']}** — {must_avoid[0]['reason']}")
    for d in dose_adjust[:2]:
        r.append(f"2. **{d['drug']}** — {d['adjustment']}: {d['reason']}")

    # Disclaimer
    r.append("\n---\n\n## Important Disclaimer\n")
    r.append("This report is for **information and awareness only**. It is **NOT a medical diagnosis**.\n")
    r.append("- Having a risk gene does NOT mean the disease will happen")
    r.append("- DNA is only 20-30% of the health picture — food, exercise, sleep matter more")
    r.append("- Always consult a doctor before making medical decisions based on this report\n")
    r.append(f"---\n\n*Generated: {now}*\n")

    output_path = Path(output_dir) / f"COMPLETE_EASY_REPORT_{safe}.md"
    output_path.write_text("\n".join(r))
    return output_path


# =============================================================================
# SWOT REPORT GENERATOR
# =============================================================================

def generate_swot_report(health_results, disease_findings, disease_stats,
                          output_dir, subject_name):
    """Generate SWOT_REPORT_{name}.md"""
    findings = health_results['findings']
    pharmgkb = health_results['pharmgkb_findings']
    summary = health_results['summary']
    safe = _safe_name(subject_name)
    now = datetime.now().strftime("%d %B %Y")

    must_avoid, dose_adjust, monitor = _get_drug_warnings(findings, pharmgkb)

    r = []
    r.append(f"# SWOT Genetic Analysis\n")
    r.append(f"**Name:** {subject_name or 'Subject'}")
    r.append(f"**Date:** {now}")
    r.append(f"**DNA Points Checked:** {summary['total_snps']:,}\n")
    r.append("---\n")

    # === STRENGTHS ===
    r.append("## S — STRENGTHS\n")
    r.append("*Built-in genetic advantages.*\n")

    strengths = []
    score = 5.0

    # Check disease-free status
    real_pathogenic = []
    if disease_findings:
        real_pathogenic = [f for f in disease_findings.get('pathogenic', [])
                          if f.get('stars', 0) >= 2]
    if not real_pathogenic:
        strengths.append({
            'title': 'Zero Genetic Diseases Detected',
            'detail': f'Out of {disease_stats.get("total_clinvar", 0):,} known disease variants — not a single confirmed match.',
            'rarity': 'Best possible outcome'
        })
        score += 1.5

    # Check protective variants
    protective = disease_findings.get('protective', []) if disease_findings else []
    for p in protective:
        cond = p.get('condition', 'Unknown')
        strengths.append({
            'title': f'Protective: {cond}',
            'detail': f'Built-in genetic protection against {cond}.',
            'rarity': 'Uncommon — genuinely lucky'
        })
        score += 0.5

    # Check for carrier status
    has_carriers = False
    if disease_findings:
        for cat in ['carrier']:
            if cat in disease_findings and disease_findings[cat]:
                has_carriers = True
    if not has_carriers:
        strengths.append({
            'title': 'No Carrier Status for Recessive Diseases',
            'detail': 'Not a carrier for any recessive condition tested. Good for future reproductive planning.',
            'rarity': 'Clean result'
        })
        score += 0.3

    # Check individual gene strengths
    for f in findings:
        kb = _get_knowledge(f['gene'], f['status'])
        if kb and kb['swot'] == 'strength':
            gene_label = f"{f['gene']} ({f['rsid']})"
            strengths.append({
                'title': kb['title'],
                'detail': kb['simple'],
                'rarity': f"Genotype: {f['genotype']}"
            })
            if f['gene'] == 'COMT':
                score += 0.4
            elif f['gene'] == 'ACTN3':
                score += 0.3
            elif f['gene'] == 'CYP1A2':
                score += 0.2
            elif f['gene'] == 'PTPN22':
                score += 0.2
            elif f['gene'] == 'ACE':
                score += 0.2

    for i, s in enumerate(strengths, 1):
        r.append(f"### {i}. {s['title']}\n")
        r.append(f"{s['detail']}\n")
        r.append(f"*{s['rarity']}*\n")

    # Strengths summary table
    r.append("### Strengths Summary\n")
    r.append("| # | Strength | Note |")
    r.append("|---|----------|------|")
    for i, s in enumerate(strengths, 1):
        r.append(f"| {i} | {s['title']} | {s['rarity']} |")
    r.append("")

    # === WEAKNESSES ===
    r.append("\n---\n\n## W — WEAKNESSES\n")
    r.append("*Built-in vulnerabilities. Most can be managed with lifestyle choices.*\n")

    weaknesses = []
    for f in findings:
        kb = _get_knowledge(f['gene'], f['status'])
        if kb and kb['swot'] == 'weakness':
            weaknesses.append({
                'title': kb['title'],
                'detail': kb['simple'],
                'severity': kb.get('severity', 'Unknown'),
                'manageable': kb.get('manageable', 'Unknown'),
                'gene': f['gene'],
                'genotype': f['genotype'],
                'rsid': f['rsid'],
            })
            if f['magnitude'] >= 4:
                score -= 0.4
            elif f['magnitude'] >= 3:
                score -= 0.3
            elif f['magnitude'] >= 2:
                score -= 0.2
            else:
                score -= 0.1

    for i, w in enumerate(weaknesses, 1):
        r.append(f"### {i}. {w['title']}\n")
        r.append(f"**Gene:** {w['rsid']} ({w['genotype']}) | **Severity:** {w['severity']}\n")
        r.append(f"{w['detail']}\n")
        r.append(f"**Can it be managed?** {w['manageable']}\n")

    # Weaknesses summary table
    r.append("### Weaknesses Summary\n")
    r.append("| # | Weakness | Severity | Manageable? |")
    r.append("|---|----------|----------|-------------|")
    for i, w in enumerate(weaknesses, 1):
        r.append(f"| {i} | {w['title']} | {w['severity']} | {w['manageable']} |")
    r.append("")

    # === OPPORTUNITIES ===
    r.append("\n---\n\n## O — OPPORTUNITIES\n")
    r.append("*How to turn this genetic profile into an advantage.*\n")

    opportunities = []

    # Athletic potential
    has_actn3 = any(f['gene'] == 'ACTN3' for f in findings)
    has_ace = any(f['gene'] == 'ACE' and f['status'] == 'low' for f in findings)
    has_comt = any(f['gene'] == 'COMT' and f['status'] == 'intermediate' for f in findings)
    if has_actn3 or has_ace:
        opportunities.append({
            'title': 'Sports & Athletic Potential',
            'detail': 'Versatile muscle type + endurance wiring = can succeed at any sport. Start exploring sports early.',
            'impact': 'Very High'
        })
    if has_comt:
        opportunities.append({
            'title': 'Mental Performance Under Pressure',
            'detail': 'Balanced dopamine profile means clear thinking under stress. Good for competitive exams, leadership, high-pressure careers.',
            'impact': 'High'
        })

    opportunities.append({
        'title': 'Preventive Health From Day Zero',
        'detail': 'All genetic risks are known from birth. This is a 20-30 year head start over people who discover their genes later in life.',
        'impact': 'Very High'
    })

    if any(f['gene'] == 'APOE' for f in findings):
        opportunities.append({
            'title': 'Heart Disease Is Preventable',
            'detail': 'Knowing about cardiovascular risk genes early means diet, exercise, and monitoring can start from childhood.',
            'impact': 'High'
        })

    if any(f['gene'] == 'TCF7L2' for f in findings):
        opportunities.append({
            'title': 'Diabetes Is Preventable',
            'detail': 'TCF7L2-related diabetes risk is one of the most responsive to lifestyle changes. Exercise + low sugar diet can nearly neutralize the risk.',
            'impact': 'High'
        })

    if must_avoid or dose_adjust:
        opportunities.append({
            'title': 'Complete Drug Safety Card Ready',
            'detail': 'Having a pharmacogenomic profile before any emergency is potentially life-saving. Most people discover drug sensitivities after a bad reaction.',
            'impact': 'Life-saving'
        })

    opportunities.append({
        'title': 'Personalized Nutrition Blueprint',
        'detail': 'Exactly which vitamins the body needs, in what form, is known. No guessing needed.',
        'impact': 'High'
    })

    for i, o in enumerate(opportunities, 1):
        r.append(f"### {i}. {o['title']}\n")
        r.append(f"{o['detail']}\n")
        r.append(f"*Potential Impact: {o['impact']}*\n")

    # Opportunities summary table
    r.append("### Opportunities Summary\n")
    r.append("| # | Opportunity | Impact |")
    r.append("|---|------------|--------|")
    for i, o in enumerate(opportunities, 1):
        r.append(f"| {i} | {o['title']} | {o['impact']} |")
    r.append("")

    # === THREATS ===
    r.append("\n---\n\n## T — THREATS\n")
    r.append("*External risks that could activate the genetic weaknesses.*\n")

    threats = []

    if must_avoid or dose_adjust:
        drugs_str = ", ".join([d['drug'] for d in must_avoid + dose_adjust][:3])
        threats.append({
            'title': 'Medical Emergency Without Genetic Info',
            'detail': f'If doctors don\'t know about drug sensitivities ({drugs_str}), wrong prescriptions could be dangerous.',
            'danger': 'Life-threatening',
            'prevention': 'Keep a drug alert card in wallet, phone, and medical records at ALL times'
        })

    weakness_genes = [w['gene'] for w in weaknesses]
    active_count = sum(1 for g in ['APOE', 'TCF7L2', 'AGT', 'FTO', 'IL6'] if g in weakness_genes)
    if active_count >= 2:
        threats.append({
            'title': 'Sedentary Lifestyle',
            'detail': f'No exercise activates {active_count} genetic weaknesses simultaneously — cholesterol, diabetes, blood pressure, weight, inflammation.',
            'danger': 'High',
            'prevention': 'Make physical activity a daily non-negotiable habit from childhood'
        })
        threats.append({
            'title': 'Junk Food & High Sugar Diet',
            'detail': 'Modern processed food activates diabetes, weight, inflammation, and cholesterol genes all at once.',
            'danger': 'High',
            'prevention': 'Establish healthy eating patterns early. This genetic profile cannot afford a junk food lifestyle'
        })

    if 'AGT' in weakness_genes:
        threats.append({
            'title': 'High Salt Diet',
            'detail': 'The AGT blood pressure gene responds very strongly to sodium. This is a major dietary threat.',
            'danger': 'Moderate-High',
            'prevention': 'Reduce salt in cooking, avoid packaged foods, use herbs/spices instead'
        })

    if 'IL6' in weakness_genes:
        threats.append({
            'title': 'Sleep Deprivation',
            'detail': 'IL-6 inflammation spikes dramatically with poor sleep. Combined with other risks, this accelerates aging.',
            'danger': 'Moderate-High',
            'prevention': '7-8 hours sleep is non-negotiable for this genetic profile'
        })

    vitamin_genes = [g for g in ['MTRR', 'BCMO1', 'PEMT'] if g in weakness_genes]
    if vitamin_genes:
        threats.append({
            'title': 'Vegetarian/Vegan Diet Without Planning',
            'detail': f'Genes {", ".join(vitamin_genes)} all require nutrients best found in animal sources (B12, vitamin A, choline).',
            'danger': 'Moderate',
            'prevention': 'If vegetarian: eggs + dairy essential. If vegan: must supplement carefully'
        })

    threats.append({
        'title': 'Skipping Health Checkups',
        'detail': 'Blood pressure, blood sugar, and cholesterol can creep up silently for years.',
        'danger': 'Moderate',
        'prevention': 'Annual blood tests from age 18. BP monitoring from age 12'
    })

    threats.append({
        'title': 'Changing Doctors Without Sharing Genetic History',
        'detail': 'New doctor doesn\'t know about drug sensitivities = dangerous prescriptions.',
        'danger': 'High',
        'prevention': 'Keep a permanent digital health record. Share genetic drug card with every new doctor'
    })

    for i, t in enumerate(threats, 1):
        r.append(f"### {i}. {t['title']}\n")
        r.append(f"**Danger Level:** {t['danger']}\n")
        r.append(f"{t['detail']}\n")
        r.append(f"**Prevention:** {t['prevention']}\n")

    # Threats summary table
    r.append("### Threats Summary\n")
    r.append("| # | Threat | Danger | Preventable? |")
    r.append("|---|--------|--------|-------------|")
    for i, t in enumerate(threats, 1):
        r.append(f"| {i} | {t['title']} | {t['danger']} | Yes — {t['prevention'][:50]}... |")
    r.append("")

    # === SWOT MATRIX ===
    r.append("\n---\n\n## THE SWOT MATRIX\n")
    r.append("```")
    r.append("                    HELPFUL                             HARMFUL")
    r.append("              ┌──────────────────────────┐    ┌──────────────────────────────┐")
    r.append("              │       STRENGTHS          │    │        WEAKNESSES            │")
    r.append("   INTERNAL   │                          │    │                              │")

    # Fill strengths column (max 7 lines)
    s_lines = [s['title'][:24] for s in strengths[:7]]
    w_lines = [w['title'][:28] for w in weaknesses[:7]]

    max_lines = max(len(s_lines), len(w_lines), 1)
    for i in range(max_lines):
        s_text = s_lines[i] if i < len(s_lines) else ""
        w_text = w_lines[i] if i < len(w_lines) else ""
        r.append(f"              │  {s_text:<24}│    │  {w_text:<28}│")

    r.append("              │                          │    │                              │")
    r.append("              └──────────────────────────┘    └──────────────────────────────┘")
    r.append("              ┌──────────────────────────┐    ┌──────────────────────────────┐")
    r.append("              │     OPPORTUNITIES        │    │         THREATS              │")
    r.append("   EXTERNAL   │                          │    │                              │")

    o_lines = [o['title'][:24] for o in opportunities[:7]]
    t_lines = [t['title'][:28] for t in threats[:7]]

    max_lines2 = max(len(o_lines), len(t_lines), 1)
    for i in range(max_lines2):
        o_text = o_lines[i] if i < len(o_lines) else ""
        t_text = t_lines[i] if i < len(t_lines) else ""
        r.append(f"              │  {o_text:<24}│    │  {t_text:<28}│")

    r.append("              │                          │    │                              │")
    r.append("              └──────────────────────────┘    └──────────────────────────────┘")
    r.append("```\n")

    # === FINAL VERDICT ===
    score = max(0, min(10, score))
    score_rounded = round(score, 1)

    r.append("---\n\n## FINAL VERDICT\n")
    r.append(f"### Overall Genetic Score: {score_rounded}/10\n")

    if score_rounded >= 8:
        verdict = "excellent"
    elif score_rounded >= 7:
        verdict = "above average"
    elif score_rounded >= 6:
        verdict = "good"
    elif score_rounded >= 5:
        verdict = "average"
    else:
        verdict = "below average but manageable"

    r.append(f"This is a **genetically healthy profile** rated as **{verdict}**. "
             f"Strengths clearly outnumber weaknesses. "
             f"The weaknesses that exist are almost all manageable through lifestyle choices — "
             f"the only truly dangerous items are the drug sensitivities, which are threats only if the medical team isn't informed.\n")

    # Disclaimer
    r.append("\n---\n\n## Important Disclaimer\n")
    r.append("This report is for **information and awareness only**. It is **NOT a medical diagnosis**.\n")
    r.append("- Having a risk gene does NOT mean the disease will happen")
    r.append("- DNA is only 20-30% of the health picture")
    r.append("- Always consult a doctor before making medical decisions\n")
    r.append(f"---\n\n*Generated: {now}*\n")

    output_path = Path(output_dir) / f"SWOT_REPORT_{safe}.md"
    output_path.write_text("\n".join(r))
    return output_path


# =============================================================================
# PRENATAL / FETAL SCAN DOCTOR REPORT — Indian Context
# =============================================================================

# Indian carrier screening conditions with population frequencies
INDIAN_CARRIER_CONDITIONS = {
    'HBB': {
        'name': 'Beta-Thalassemia / Hemoglobinopathy',
        'frequency': '1-17% carrier rate (varies by community)',
        'high_risk_groups': 'Sindhis (8-17%), Punjabis (4-8%), Gujaratis (4-7%), Bengalis (3-8%)',
        'confirmatory_test': 'HPLC / Hb Electrophoresis for both parents',
        'prenatal_test': 'CVS at 11-12 weeks or amniocentesis at 15-16 weeks for DNA analysis',
        'urgency': 'HIGH',
    },
    'G6PD': {
        'name': 'G6PD Deficiency',
        'frequency': '4-25% (X-linked; Parsees 15-25%, Sindhis 10-15%)',
        'high_risk_groups': 'Parsees, Sindhis, Valmikis, Jats, tribal populations',
        'confirmatory_test': 'G6PD enzyme assay (quantitative)',
        'prenatal_test': 'Not usually needed — manageable condition. Drug avoidance list at birth',
        'urgency': 'MODERATE',
    },
    'CFTR': {
        'name': 'Cystic Fibrosis',
        'frequency': '1:40 to 1:100 carrier rate (underdiagnosed in India)',
        'high_risk_groups': 'Pan-Indian, often missed due to atypical presentation',
        'confirmatory_test': 'Sweat chloride test + CFTR gene panel',
        'prenatal_test': 'CVS/amniocentesis for CFTR mutation panel if both parents carriers',
        'urgency': 'HIGH',
    },
    'SMN1': {
        'name': 'Spinal Muscular Atrophy',
        'frequency': '~1:50 to 1:60 carrier rate',
        'high_risk_groups': 'Pan-Indian, leading genetic cause of infant death',
        'confirmatory_test': 'MLPA / qPCR for SMN1 copy number (NOT SNP-based)',
        'prenatal_test': 'CVS at 11 weeks for SMN1 deletion analysis if both parents carriers',
        'urgency': 'HIGH',
    },
    'GJB2': {
        'name': 'Congenital Hearing Loss (Connexin 26)',
        'frequency': '~1:25 to 1:40 carrier rate (W24X mutation)',
        'high_risk_groups': 'Pan-Indian; W24X accounts for 68-75% of Indian GJB2 mutations',
        'confirmatory_test': 'GJB2 gene sequencing',
        'prenatal_test': 'Not usually done prenatally — newborn OAE/BERA screening at birth',
        'urgency': 'MODERATE',
    },
    'CYP21A2': {
        'name': 'Congenital Adrenal Hyperplasia',
        'frequency': '~1:50 carrier rate',
        'high_risk_groups': 'Pan-Indian, included in newborn screening',
        'confirmatory_test': '17-OHP level (newborn), CYP21A2 gene analysis',
        'prenatal_test': 'CVS if both parents carriers (for female fetus: early dexamethasone may be considered)',
        'urgency': 'HIGH',
    },
    'ATP7B': {
        'name': 'Wilson Disease',
        'frequency': '1:10,000 to 1:30,000 (higher with consanguinity)',
        'high_risk_groups': 'Consanguineous families across India',
        'confirmatory_test': 'Ceruloplasmin, 24hr urine copper, ATP7B gene analysis',
        'prenatal_test': 'CVS if both parents carriers and family history positive',
        'urgency': 'MODERATE',
    },
}


def generate_prenatal_report(health_results, disease_findings, disease_stats,
                             output_dir, subject_name):
    """
    Generate PRENATAL_REPORT_{name}.md — formatted for fetal scan doctors.

    This report is specifically designed for:
    - Indian population context
    - Prenatal / fetal genetic counseling
    - Carrier screening results for family planning
    - Actionable recommendations for OB-GYN / fetal medicine specialist
    """
    findings = health_results['findings']
    pharmgkb = health_results['pharmgkb_findings']
    safe = _safe_name(subject_name)
    now = datetime.now().strftime("%d %B %Y")

    r = []

    r.append(f"# PRENATAL GENETIC SCREENING REPORT")
    r.append(f"## {subject_name or 'Subject'}")
    r.append(f"\n**Report Date:** {now}")
    r.append(f"**Report Type:** Prenatal Genetic Screening — Indian Population Context")
    r.append(f"**For:** Fetal Medicine Specialist / OB-GYN / Genetic Counselor")
    r.append(f"**Confidence Note:** This report is generated from whole genome/exome sequencing data. "
             f"All critical findings should be confirmed with targeted testing before clinical decisions.\n")

    r.append("---\n")

    # =========================================================================
    # SECTION 1: EXECUTIVE SUMMARY FOR DOCTOR
    # =========================================================================
    r.append("## 1. EXECUTIVE SUMMARY\n")

    # Collect carrier findings from lifestyle analysis
    carrier_findings_snp = []
    drug_warnings_snp = []
    positive_findings_snp = []
    nutrition_findings_snp = []

    for f in findings:
        gene = f['gene']
        status = f['status']
        cat = f.get('category', '')

        # Indian carrier screening hits
        if cat == 'Indian Carrier Screening':
            carrier_findings_snp.append(f)
        elif cat in ('Indian Nutrition', 'Indian Prenatal', 'Indian Autoimmune'):
            nutrition_findings_snp.append(f)
        elif gene in ('DPYD', 'HLA-B', 'CYP2C19', 'CYP2C9') and f['magnitude'] >= 3:
            drug_warnings_snp.append(f)
        elif f['magnitude'] == 0 or status in ('normal', 'reference'):
            positive_findings_snp.append(f)

    # ClinVar carrier findings
    carrier_clinvar = []
    affected_clinvar = []
    affected_low_confidence = []
    if disease_findings:
        for df in disease_findings.get('pathogenic', []) + disease_findings.get('likely_pathogenic', []):
            inheritance = df.get('inheritance', '').lower()
            gold_stars = df.get('gold_stars', 0)
            confidence = df.get('confidence', 'LOW')
            gene = df.get('gene', '')

            if df['is_heterozygous'] and 'recessive' in inheritance:
                carrier_clinvar.append(df)
            elif df['is_homozygous'] or (df['is_heterozygous'] and 'dominant' in inheritance):
                # Separate high-confidence from low-confidence affected
                if gold_stars >= 2 or (gold_stars >= 1 and gene):
                    affected_clinvar.append(df)
                else:
                    affected_low_confidence.append(df)

    # Summary counts
    total_carriers = len(carrier_findings_snp) + len(carrier_clinvar)
    total_affected = len(affected_clinvar)
    total_affected_low = len(affected_low_confidence)
    total_drug = len(drug_warnings_snp)

    r.append("### Quick Overview\n")
    r.append("| Category | Count | Action Required |")
    r.append("|----------|-------|-----------------|")

    if total_affected > 0:
        r.append(f"| **Pathogenic (Affected — High Confidence)** | {total_affected} | **URGENT — Confirm with targeted test** |")
    else:
        r.append(f"| Pathogenic (Affected — High Confidence) | 0 | No confirmed disease variants |")

    if total_affected_low > 0:
        r.append(f"| Pathogenic (Low Confidence) | {total_affected_low} | Low evidence — likely not clinically significant |")

    if total_carriers > 0:
        r.append(f"| **Carrier Status** | {total_carriers} | **Partner screening required** |")
    else:
        r.append(f"| Carrier Status | 0 | No carrier variants detected |")

    r.append(f"| Drug Sensitivities | {total_drug} | Note in medical records |")
    r.append(f"| Nutrition/Metabolism | {len(nutrition_findings_snp)} | Optimize prenatal supplements |")
    r.append("")

    if total_affected == 0 and total_carriers == 0:
        if total_affected_low > 0:
            r.append(f"> **OVERALL: No high-confidence disease variants detected.** {total_affected_low} low-evidence variants "
                     f"were found (see Section 2) but are unlikely to be clinically significant. Standard prenatal care recommended.\n")
        else:
            r.append("> **OVERALL: No high-risk carrier conditions detected in this screening.** "
                     "Standard prenatal care recommended.\n")
    elif total_affected > 0:
        r.append("> **ALERT: Pathogenic variant(s) detected. See Section 2 for details.** "
                 "Genetic counseling referral recommended.\n")
    elif total_carriers > 0:
        r.append("> **CARRIER STATUS DETECTED: Partner screening is mandatory before risk assessment.** "
                 "See Section 3 for carrier details and Section 5 for recommended tests.\n")

    r.append("---\n")

    # =========================================================================
    # SECTION 2: CRITICAL FINDINGS (AFFECTED STATUS)
    # =========================================================================
    r.append("## 2. CRITICAL FINDINGS — Affected Status\n")

    if affected_clinvar:
        r.append("**These variants suggest the individual may be affected by or at significant risk for the following conditions.**\n")
        for af in affected_clinvar:
            stars = '⭐' * af['gold_stars'] if af['gold_stars'] else '☆'
            conf = af.get('confidence', 'UNKNOWN')
            gene_name = af['gene'] if af['gene'] else 'Unknown gene'
            r.append(f"### {gene_name} — {af['traits'].split(';')[0] if af['traits'] else 'Condition not specified'}\n")
            r.append(f"| Field | Value |")
            r.append(f"|-------|-------|")
            r.append(f"| Gene | {gene_name} |")
            r.append(f"| Variant | {af['rsid']} ({af['ref']}→{af['alt']}) |")
            r.append(f"| Genotype | `{af['user_genotype']}` ({'Homozygous' if af['is_homozygous'] else 'Heterozygous dominant'}) |")
            r.append(f"| ClinVar Confidence | {stars} ({af['gold_stars']}/4) — {conf} |")
            r.append(f"| Condition | {af['traits']} |")
            r.append(f"| Inheritance | {af['inheritance'] if af['inheritance'] else 'Not specified'} |")
            r.append(f"\n**Action:** Confirm with targeted genetic testing. Refer to clinical geneticist.\n")
    else:
        r.append("**No high-confidence pathogenic variants with affected status detected.** This is a positive finding.\n")
        r.append("> Zero confirmed disease-causing variants (with adequate ClinVar evidence) in homozygous or dominant state.\n")

    if affected_low_confidence:
        r.append(f"\n### Low-Confidence Variants ({len(affected_low_confidence)} found)\n")
        r.append("The following variants were flagged as pathogenic/likely pathogenic but have **very low evidence** "
                 "(0-1 ClinVar stars, often with missing gene annotations). These are **unlikely to be clinically significant** "
                 "and should NOT cause alarm.\n")
        r.append("| rsID | Genotype | Condition | Stars | Note |")
        r.append("|------|----------|-----------|-------|------|")
        for af in affected_low_confidence:
            gene_name = af['gene'] if af['gene'] else '—'
            condition = af['traits'].split(';')[0] if af['traits'] else '—'
            r.append(f"| {af['rsid']} | `{af['user_genotype']}` | {condition} | {af['gold_stars']}/4 | Low evidence — confirm only if clinically indicated |")
        r.append("")

    r.append("---\n")

    # =========================================================================
    # SECTION 3: CARRIER SCREENING — INDIAN CONTEXT
    # =========================================================================
    r.append("## 3. CARRIER SCREENING RESULTS — Indian Population\n")
    r.append("Carrier status means the individual has ONE copy of a disease-causing variant. "
             "Carriers are typically healthy but can pass the variant to children.\n")
    r.append("**KEY RULE:** If BOTH parents are carriers of the SAME autosomal recessive condition, "
             "each pregnancy has a **25% (1 in 4)** chance of an affected child.\n")

    all_carriers = []

    # From SNP database (Indian carrier screening)
    for cf in carrier_findings_snp:
        gene = cf['gene']
        status = cf['status']
        kb = _get_knowledge(gene, status)
        condition_info = INDIAN_CARRIER_CONDITIONS.get(gene, {})

        entry = {
            'gene': gene,
            'rsid': cf['rsid'],
            'genotype': cf['genotype'],
            'status': status,
            'condition': condition_info.get('name', f'{gene} carrier condition'),
            'frequency': condition_info.get('frequency', 'Unknown in Indian population'),
            'high_risk': condition_info.get('high_risk_groups', 'Unknown'),
            'confirm_test': condition_info.get('confirmatory_test', 'Targeted genetic testing'),
            'prenatal_test': condition_info.get('prenatal_test', 'Consult genetic counselor'),
            'urgency': condition_info.get('urgency', 'MODERATE'),
            'detail': kb['simple'] if kb else cf.get('desc', ''),
        }
        all_carriers.append(entry)

    # From ClinVar carrier findings
    for ccf in carrier_clinvar:
        gene = ccf['gene']
        condition_info = INDIAN_CARRIER_CONDITIONS.get(gene, {})
        entry = {
            'gene': gene,
            'rsid': ccf['rsid'],
            'genotype': ccf['user_genotype'],
            'status': 'carrier (ClinVar)',
            'condition': ccf['traits'].split(';')[0] if ccf['traits'] else f'{gene} recessive condition',
            'frequency': condition_info.get('frequency', 'See ClinVar'),
            'high_risk': condition_info.get('high_risk_groups', 'See ClinVar'),
            'confirm_test': condition_info.get('confirmatory_test', 'Targeted genetic test'),
            'prenatal_test': condition_info.get('prenatal_test', 'Consult genetic counselor'),
            'urgency': condition_info.get('urgency', 'MODERATE'),
            'detail': ccf['traits'] if ccf['traits'] else '',
        }
        all_carriers.append(entry)

    if all_carriers:
        # Sort by urgency
        urgency_order = {'HIGH': 0, 'MODERATE': 1, 'LOW': 2}
        all_carriers.sort(key=lambda x: urgency_order.get(x['urgency'], 3))

        for i, c in enumerate(all_carriers, 1):
            urgency_icon = '🔴' if c['urgency'] == 'HIGH' else '🟡' if c['urgency'] == 'MODERATE' else '🟢'
            r.append(f"### {urgency_icon} {i}. {c['condition']} ({c['gene']})\n")
            r.append(f"| Field | Detail |")
            r.append(f"|-------|--------|")
            r.append(f"| **Gene** | {c['gene']} ({c['rsid']}) |")
            r.append(f"| **Genotype** | `{c['genotype']}` — {c['status']} |")
            r.append(f"| **Indian Carrier Frequency** | {c['frequency']} |")
            r.append(f"| **High-Risk Communities** | {c['high_risk']} |")
            r.append(f"| **Urgency** | {c['urgency']} |")
            r.append(f"| **Confirmatory Test** | {c['confirm_test']} |")
            r.append(f"| **Prenatal Testing** | {c['prenatal_test']} |")
            r.append(f"\n{c['detail']}\n")

        # Carrier summary table
        r.append("\n### Carrier Screening Summary Table\n")
        r.append("| # | Condition | Gene | Urgency | Partner Test Required |")
        r.append("|---|-----------|------|---------|---------------------|")
        for i, c in enumerate(all_carriers, 1):
            r.append(f"| {i} | {c['condition']} | {c['gene']} | {c['urgency']} | **YES** — {c['confirm_test']} |")
        r.append("")
    else:
        r.append("### No carrier conditions detected\n")
        r.append("The common Indian carrier conditions screened (Beta-Thalassemia, Sickle Cell, "
                 "HbE, G6PD, Cystic Fibrosis, SMA, Hearing Loss, CAH, Wilson Disease) "
                 "were **not detected** in this analysis.\n")
        r.append("> **Note:** This screening is based on known SNP variants. Some carrier conditions "
                 "(especially SMA/SMN1 deletions) require MLPA/copy number analysis for definitive screening. "
                 "Clinical carrier screening is recommended for high-risk communities.\n")

    r.append("---\n")

    # =========================================================================
    # SECTION 4: DRUG SENSITIVITIES — CRITICAL FOR PRESCRIBING
    # =========================================================================
    r.append("## 4. PHARMACOGENOMIC ALERTS — Drug Sensitivities\n")
    r.append("These findings affect how certain medications are processed. "
             "**Print this section and attach to the patient's medical file.**\n")

    must_avoid, dose_adjust, monitor = _get_drug_warnings(findings, pharmgkb)

    if must_avoid:
        r.append("### 🔴 MUST AVOID — Life-Threatening Reactions\n")
        r.append("| Drug | Reason |")
        r.append("|------|--------|")
        for d in must_avoid:
            r.append(f"| **{d['drug']}** | {d['reason']} |")
        r.append("")

    if dose_adjust:
        r.append("### 🟡 DOSE ADJUSTMENT REQUIRED\n")
        r.append("| Drug | Adjustment | Reason |")
        r.append("|------|-----------|--------|")
        for d in dose_adjust:
            r.append(f"| **{d['drug']}** | {d['adjustment']} | {d['reason']} |")
        r.append("")

    if not must_avoid and not dose_adjust:
        r.append("No critical drug sensitivities detected.\n")

    # G6PD specific drug list (if carrier or affected)
    g6pd_found = any(f['gene'] == 'G6PD' for f in findings if f.get('category') == 'Indian Carrier Screening')
    if g6pd_found:
        r.append("### 🔴 G6PD DEFICIENCY — Drug and Food Avoidance List\n")
        r.append("If the child is a MALE and inherits the G6PD deficiency, the following must be avoided:\n")
        r.append("**DRUGS TO AVOID:**")
        r.append("- Primaquine (antimalarial)")
        r.append("- Dapsone")
        r.append("- Nitrofurantoin (UTI antibiotic)")
        r.append("- Sulfonamides (e.g., co-trimoxazole)")
        r.append("- Rasburicase")
        r.append("- Methylene blue")
        r.append("- High-dose Vitamin C (>1g)\n")
        r.append("**FOODS/SUBSTANCES TO AVOID:**")
        r.append("- Fava beans (broad beans)")
        r.append("- Mothballs (naphthalene) — keep away from baby's clothes")
        r.append("- Henna (in large amounts)\n")

    r.append("---\n")

    # =========================================================================
    # SECTION 5: RECOMMENDED TESTS AND FOLLOW-UP
    # =========================================================================
    r.append("## 5. RECOMMENDED TESTS AND FOLLOW-UP\n")

    r.append("### 5A. Immediate (Before Delivery)\n")
    r.append("| # | Test | For | Priority |")
    r.append("|---|------|-----|----------|")

    test_num = 1
    if all_carriers:
        for c in all_carriers:
            if c['urgency'] == 'HIGH':
                r.append(f"| {test_num} | **{c['confirm_test']}** (PARTNER) | {c['condition']} carrier confirmation | 🔴 HIGH |")
                test_num += 1

    # Standard Indian prenatal tests
    r.append(f"| {test_num} | HPLC / Hb Electrophoresis (if not done) | Beta-thalassemia / HbE / HbS screening | 🔴 HIGH |")
    test_num += 1
    r.append(f"| {test_num} | 25-OH Vitamin D level | Vitamin D status (70-90% Indian women deficient) | 🟡 MODERATE |")
    test_num += 1
    r.append(f"| {test_num} | Serum Ferritin + CBC | Iron status (50% Indian women are iron deficient) | 🟡 MODERATE |")
    test_num += 1
    r.append(f"| {test_num} | Fasting glucose / HbA1c | Gestational diabetes screening | 🟡 MODERATE |")
    test_num += 1
    r.append("")

    r.append("### 5B. At Birth / Neonatal\n")
    r.append("| # | Test | For | Priority |")
    r.append("|---|------|-----|----------|")

    ntest = 1
    # UGT1A1 check
    ugt_found = any(f['gene'] == 'UGT1A1' for f in findings if f.get('category') == 'Indian Prenatal')
    if ugt_found:
        r.append(f"| {ntest} | **Early bilirubin check** (within 24 hrs) | Neonatal jaundice — UGT1A1 variant detected | 🔴 HIGH |")
        ntest += 1
    if g6pd_found:
        r.append(f"| {ntest} | **G6PD enzyme assay** (cord blood) | G6PD deficiency screening — carrier mother | 🔴 HIGH |")
        ntest += 1
    r.append(f"| {ntest} | OAE / BERA hearing screening | Congenital hearing loss | 🟡 MODERATE |")
    ntest += 1
    r.append(f"| {ntest} | Newborn screening panel (17-OHP, TSH, IRT) | CAH, hypothyroid, CF | 🟡 MODERATE |")
    ntest += 1
    r.append("")

    r.append("---\n")

    # =========================================================================
    # SECTION 6: PRENATAL NUTRITION OPTIMIZATION
    # =========================================================================
    r.append("## 6. PRENATAL NUTRITION — Genetically Optimized\n")
    r.append("Based on genetic analysis, personalized prenatal nutrition recommendations:\n")

    r.append("### Supplement Recommendations\n")
    r.append("| Supplement | Dose | Reason (Genetic) |")
    r.append("|-----------|------|-----------------|")

    # Check for MTHFR variants
    mthfr_found = any(f['gene'] == 'MTHFR' for f in findings)
    if mthfr_found:
        r.append("| **Methylfolate** (NOT folic acid) | 800-1000 mcg/day | MTHFR variant — reduced folic acid conversion |")
    else:
        r.append("| Folic acid | 400-800 mcg/day | Standard prenatal dose |")

    # Vitamin D
    vdbp_found = any(f['gene'] in ('GC (VDBP)', 'GC') for f in findings)
    if vdbp_found:
        r.append("| **Vitamin D3** | 2000 IU/day (minimum) | VDBP variant + Indian deficiency risk |")
    else:
        r.append("| Vitamin D3 | 1000 IU/day | Standard — 70-90% Indian women are deficient |")

    # Iron
    tmprss6_found = any(f['gene'] == 'TMPRSS6' for f in findings)
    if tmprss6_found:
        r.append("| **Iron** (ferrous bisglycinate) | As per OB-GYN | TMPRSS6 variant — reduced iron absorption |")
    else:
        r.append("| Iron | As per OB-GYN | Standard prenatal |")

    # B12
    mtrr_found = any(f['gene'] == 'MTRR' for f in findings)
    if mtrr_found:
        r.append("| **Methylcobalamin** (B12) | 1000 mcg/day | MTRR variant — reduced B12 recycling |")
    else:
        r.append("| Vitamin B12 | 250 mcg/day | Standard — important for vegetarian mothers |")

    r.append("| DHA (Omega-3) | 200-300 mg/day | Fetal brain and eye development |")
    r.append("| Calcium | 500-1000 mg/day | Fetal bone development |")
    r.append("")

    # Lactose intolerance guidance
    lactose_found = any(f['gene'] in ('LCT/MCM6', 'MCM6') and f['status'] in ('lactose_intolerant',) for f in findings)
    if lactose_found:
        r.append("### Lactose Intolerance — Calcium Strategy\n")
        r.append("Lactose intolerant genotype detected. **This does NOT mean avoid all dairy:**")
        r.append("- **OK:** Curd/yoghurt, paneer, ghee, aged cheese (low lactose)")
        r.append("- **Limit:** Plain milk, ice cream, kulfi")
        r.append("- **Non-dairy calcium:** Ragi, sesame seeds (til), amaranth, dark leafy greens, calcium-fortified foods\n")

    r.append("---\n")

    # =========================================================================
    # SECTION 7: CONSANGUINITY RISK ASSESSMENT
    # =========================================================================
    r.append("## 7. CONSANGUINITY RISK NOTE\n")
    r.append("Consanguineous marriages are common in many Indian communities (10-30% in some regions). "
             "This increases the risk of ALL autosomal recessive conditions.\n")
    if total_carriers > 0:
        r.append(f"**This individual carries {total_carriers} recessive condition variant(s).** "
                 f"If the partner is from the same community or is a blood relative, "
                 f"the risk of the partner being a carrier for the same condition is significantly higher.\n")
        r.append("**Recommendation:** Partner carrier screening is **strongly recommended**, "
                 "especially if consanguinity or same-community marriage.\n")
    else:
        r.append("No recessive carrier variants detected in this screening. "
                 "However, consanguineous couples should still consider expanded carrier screening.\n")

    r.append("---\n")

    # =========================================================================
    # SECTION 8: CONFIDENCE AND LIMITATIONS
    # =========================================================================
    r.append("## 8. REPORT CONFIDENCE AND LIMITATIONS\n")

    r.append("### Data Quality Assessment\n")
    r.append("| Metric | Value |")
    r.append("|--------|-------|")
    total_snps = len(health_results.get('findings', [])) + len(health_results.get('pharmgkb_findings', []))
    r.append(f"| Total SNPs Analyzed | {health_results['summary'].get('total_snps_checked', 'N/A')} |")
    r.append(f"| Lifestyle/Health Findings | {len(findings)} |")
    r.append(f"| Drug Interactions | {len(pharmgkb)} |")
    if disease_stats:
        r.append(f"| ClinVar Matches | {disease_stats.get('matched', 'N/A')} |")
        r.append(f"| Quality-Flagged (Low Confidence) | {disease_stats.get('quality_flagged', 'N/A')} |")
    r.append("")

    r.append("### Important Limitations\n")
    r.append("1. **This is a screening report, NOT a diagnostic report.** All critical findings must be confirmed with targeted testing")
    r.append("2. **SNP-based screening has gaps:** Some conditions (especially SMA/SMN1 deletions) require MLPA/copy number analysis")
    r.append("3. **Population context:** Carrier frequencies are based on published Indian population studies. Individual risk may vary")
    r.append("4. **Reference genome:** VCF data uses hg38 coordinates. rsID-based matching is reliable; position-based matching may have minor discrepancies with older databases")
    r.append("5. **Not all Indian variants are in databases:** Some rare community-specific mutations may not be in ClinVar/PharmGKB")
    r.append("6. **Genetic counseling is essential:** For any carrier or pathogenic finding, formal genetic counseling should be offered\n")

    r.append("### Confidence Ratings by Section\n")
    r.append("| Section | Confidence | Notes |")
    r.append("|---------|------------|-------|")
    r.append("| Drug Sensitivities | **A (High)** | Well-established pharmacogenomic associations |")
    r.append("| Carrier Screening (SNP-based) | **B+ (Good)** | Strong for detected variants; may miss rare mutations |")
    r.append("| ClinVar Disease Variants | **B (Good)** | Depends on gold star rating of each variant |")
    r.append("| Nutrition/Metabolism | **B- (Moderate)** | Based on population studies, individual response varies |")
    r.append("| Consanguinity Risk | **C+ (Informational)** | Statistical estimate, not individual assessment |")
    r.append("")

    r.append("---\n")

    # =========================================================================
    # SECTION 9: DOCTOR'S QUICK REFERENCE CARD
    # =========================================================================
    r.append("## 9. DOCTOR'S QUICK REFERENCE CARD\n")
    r.append("*Print this section and attach to patient file*\n")

    r.append(f"**Patient:** {subject_name or 'Subject'}")
    r.append(f"**Date:** {now}")
    r.append(f"**Report:** Prenatal Genetic Screening (Indian Population)\n")

    r.append("### 🔴 MUST-KNOW Drug Alerts\n")
    if must_avoid:
        for d in must_avoid:
            r.append(f"- **NEVER GIVE:** {d['drug']} — {d['reason']}")
    if dose_adjust:
        for d in dose_adjust:
            r.append(f"- **ADJUST DOSE:** {d['drug']} — {d['adjustment']}")
    if not must_avoid and not dose_adjust:
        r.append("- No critical drug alerts")
    r.append("")

    r.append("### 🟡 Carrier Status\n")
    if all_carriers:
        for c in all_carriers:
            r.append(f"- **{c['condition']}** ({c['gene']}) — Partner test: {c['confirm_test']}")
    else:
        r.append("- No carrier conditions detected in screening")
    r.append("")

    r.append("### 🟢 Positive Findings\n")
    if total_affected == 0:
        r.append("- Zero confirmed disease variants")
    prot_count = len(disease_findings.get('protective', [])) if disease_findings else 0
    if prot_count > 0:
        r.append(f"- {prot_count} protective variant(s) detected")
    r.append("")

    r.append("### 📋 Priority Tests to Order\n")
    if all_carriers:
        for c in all_carriers:
            if c['urgency'] == 'HIGH':
                r.append(f"- [ ] **Partner:** {c['confirm_test']} for {c['condition']}")
    r.append("- [ ] 25-OH Vitamin D level")
    r.append("- [ ] Serum Ferritin + CBC")
    r.append("- [ ] HbA1c / Fasting glucose")
    r.append("")

    # Disclaimer
    r.append("\n---\n\n## Disclaimer\n")
    r.append("This report is generated from genomic sequencing data and is intended as a **screening tool only**. "
             "It is **NOT a clinical diagnosis**.\n")
    r.append("- All pathogenic/carrier findings must be confirmed with targeted genetic testing before clinical action")
    r.append("- Genetic counseling should be offered for all significant findings")
    r.append("- This report does not replace clinical judgment")
    r.append("- Variant classifications may change as scientific knowledge evolves")
    r.append("- Absence of a finding does not guarantee absence of risk\n")
    r.append("**Prepared by:** Automated Genetic Analysis Pipeline — Indian Prenatal Screening Module")
    r.append(f"**Generated:** {now}\n")

    output_path = Path(output_dir) / f"PRENATAL_REPORT_{safe}.md"
    output_path.write_text("\n".join(r))
    return output_path
