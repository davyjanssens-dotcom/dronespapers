import re
from collections import defaultdict

def parse_bib_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = content.split('@')[1:]
    papers = []
    
    for entry in entries:
        paper = {}
        
        type_match = re.match(r'(\w+)\{([^,]+),', entry)
        if type_match:
            paper['type'] = type_match.group(1)
            paper['id'] = type_match.group(2)
        
        fields = {
            'title': r'title\s*=\s*\{\{([^}]+)\}\}',
            'title_alt': r'title\s*=\s*\{([^}]+)\}',
            'author': r'author\s*=\s*\{([^}]+)\}',
            'year': r'year\s*=\s*\{([^}]+)\}',
            'abstract': r'abstract\s*=\s*\{([^}]+)\}',
            'keywords': r'keywords\s*=\s*\{([^}]+)\}',
            'journal': r'journal\s*=\s*\{([^}]+)\}',
        }
        
        for key, pattern in fields.items():
            match = re.search(pattern, entry)
            if match:
                if key == 'title_alt' and 'title' not in paper:
                    paper['title'] = match.group(1).strip()
                elif key != 'title_alt':
                    paper[key] = match.group(1).strip()
        
        if 'title' in paper:
            papers.append(paper)
    
    return papers

def categorize_papers(papers):
    categories = {
        'detection_tracking': [],
        'parking': [],
        'pedestrian': [],
        'traffic_flow': [],
        'speed_estimation': [],
        'dataset': [],
        'methodology': [],
        'real_time': [],
        'deep_learning': []
    }
    
    for paper in papers:
        text = (paper.get('title', '') + ' ' + 
                paper.get('abstract', '') + ' ' + 
                paper.get('keywords', '')).lower()
        
        if 'parking' in text:
            categories['parking'].append(paper)
        if 'pedestrian' in text:
            categories['pedestrian'].append(paper)
        if 'detection' in text or 'tracking' in text:
            categories['detection_tracking'].append(paper)
        if 'traffic flow' in text or 'congestion' in text or 'counting' in text:
            categories['traffic_flow'].append(paper)
        if 'speed' in text or 'velocity' in text:
            categories['speed_estimation'].append(paper)
        if 'dataset' in text:
            categories['dataset'].append(paper)
        if 'yolo' in text or 'cnn' in text or 'deep learning' in text or 'neural network' in text:
            categories['deep_learning'].append(paper)
        if 'real-time' in text or 'real time' in text:
            categories['real_time'].append(paper)
    
    return categories

def extract_research_questions(papers):
    questions = {
        'Methodologisch': [],
        'Toepassing': [],
        'Technisch': [],
        'Economisch/Praktisch': []
    }
    
    for paper in papers:
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        keywords = paper.get('keywords', '')
        year = paper.get('year', '')
        
        if 'parking' in (title + abstract).lower():
            questions['Toepassing'].append({
                'question': 'Hoe kunnen UAVs effectief worden ingezet voor real-time parkeerplaats detectie en monitoring?',
                'papers': [title],
                'year': year
            })
        
        if 'yolo' in (title + abstract + keywords).lower():
            questions['Methodologisch'].append({
                'question': 'Welke YOLO-varianten presteren het best voor object detectie in UAV beelden?',
                'papers': [title],
                'year': year
            })
        
        if 'pedestrian' in (title + abstract).lower():
            questions['Toepassing'].append({
                'question': 'Hoe kunnen UAVs worden gebruikt voor voetgangersgedrag analyse en veiligheidsmonitoring?',
                'papers': [title],
                'year': year
            })
        
        if 'real-time' in (title + abstract).lower() or 'real time' in (title + abstract).lower():
            questions['Technisch'].append({
                'question': 'Wat zijn de technische uitdagingen voor real-time verwerking van UAV video streams?',
                'papers': [title],
                'year': year
            })
        
        if 'economic' in (title + abstract).lower() or 'cost' in (title + abstract).lower():
            questions['Economisch/Praktisch'].append({
                'question': 'Wat is de economische haalbaarheid van UAV-gebaseerde verkeerssystemen vs traditionele methoden?',
                'papers': [title],
                'year': year
            })
    
    return questions

papers = parse_bib_file('bilal drones data references.bib')
print(f"Totaal aantal papers: {len(papers)}\n")

categories = categorize_papers(papers)

print("=" * 80)
print("CATEGORISATIE VAN PAPERS")
print("=" * 80)
for category, paper_list in categories.items():
    if paper_list:
        print(f"\n{category.upper().replace('_', ' ')}: {len(paper_list)} papers")
        for p in paper_list[:3]:
            print(f"  - {p.get('title', 'No title')} ({p.get('year', 'N/A')})")

print("\n" + "=" * 80)
print("ONDERZOEKSVRAGEN PER THEMA")
print("=" * 80)

research_questions = extract_research_questions(papers)

for theme, questions in research_questions.items():
    if questions:
        print(f"\n{theme}:")
        unique_q = {}
        for q in questions:
            if q['question'] not in unique_q:
                unique_q[q['question']] = q
        
        for question, data in unique_q.items():
            print(f"  • {question}")
            print(f"    Voorbeeld: {data['papers'][0][:80]}...")
