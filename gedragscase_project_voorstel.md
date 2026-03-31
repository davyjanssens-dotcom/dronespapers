# 🎯 Project Voorstel: Gedragscase Clustering via Drone Beelden

## 📋 Project Overzicht

**Doel**: Automatische identificatie en clustering van verkeerssituaties en gedragspatronen uit drone beelden om herbruikbare "gedragscases" te creëren voor verdere analyse.

---

## 🔍 Relevante Papers & Methodologieën

### 1. **Trajectory-Based Analysis**

#### openDD Dataset (Breuer et al., 2020)
- **Wat**: 84,774 nauwkeurig getrackte trajectories van 7 verschillende rotondes
- **Relevantie**: Toont hoe trajectories kunnen worden gebruikt voor behavior clustering
- **Methodologie**: 
  - HD map data + trajectory extraction
  - 62 uur aan trajectory data
  - Interaction patterns tussen weggebruikers
- **Jouw toepassing**: Basis voor trajectory-based clustering

#### UAV-Based Intelligent Traffic Surveillance (Khanpour et al., 2025)
- **Wat**: Real-time vehicle detection, classification, tracking, en behavioral analysis
- **Relevantie**: Integreert behavioral analysis in UAV pipeline
- **Methodologie**:
  - Origin-destination tracking
  - Traffic violation detection (lane changes, double parking, crosswalk obstructions)
  - Trajectory deviation analysis
  - Movement direction logging
- **Jouw toepassing**: Framework voor behavior classification

### 2. **Traffic Pattern Analysis**

#### Traffic Vision (Alnusayri et al., 2026)
- **Wat**: UAV-based vehicle detection + traffic pattern analysis
- **Relevantie**: Combineert detection met pattern recognition
- **Methodologie**:
  - LSTM-based trajectory forecasting
  - Optical-flow density estimation
  - VGG16 classification voor pattern types
- **Jouw toepassing**: Pattern clustering algoritmes

#### Pedestrian Behavior Study (Sutheerakul et al., 2017)
- **Wat**: UAV voor pedestrian traffic flow monitoring op shopping streets
- **Relevantie**: Toont hoe UAV data gebruikt kan worden voor behavior analysis
- **Methodologie**:
  - Traffic demand and supply management
  - Pedestrian flow characteristics
  - Behavior patterns in outdoor zones
- **Jouw toepassing**: Multi-modal behavior clustering (voetgangers + voertuigen)

### 3. **Conflict & Interaction Detection**

#### Surrogate Safety Measures (Gettman & Head, 2003)
- **Wat**: Framework voor safety assessment via traffic simulation
- **Relevantie**: Definieert metrics voor conflict detection
- **Methodologie**:
  - Traffic conflicts identification
  - Surrogate safety measures (TTC, PET)
  - Intersection safety assessment
- **Jouw toepassing**: Safety-based clustering van situaties

#### Multi-Object Trajectory Tracking (Han et al., 2007)
- **Wat**: Trajectory tracking voor multi-object scenarios
- **Relevantie**: Detecteert interactions tussen objecten
- **Methodologie**:
  - Joint multi-object state-observation probability
  - Trajectory-based analysis
  - Multi-object configuration analysis
- **Jouw toepassing**: Interaction-based clustering

### 4. **Behavioral Analysis Frameworks**

#### Traffic and Self-Driven Systems (Helbing, 2001)
- **Wat**: Fundamentele traffic dynamics en behavior modeling
- **Relevantie**: Theoretische basis voor behavior clustering
- **Methodologie**:
  - Microscopic (particle-based) models
  - Mesoscopic (gas-kinetic) models
  - Macroscopic (fluid-dynamic) models
- **Jouw toepassing**: Multi-level behavior representation

#### Pedestrian Walking Speed Monitoring (Jiao & Fei, 2023)
- **Wat**: Street-scale pedestrian behavior extraction
- **Relevantie**: Toont hoe behavior metrics kunnen worden geëxtraheerd
- **Methodologie**:
  - YOLOv5 + DeepSORT voor tracking
  - Geometric correction voor accurate measurements
  - Behavior analysis op street scale
