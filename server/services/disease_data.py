"""
Disease information database with treatments and prevention tips
"""

DISEASE_DATABASE = {
    "Pepper__bell___Bacterial_spot": {
        "plant_type": "Pepper",
        "disease_name": "Bacterial Spot",
        "is_healthy": False,
        "description": "Bacterial spot is caused by Xanthomonas bacteria and affects pepper plants, causing dark, water-soaked lesions on leaves and fruits.",
        "symptoms": "Dark, water-soaked spots on leaves; raised, scab-like spots on fruits; yellowing and leaf drop",
        "causes": "Spread through contaminated seeds, transplants, or by rain splash. Thrives in warm, humid conditions.",
        "treatment": "Remove and destroy infected plants. Apply copper-based bactericides. Avoid overhead watering.",
        "prevention": "Use certified disease-free seeds. Practice crop rotation. Space plants for good air circulation. Avoid working with wet plants.",
        "severity": "moderate",
        "recommendations": [
            "Remove infected plant parts immediately",
            "Apply copper-based spray every 7-10 days",
            "Improve air circulation between plants",
            "Avoid overhead irrigation",
            "Rotate crops next season"
        ]
    },
    "Pepper__bell___healthy": {
        "plant_type": "Pepper",
        "disease_name": "Healthy",
        "is_healthy": True,
        "description": "Your pepper plant appears healthy with no visible signs of disease.",
        "symptoms": "No symptoms - plant is healthy",
        "causes": "N/A",
        "treatment": "No treatment needed. Continue regular maintenance.",
        "prevention": "Maintain regular watering schedule. Ensure proper nutrition. Monitor for early signs of stress.",
        "severity": "none",
        "recommendations": [
            "Continue regular watering schedule",
            "Apply balanced fertilizer monthly",
            "Monitor for pest activity",
            "Ensure 6-8 hours of sunlight daily"
        ]
    },
    "Potato___Early_blight": {
        "plant_type": "Potato",
        "disease_name": "Early Blight",
        "is_healthy": False,
        "description": "Early blight is caused by Alternaria solani fungus. It typically affects older leaves first and can significantly reduce yield.",
        "symptoms": "Dark brown spots with concentric rings (target-like appearance); yellowing around lesions; premature defoliation",
        "causes": "Fungal spores spread by wind and rain. Favored by warm temperatures and high humidity.",
        "treatment": "Apply fungicides containing chlorothalonil or copper. Remove infected leaves. Ensure proper plant spacing.",
        "prevention": "Use resistant varieties. Practice crop rotation. Mulch to prevent soil splash. Remove plant debris.",
        "severity": "moderate",
        "recommendations": [
            "Remove and destroy infected leaves",
            "Apply fungicide spray every 7-14 days",
            "Mulch around plants to prevent splash",
            "Water at soil level, not on foliage",
            "Improve air circulation"
        ]
    },
    "Potato___healthy": {
        "plant_type": "Potato",
        "disease_name": "Healthy",
        "is_healthy": True,
        "description": "Your potato plant appears healthy with no visible signs of disease.",
        "symptoms": "No symptoms - plant is healthy",
        "causes": "N/A",
        "treatment": "No treatment needed. Continue regular maintenance.",
        "prevention": "Hill soil around stems. Maintain consistent moisture. Watch for pest damage.",
        "severity": "none",
        "recommendations": [
            "Hill soil around stems as plants grow",
            "Maintain consistent watering",
            "Apply fertilizer at planting and mid-season",
            "Monitor for Colorado potato beetles"
        ]
    },
    "Potato___Late_blight": {
        "plant_type": "Potato",
        "disease_name": "Late Blight",
        "is_healthy": False,
        "description": "Late blight is caused by Phytophthora infestans, the same pathogen responsible for the Irish Potato Famine. It's highly destructive and spreads rapidly.",
        "symptoms": "Water-soaked, pale green to brown lesions; white fuzzy growth on leaf undersides; rapid plant collapse",
        "causes": "Oomycete pathogen spread by wind-borne spores. Thrives in cool, wet conditions.",
        "treatment": "Apply fungicides immediately (mancozeb, chlorothalonil). Remove and destroy all infected plants. Do not compost infected material.",
        "prevention": "Use certified seed potatoes. Plant resistant varieties. Ensure good drainage. Destroy volunteer plants.",
        "severity": "severe",
        "recommendations": [
            "ACT IMMEDIATELY - this disease spreads rapidly",
            "Remove and burn all infected plants",
            "Apply systemic fungicide to remaining plants",
            "Do not save seed from infected fields",
            "Report outbreak to local agricultural extension"
        ]
    },
    "Tomato__Target_Spot": {
        "plant_type": "Tomato",
        "disease_name": "Target Spot",
        "is_healthy": False,
        "description": "Target spot is caused by Corynespora cassiicola fungus. It creates distinctive concentric ring patterns on leaves.",
        "symptoms": "Brown spots with concentric rings; spots may merge; severe defoliation possible",
        "causes": "Fungal infection favored by warm, humid conditions and poor air circulation.",
        "treatment": "Apply fungicides (azoxystrobin, chlorothalonil). Remove infected leaves. Improve air circulation.",
        "prevention": "Space plants properly. Stake or cage tomatoes. Water at base. Remove lower leaves.",
        "severity": "moderate",
        "recommendations": [
            "Remove infected lower leaves",
            "Apply fungicide every 7-10 days",
            "Stake plants for better air flow",
            "Water in morning at soil level",
            "Mulch to prevent splash"
        ]
    },
    "Tomato__Tomato_mosaic_virus": {
        "plant_type": "Tomato",
        "disease_name": "Tomato Mosaic Virus",
        "is_healthy": False,
        "description": "Tomato mosaic virus (ToMV) is a highly contagious viral disease that causes mottled leaves and reduced fruit production.",
        "symptoms": "Mottled light and dark green leaves; distorted or fern-like leaves; stunted growth; reduced fruit set",
        "causes": "Spread by contaminated tools, hands, or infected plant material. Can persist in soil and debris.",
        "treatment": "No cure exists. Remove and destroy infected plants. Disinfect all tools and wash hands thoroughly.",
        "prevention": "Use resistant varieties. Disinfect tools. Don't smoke near plants (tobacco mosaic virus is related). Start with certified seeds.",
        "severity": "severe",
        "recommendations": [
            "Remove infected plants immediately",
            "Wash hands with soap before handling healthy plants",
            "Disinfect all tools with 10% bleach solution",
            "Do not save seeds from infected plants",
            "Plant resistant varieties in future"
        ]
    },
    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "plant_type": "Tomato",
        "disease_name": "Tomato Yellow Leaf Curl Virus",
        "is_healthy": False,
        "description": "TYLCV is transmitted by whiteflies and causes severe yield losses. Infected plants produce little to no fruit.",
        "symptoms": "Upward curling leaves; yellowing leaf margins; stunted growth; small, pale leaves; flower drop",
        "causes": "Transmitted by silverleaf whitefly. Cannot be spread by tools or contact.",
        "treatment": "No cure. Remove and destroy infected plants. Control whitefly populations.",
        "prevention": "Use resistant varieties. Control whiteflies with insecticidal soap or neem. Use reflective mulches. Install fine mesh screens.",
        "severity": "severe",
        "recommendations": [
            "Remove and destroy infected plants",
            "Control whiteflies with yellow sticky traps",
            "Apply neem oil or insecticidal soap",
            "Use reflective mulch to repel whiteflies",
            "Plant resistant varieties"
        ]
    },
    "Tomato_Bacterial_spot": {
        "plant_type": "Tomato",
        "disease_name": "Bacterial Spot",
        "is_healthy": False,
        "description": "Bacterial spot affects tomato leaves, stems, and fruits, caused by several Xanthomonas species.",
        "symptoms": "Small, dark, water-soaked spots on leaves; raised, scabby spots on fruits; defoliation",
        "causes": "Bacteria spread by rain splash, overhead irrigation, and contaminated tools.",
        "treatment": "Apply copper-based bactericides. Remove severely infected plants. Avoid working with wet plants.",
        "prevention": "Use disease-free seeds. Rotate crops. Space plants properly. Avoid overhead watering.",
        "severity": "moderate",
        "recommendations": [
            "Apply copper spray every 5-7 days",
            "Remove heavily infected leaves",
            "Avoid overhead irrigation",
            "Do not work with wet plants",
            "Rotate crops for 2-3 years"
        ]
    },
    "Tomato_Early_blight": {
        "plant_type": "Tomato",
        "disease_name": "Early Blight",
        "is_healthy": False,
        "description": "Early blight is caused by Alternaria solani and is one of the most common tomato diseases.",
        "symptoms": "Dark brown spots with concentric rings; starts on lower leaves; yellowing and leaf drop",
        "causes": "Fungal spores overwinter in soil and plant debris. Spread by wind and rain.",
        "treatment": "Apply fungicides (chlorothalonil, copper, mancozeb). Remove infected leaves. Mulch heavily.",
        "prevention": "Rotate crops. Remove plant debris. Mulch to prevent splash. Water at soil level.",
        "severity": "moderate",
        "recommendations": [
            "Remove infected lower leaves",
            "Apply mulch 3-4 inches deep",
            "Use drip irrigation or water at base",
            "Apply fungicide preventatively",
            "Stake plants for air circulation"
        ]
    },
    "Tomato_healthy": {
        "plant_type": "Tomato",
        "disease_name": "Healthy",
        "is_healthy": True,
        "description": "Your tomato plant appears healthy with no visible signs of disease.",
        "symptoms": "No symptoms - plant is healthy",
        "causes": "N/A",
        "treatment": "No treatment needed. Continue regular maintenance.",
        "prevention": "Stake or cage plants. Maintain consistent watering. Apply balanced fertilizer.",
        "severity": "none",
        "recommendations": [
            "Continue regular watering - 1-2 inches per week",
            "Fertilize every 2-3 weeks with balanced fertilizer",
            "Prune suckers for better air circulation",
            "Monitor for pest and disease signs",
            "Harvest when fruits are ripe"
        ]
    },
    "Tomato_Late_blight": {
        "plant_type": "Tomato",
        "disease_name": "Late Blight",
        "is_healthy": False,
        "description": "Late blight is a devastating disease caused by Phytophthora infestans that can destroy entire crops in days.",
        "symptoms": "Large, irregular water-soaked lesions; white fuzzy growth; rapid plant death; firm brown rot on fruits",
        "causes": "Spreads rapidly in cool, wet weather. Airborne spores can travel miles.",
        "treatment": "Apply fungicides immediately. Remove and destroy all infected material. Do not compost.",
        "prevention": "Use resistant varieties. Ensure good air flow. Avoid overhead watering. Scout regularly in wet weather.",
        "severity": "severe",
        "recommendations": [
            "URGENT: Remove and destroy infected plants immediately",
            "Apply fungicide to remaining healthy plants",
            "Alert neighbors - spores travel by wind",
            "Avoid watering foliage",
            "Consider early harvest of green tomatoes"
        ]
    },
    "Tomato_Leaf_Mold": {
        "plant_type": "Tomato",
        "disease_name": "Leaf Mold",
        "is_healthy": False,
        "description": "Leaf mold is caused by Passalora fulva fungus and primarily affects greenhouse tomatoes or those in humid conditions.",
        "symptoms": "Pale green to yellow spots on upper leaves; olive-green to brown velvety growth on undersides",
        "causes": "High humidity (above 85%) and poor air circulation. Spores spread by air, water, and tools.",
        "treatment": "Improve ventilation. Reduce humidity. Apply fungicides. Remove infected leaves.",
        "prevention": "Maintain humidity below 85%. Space plants properly. Prune for air circulation. Water at soil level.",
        "severity": "moderate",
        "recommendations": [
            "Increase air circulation immediately",
            "Reduce humidity if in greenhouse",
            "Remove infected leaves",
            "Apply fungicide to remaining foliage",
            "Avoid wetting leaves when watering"
        ]
    },
    "Tomato_Septoria_leaf_spot": {
        "plant_type": "Tomato",
        "disease_name": "Septoria Leaf Spot",
        "is_healthy": False,
        "description": "Septoria leaf spot is caused by Septoria lycopersici fungus. It's common and can cause significant defoliation.",
        "symptoms": "Small circular spots with dark borders and gray centers; tiny black dots in spots; starts on lower leaves",
        "causes": "Fungal spores spread by rain splash and overhead watering. Overwinters in plant debris.",
        "treatment": "Remove infected leaves. Apply fungicides (chlorothalonil, copper). Mulch to prevent splash.",
        "prevention": "Remove plant debris. Rotate crops. Mulch heavily. Avoid overhead watering.",
        "severity": "moderate",
        "recommendations": [
            "Remove and destroy infected leaves",
            "Apply fungicide every 7-10 days",
            "Mulch to prevent soil splash",
            "Water at ground level only",
            "Clean up all debris at season end"
        ]
    },
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "plant_type": "Tomato",
        "disease_name": "Spider Mites (Two-spotted)",
        "is_healthy": False,
        "description": "Two-spotted spider mites are tiny arachnids that feed on plant cells, causing stippling and webbing on tomato plants.",
        "symptoms": "Yellow stippling on leaves; fine webbing; bronzed or dusty appearance; leaf drop",
        "causes": "Hot, dry conditions favor mite populations. Often worse when natural predators are killed by pesticides.",
        "treatment": "Spray with water to dislodge mites. Apply insecticidal soap or neem oil. Use miticides for severe infestations.",
        "prevention": "Maintain plant health. Avoid water stress. Encourage natural predators. Avoid broad-spectrum pesticides.",
        "severity": "moderate",
        "recommendations": [
            "Spray plants with strong water jet",
            "Apply neem oil or insecticidal soap",
            "Increase humidity around plants",
            "Release predatory mites if available",
            "Avoid dusty conditions"
        ]
    }
}


def get_disease_info(class_name: str) -> dict:
    """Get disease information for a predicted class"""
    return DISEASE_DATABASE.get(class_name, {
        "plant_type": "Unknown",
        "disease_name": class_name.replace("_", " "),
        "is_healthy": "healthy" in class_name.lower(),
        "description": "Disease information not available for this condition.",
        "symptoms": "Symptoms not documented.",
        "causes": "Causes not documented.",
        "treatment": "Please consult a local agricultural expert.",
        "prevention": "Practice good plant hygiene and regular monitoring.",
        "severity": "unknown",
        "recommendations": [
            "Consult local agricultural extension",
            "Take additional photos for diagnosis",
            "Monitor plant for changes"
        ]
    })
