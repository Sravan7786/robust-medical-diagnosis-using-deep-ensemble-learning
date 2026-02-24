import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "medical_diagnosis.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diagnosis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            modality TEXT,
            condition TEXT,
            confidence REAL,
            diagnostic_issue TEXT,
            observations TEXT,
            severity TEXT,
            recommendation TEXT,
            filename TEXT
        )
    ''')
    
    # Create a table for clinical knowledge base
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clinical_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            condition TEXT UNIQUE,
            base_observations TEXT,
            patient_explanation TEXT,
            standard_recommendation TEXT
        )
    ''')

    # Seed initial knowledge if empty
    cursor.execute("SELECT COUNT(*) FROM clinical_knowledge")
    if cursor.fetchone()[0] == 0:
        knowledge_data = [
            ('Normal', 'No focal consolidation, pneumothorax, or pleural effusion. Cardiac silhouette is within normal limits. Symmetrical patterns observed.', 'The scan shows no signs of disease or injury. Everything appears healthy and functioning normally.', 'Follow-up as per standard clinical screening guidelines.'),
            ('Pneumonia', 'Increased opacification/consolidation identified. Patchy infiltrates suggestive of inflammatory process.', 'There are signs of an infection in the lungs, which may cause difficulty breathing or coughing.', 'Correlation with clinical symptoms (fever, cough). Antibiotic therapy as indicated. Follow-up imaging in 4-6 weeks.'),
            ('Tumor', 'Well-defined focal mass lesion with signal intensity variation. Mass effect on adjacent structures noted.', 'A persistent growth or mass has been detected that requires further investigation to determine its nature.', 'Contrast-enhanced MRI for characterization. Biopsy/Neurological consultation required.'),
            ('Fracture', 'Disruption of cortical continuity and trabecular misalignment. Associated soft tissue swelling.', 'A break or crack has been detected in the bone structure, likely due to recent injury.', 'Immobilization/Splinting. Orthopedic consultation. Surgical evaluation if displaced.'),
            ('Stroke', 'Area of restricted diffusion/ischemic change. Cytotoxic edema observed in the vascular territory.', 'Areas of the brain are showing reduced blood flow, which requires immediate medical attention.', 'Emergency neurological management. Assessment for thrombolytic eligibility. Stroke unit admission.'),
            ('Cardiomegaly', 'Transverse diameter of the heart exceeds 50% of the internal thoracic diameter. Prominent cardiac silhouette.', 'The heart appears larger than normal, which can sometimes be a sign of underlying heart conditions.', 'Clinical correlation for congestive heart failure. Echocardiography recommended.'),
            ('Pneumothorax', 'Visible visceral pleural line with absence of peripheral lung markings. Hyperlucent area.', 'There is air trapped outside the lung, causing it to partially collapse.', 'Urgent clinical assessment. Consideration for chest tube insertion if significant or symptomatic.')
        ]
        cursor.executemany('INSERT INTO clinical_knowledge (condition, base_observations, patient_explanation, standard_recommendation) VALUES (?, ?, ?, ?)', knowledge_data)

    # Migration for older versions
    try:
        cursor.execute("ALTER TABLE clinical_knowledge ADD COLUMN patient_explanation TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

def save_diagnosis(modality, condition, confidence, report, filename):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Flatten structured report for fallback database schema
    observation_text = " | ".join(report.get('clinical_findings', []))
    impression = report.get('impression', '')
    
    cursor.execute('''
        INSERT INTO diagnosis_history (
            modality, condition, confidence, diagnostic_issue, observations, severity, recommendation, filename
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        modality, 
        condition, 
        confidence, 
        impression, 
        observation_text, 
        report.get('severity', ''), 
        report.get('recommendation', ''),
        filename
    ))
    conn.commit()
    conn.close()

def get_clinical_knowledge(condition):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clinical_knowledge WHERE condition = ?', (condition,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_history(limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM diagnosis_history ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    history = [dict(row) for row in rows]
    conn.close()
    return history

if __name__ == "__main__":
    init_db()
    print("Database initialized with Clinical Knowledge Base.")