- **Jouw toepassing**: Feature extraction voor clustering

---

## 🏗️ Voorgestelde Architectuur

### Pipeline Overzicht

```
Drone Beelden
    ↓
1. Detection & Tracking (YOLOv10 + ByteTrack)
    ↓
2. Trajectory Extraction
    ↓
3. Feature Engineering
    ↓
4. Behavior Clustering
    ↓
5. Case Database
```

### Stap 1: Detection & Tracking
**Gebaseerd op**: Khan et al. (2026), Alnusayri et al. (2026)

**Implementatie**:
- YOLOv10-S met knowledge distillation voor detection
- ByteTrack voor multi-object tracking
- Object classificatie: vehicles, pedestrians, cyclists

**Output**: Tracked objects met IDs over tijd

### Stap 2: Trajectory Extraction
**Gebaseerd op**: Breuer et al. (2020), Khanpour et al. (2025)

**Implementatie**:
- Homography-based calibration voor world coordinates
- Trajectory smoothing (Kalman filtering)
- Velocity en acceleration berekening

**Output**: Trajectory data per object (x, y, t, v, a, class)

### Stap 3: Feature Engineering
**Gebaseerd op**: Meerdere papers

**Features per situatie**:

#### Spatial Features
- Object density (aantal objecten per m²)
- Spatial distribution (clustering coefficient)
- Distance matrices tussen objecten
- Lane occupancy

#### Temporal Features
- Speed distributions
- Acceleration patterns
- Stop frequency
- Dwell time

#### Interaction Features
- Time-to-Collision (TTC)
- Post-Encroachment Time (PET)
- Proximity events
- Overtaking maneuvers
- Lane change frequency

#### Behavioral Features
- Trajectory curvature
- Direction changes
- Group behavior (pedestrians)
- Violation events (red light, illegal parking)

### Stap 4: Behavior Clustering
**Gebaseerd op**: Traffic pattern analysis papers

**Clustering Methoden**:

#### A. Unsupervised Clustering
- **K-means**: Voor duidelijk gescheiden gedragstypen
- **DBSCAN**: Voor density-based clustering (detecteert outliers)
- **Hierarchical Clustering**: Voor multi-level behavior taxonomy
- **Gaussian Mixture Models**: Voor overlappende behaviors

#### B. Deep Learning Clustering
- **Autoencoder**: Latent space representation van situations
- **VAE (Variational Autoencoder)**: Generative model voor similar cases
- **t-SNE/UMAP**: Visualisatie van behavior space

#### C. Sequence Clustering
- **LSTM Autoencoder**: Voor temporal pattern clustering
- **Dynamic Time Warping (DTW)**: Voor trajectory similarity
- **Hidden Markov Models**: Voor state-based clustering

### Stap 5: Case Database
**Gebaseerd op**: Dataset papers (VisDrone, openDD)

**Database Schema**:
```
Case {
  id: unique_id
  cluster_label: behavior_type
  timestamp: datetime
  location: GPS coordinates
  duration: seconds
  
  objects: [
    {type, trajectory, speed_profile, interactions}
  ]
  
  features: {
    spatial: {...}
    temporal: {...}
    interaction: {...}
  }
  
  metadata: {
    weather, lighting, traffic_density
  }
  
  video_clip: link_to_footage
  thumbnail: representative_frame
}
```

---

## 🎯 Concrete Gedragscases (Voorbeelden)

### 1. **Parking Behavior**
**Clusters**:
- Normal parking (smooth entry)
- Hesitant parking (multiple attempts)
- Illegal parking (no-parking zone)
- Double parking
- Parking search behavior (circling)

**Features**: Trajectory curvature, dwell time, proximity to parking lines

