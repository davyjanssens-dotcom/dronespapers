# 🚁 Drone Papers Analysis Dashboard

Een interactieve dashboard voor het analyseren van 569 wetenschappelijke papers over UAV-based traffic en pedestrian monitoring.

## 📊 Dataset Overzicht

- **Totaal aantal papers**: 569
- **Tijdsperiode**: 2001-2026
- **Bron**: Bilal Drones Data References

## 🎯 Hoofdcategorieën

### Detection & Tracking (78 papers)
Object detection en tracking algoritmes voor UAV beelden

### Parking Management (10 papers)
Parkeerplaats detectie en monitoring systemen

### Pedestrian Analysis (124 papers)
Voetgangersgedrag, -detectie en -tracking

### Traffic Flow (46 papers)
Verkeersstroom analyse, congestion monitoring, vehicle counting

### Speed Estimation (69 papers)
Snelheidsmetingen van voertuigen en voetgangers

### Deep Learning (35 papers)
YOLO, CNN, en andere neural network architecturen

### Real-time Processing (30 papers)
Real-time video verwerking en edge computing

### Datasets (32 papers)
VisDrone, UAVDT, CARPK, openDD, UA-DETRAC

## 🔬 Onderzoeksthema's

### 1. Methodologisch
- YOLO-varianten (v4, v5, v8, v10, v11) vergelijkingen
- Multi-scale feature fusion
- Attention mechanisms
- Tracking algoritmes (SORT, DeepSORT, ByteTrack)

### 2. Technisch
- Real-time processing bottlenecks
- Edge computing (Jetson, Coral)
- Image registration & stabilization
- On-device inference

### 3. Toepassing
- Parking occupancy monitoring
- Pedestrian behavior analysis
- Traffic flow & congestion
- Roundabout trajectory analysis
- Traffic violation detection

### 4. Economisch
- Cost-benefit analyses (60-80% kostenreductie)
- Deployment scalability
- ROI bij verschillende operational intensities

## 🚀 Gebruik

### Dashboard Starten
```bash
cd "papers downloader"
python3 -m http.server 8000
```

Open browser: `http://localhost:8000/dashboard.html`

### Papers Analyseren
```bash
python3 analyze_papers.py
```

## 📁 Bestanden

- `dashboard.html` - Interactieve papers browser met DOI links
- `bilal drones data references.bib` - BibTeX database (569 papers)
- `onderzoeksvragen_analyse.md` - Uitgebreide analyse met onderzoeksvragen
- `analyze_papers.py` - Python script voor paper categorisatie

## 🔑 Belangrijkste Bevindingen

### Methodologisch
- YOLOv8 en YOLOv10 met knowledge distillation tonen beste real-time prestaties
- Multi-scale feature fusion essentieel voor kleine object detectie
- Attention mechanisms verbeteren detectie in complexe achtergronden

### Technisch
- Minimale frame rate: 3+ Hz voor automatische tracking
- NVIDIA Jetson TX2 kan 4K real-time processing aan
- Image registration (SIFT, SURF) cruciaal voor bewegende camera's

### Toepassing
- Optimale vlieghoogte: ~50m voor balans coverage/resolutie
- 95-100% detection rates haalbaar voor vehicles/cyclists/pedestrians
- UAVs kunnen origin-destination matrices genereren

### Economisch
- 60-80% kostenreductie vs traditionele methoden
- 8-point density threshold voor economische viability
- 81.6% viability bij 180 dagen operationele intensiteit

## 📈 Trends

**2016-2018**: Opkomst deep learning (YOLO, Faster R-CNN)  
**2019-2021**: Focus op real-time processing  
**2022-2024**: Multi-task frameworks  
**2025-2026**: Knowledge distillation, economic feasibility

## 🎓 Research Gaps

1. Cross-domain generalization
2. Extreme weather performance
3. Long-term deployment studies
4. Privacy-preserving techniques
5. Total Cost of Ownership analyses

## 📚 Top Datasets

- **VisDrone2019**: Urban traffic, vehicles & pedestrians
- **UAVDT**: UAV detection and tracking
- **CARPK**: 90,000 cars in parking lots
- **openDD**: 84,774 trajectories in roundabouts
- **UA-DETRAC**: Urban road environments

## 🔗 Links

- Dashboard: `http://localhost:8000/dashboard.html`
- Volledige analyse: [onderzoeksvragen_analyse.md](onderzoeksvragen_analyse.md)

---

*Laatste update: Maart 2026*