### 2. **Intersection Behavior**
**Clusters**:
- Compliant crossing (following signals)
- Aggressive crossing (running red light)
- Hesitant crossing (stopping mid-intersection)
- Conflict situations (near-miss events)
- Roundabout yielding patterns

**Features**: TTC, PET, speed at intersection, trajectory deviation

### 3. **Pedestrian Crossing**
**Clusters**:
- Zebra crossing usage
- Jaywalking
- Group crossing
- Waiting behavior
- Pedestrian-vehicle conflicts

**Features**: Crossing location, group size, waiting time, vehicle proximity

### 4. **Traffic Flow States**
**Clusters**:
- Free flow
- Synchronized flow
- Stop-and-go
- Congestion
- Incident-related disruption

**Features**: Speed variance, density, flow rate, shockwave propagation

### 5. **Lane Change Behavior**
**Clusters**:
- Safe lane change (with indicator)
- Aggressive lane change
- Forced merge
- Weaving behavior
- Lane discipline violations

**Features**: Lateral acceleration, gap acceptance, indicator usage

### 6. **Pedestrian-Vehicle Interaction**
**Clusters**:
- Vehicle yields to pedestrian
- Pedestrian yields to vehicle
- Simultaneous yielding (deadlock)
- Conflict (neither yields)
- Cooperative crossing

**Features**: Approach speeds, deceleration patterns, eye contact proxy

---

## 🛠️ Implementatie Stappenplan

### Fase 1: Data Collection (Weken 1-2)
1. Selecteer diverse locaties (intersections, parking lots, shopping streets)
2. Verzamel drone footage (verschillende tijden, weersomstandigheden)
3. Annoteer ground truth voor validation
4. **Papers**: Sutheerakul (2017) voor data collection best practices

### Fase 2: Detection & Tracking Pipeline (Weken 3-4)
1. Implementeer YOLOv10 detection
2. Integreer ByteTrack tracking
3. Calibreer camera voor world coordinates
4. **Papers**: Khan (2026), Alnusayri (2026)

### Fase 3: Feature Engineering (Weken 5-6)
1. Extract spatial features
2. Compute temporal features
3. Calculate interaction metrics (TTC, PET)
4. **Papers**: Gettman (2003), Khanpour (2025)

### Fase 4: Clustering Experiments (Weken 7-8)
1. Test verschillende clustering algoritmes
2. Determine optimal number of clusters
3. Validate clusters met domain experts
4. **Papers**: Helbing (2001) voor behavior theory

### Fase 5: Case Database & Visualization (Weken 9-10)
1. Build case database
2. Create visualization dashboard
3. Implement case retrieval system
4. **Papers**: Breuer (2020) voor dataset structure

### Fase 6: Validation & Refinement (Weken 11-12)
1. Cross-validate met nieuwe data
2. Refine cluster definitions
3. Document behavior taxonomy
4. Prepare case studies

---

## 📊 Verwachte Output

### 1. **Behavior Taxonomy**
Hierarchische classificatie van alle geobserveerde gedragingen:
```
Traffic Behaviors
├── Vehicle Behaviors
│   ├── Parking
│   │   ├── Normal
│   │   ├── Hesitant
│   │   └── Illegal
│   ├── Lane Changes
│   └── Intersection
├── Pedestrian Behaviors
│   ├── Crossing
│   ├── Waiting
│   └── Group Movement
└── Interactions
    ├── Vehicle-Vehicle
    ├── Vehicle-Pedestrian
    └── Pedestrian-Pedestrian
```

### 2. **Case Library**
Database met 1000+ geclusterde situaties:
- Searchable by behavior type
- Filterable by location, time, weather
- Linked to video clips
- Annotated with features

### 3. **Visualization Dashboard**
Interactive tool voor:
- Cluster exploration (t-SNE plots)
- Case comparison
- Trajectory playback
- Statistical analysis per cluster

### 4. **API voor Case Retrieval**
```python
# Voorbeeld gebruik
cases = get_cases(
    behavior_type="aggressive_lane_change",
    location="intersection_A",
    min_conflict_severity=0.7
)

similar_cases = find_similar(
    reference_case=case_123,
    similarity_threshold=0.85
)
```

---

## 🔬 Wetenschappelijke Bijdrage

### Novelty
1. **Unified Framework**: Eerste systeem dat detection, tracking, en behavior clustering integreert
2. **Multi-Modal**: Combineert vehicles, pedestrians, cyclists in één framework
3. **Hierarchical Clustering**: Multi-level behavior taxonomy
4. **Reusable Cases**: Case database voor training en validation

### Toepassingen
1. **Traffic Safety**: Identificeer gevaarlijke situaties
2. **Urban Planning**: Inform infrastructure design
3. **Autonomous Vehicles**: Training data voor edge cases
4. **Policy Making**: Evidence-based traffic regulations
5. **Simulation Validation**: Real-world behavior patterns

---

## 📚 Aanbevolen Papers om te Lezen

### Must-Read (Top 5)
1. **Khanpour et al. (2025)** - UAV-Based Intelligent Traffic Surveillance
   - Meest complete behavioral analysis framework
   
2. **Breuer et al. (2020)** - openDD Dataset
   - Best practice voor trajectory dataset creation
   
3. **Alnusayri et al. (2026)** - Traffic Vision
   - Pattern analysis methodologie
   
4. **Gettman & Head (2003)** - Surrogate Safety Measures
   - Conflict detection metrics
   
5. **Khan et al. (2026)** - Unified Framework
   - State-of-the-art detection + tracking

### Aanvullend (Top 5)
6. **Jiao & Fei (2023)** - Pedestrian Walking Speed
7. **Sutheerakul et al. (2017)** - Pedestrian Traffic Monitoring
8. **Helbing (2001)** - Traffic Dynamics Theory
9. **Hsieh et al. (2017)** - Drone-Based Object Counting (CARPK dataset)
10. **Byun et al. (2021)** - Road Traffic Monitoring

---

## 🚀 Quick Start

### Minimale Implementatie (MVP)
Voor een proof-of-concept in 2-3 weken:

1. **Dataset**: Gebruik bestaande VisDrone2019 of UAVDT
2. **Detection**: Pre-trained YOLOv8 model
3. **Tracking**: DeepSORT (simpeler dan ByteTrack)
4. **Features**: Alleen spatial + temporal (skip interactions)
5. **Clustering**: K-means met k=5-10 clusters
6. **Validation**: Manual inspection van clusters

### Code Skeleton
```python
# 1. Detection & Tracking
detector = YOLOv8('yolov8n.pt')
tracker = DeepSORT()

# 2. Feature Extraction
features = extract_features(trajectories)
# - speed_mean, speed_std
# - trajectory_length
# - direction_changes
# - density

# 3. Clustering
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=8)
labels = kmeans.fit_predict(features)

# 4. Case Database
cases = create_cases(trajectories, labels, features)
save_to_database(cases)
```

---

## 💡 Vervolgstappen

1. **Lees de 5 must-read papers**
2. **Definieer je specifieke use case** (parking? intersections? pedestrians?)
3. **Verzamel of download dataset** (VisDrone2019 is gratis beschikbaar)
4. **Implementeer MVP** (2-3 weken)
5. **Itereer op basis van resultaten**

---

## 📞 Vragen voor Verdere Specificatie

1. **Welk type situaties interesseren je het meest?**
   - Parking behavior?
   - Intersection conflicts?
   - Pedestrian patterns?
   - Traffic flow states?

2. **Wat is je primaire toepassing?**
   - Safety analysis?
   - Urban planning?
   - Simulation validation?
   - Autonomous vehicle training?

3. **Heb je al drone footage of gebruik je bestaande datasets?**

4. **Wat is je technische achtergrond?**
   - Python/ML ervaring?
   - Computer vision kennis?
   - Traffic engineering background?

---

*Dit voorstel is gebaseerd op analyse van 569 papers uit de Bilal Drones Data References collectie*
