"""
TRT Transcript Processing Pipeline for RAG Embedding
Extracts and labels therapeutic exchanges from session transcripts
"""

import json
import re
from typing import List, Dict, Any

class TRTTranscriptProcessor:
    def __init__(self):
        self.trt_stages = {
            "stage_1_safety_building": ["goal_setting", "problem_construction", "body_awareness", "vision_building"],
            "stage_2_logical_levels": ["brain_responsibility", "zebra_lion_reframe"],
            "stage_3_trauma_explanation": ["timing_meaning", "why_trauma_sticks"]
        }

        self.dr_q_techniques = {
            "multiple_goal_questions": ["what do we want", "what do you want", "how do we want you"],
            "how_do_you_know_inquiry": ["how do you know when", "what is it that's happening"],
            "present_moment_body": ["right now", "even talking about it now", "what do you notice"],
            "future_self_visioning": ["we want you to be", "more peaceful", "emotionally present"],
            "somatic_questioning": ["where in the", "what kind of", "is it an ache"],
            "normalization_support": ["this is stuff", "really difficult", "really heavy"]
        }

        self.situation_types = {
            "initial_goal_inquiry": ["session start", "goal clarification"],
            "body_symptom_exploration": ["pain", "ache", "tension", "tight"],
            "emotional_pattern_inquiry": ["feel like", "always feel", "when you"],
            "future_vision_building": ["we want you", "seeing you", "grounded"],
            "present_moment_awareness": ["right now", "in this moment", "talking about it now"],
            "normalization_emotional_response": ["crying", "emotional", "tears"]
        }

    def extract_exchanges_from_txt(self, file_path: str) -> List[Dict]:
        """Extract doctor-patient exchanges from .txt transcript"""
        exchanges = []

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_exchange = {"doctor_lines": [], "patient_lines": []}
        exchange_id = 1

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('[DOCTOR]:'):
                # If we have patient content, save current exchange
                if current_exchange["patient_lines"]:
                    exchange = self._create_exchange(current_exchange, exchange_id)
                    if exchange:
                        exchanges.append(exchange)
                        exchange_id += 1
                    current_exchange = {"doctor_lines": [], "patient_lines": []}

                # Add doctor line
                doctor_text = line.replace('[DOCTOR]:', '').strip()
                if doctor_text:
                    current_exchange["doctor_lines"].append(doctor_text)

            elif line.startswith('[PATIENT]:'):
                patient_text = line.replace('[PATIENT]:', '').strip()
                if patient_text:
                    current_exchange["patient_lines"].append(patient_text)

        # Process final exchange
        if current_exchange["patient_lines"]:
            exchange = self._create_exchange(current_exchange, exchange_id)
            if exchange:
                exchanges.append(exchange)

        return exchanges

    def _create_exchange(self, exchange_data: Dict, exchange_id: int) -> Dict:
        """Create structured exchange from raw data"""
        doctor_input = " ".join(exchange_data["doctor_lines"])
        patient_response = " ".join(exchange_data["patient_lines"])

        if not doctor_input or not patient_response:
            return None

        return {
            "exchange_id": f"session_{exchange_id:03d}",
            "doctor_input": doctor_input,
            "patient_response": patient_response,
            "raw_doctor_lines": exchange_data["doctor_lines"],
            "raw_patient_lines": exchange_data["patient_lines"]
        }

    def label_exchange(self, exchange: Dict) -> Dict:
        """Add therapeutic labels to exchange"""
        doctor_text = exchange["doctor_input"].lower()
        patient_text = exchange["patient_response"].lower()

        # Detect TRT stage and substate
        trt_labels = self._detect_trt_stage_substate(doctor_text, patient_text)

        # Detect Dr. Q technique
        dr_q_technique = self._detect_dr_q_technique(doctor_text)

        # Detect situation type
        situation_type = self._detect_situation_type(doctor_text, patient_text)

        # Create embedding tags
        embedding_tags = self._create_embedding_tags(doctor_text, patient_text, trt_labels)

        # Create RAG retrieval contexts
        rag_contexts = self._create_rag_contexts(trt_labels, situation_type, dr_q_technique)

        exchange["therapeutic_labels"] = {
            "trt_stage": trt_labels["stage"],
            "trt_substate": trt_labels["substate"],
            "situation_type": situation_type,
            "dr_q_technique": dr_q_technique,
            "client_presentation": self._analyze_client_presentation(patient_text),
            "outcome": self._assess_exchange_outcome(doctor_text, patient_text)
        }

        exchange["embedding_tags"] = embedding_tags
        exchange["rag_retrieval_contexts"] = rag_contexts

        return exchange

    def _detect_trt_stage_substate(self, doctor_text: str, patient_text: str) -> Dict:
        """Detect TRT stage and substate based on content"""

        # Stage 1 indicators
        if any(phrase in doctor_text for phrase in ["what do we want", "what do you want", "how do we want you"]):
            if "peaceful" in patient_text or "calm" in patient_text:
                return {"stage": "stage_1_safety_building", "substate": "1.1_goal_and_vision"}

        if "how do you know when" in doctor_text:
            return {"stage": "stage_1_safety_building", "substate": "1.2_problem_and_body"}

        if any(phrase in doctor_text for phrase in ["where in the", "what kind of", "right now"]):
            return {"stage": "stage_1_safety_building", "substate": "1.2_problem_and_body"}

        if "we want you to be" in doctor_text:
            return {"stage": "stage_1_safety_building", "substate": "1.1_goal_and_vision"}

        if "what else comes to mind" in doctor_text:
            return {"stage": "stage_1_safety_building", "substate": "1.3_readiness_assessment"}

        # Default to stage 1 if unclear
        return {"stage": "stage_1_safety_building", "substate": "1.1_goal_and_vision"}

    def _detect_dr_q_technique(self, doctor_text: str) -> str:
        """Detect specific Dr. Q technique used"""

        for technique, patterns in self.dr_q_techniques.items():
            if any(pattern in doctor_text for pattern in patterns):
                return technique

        return "general_inquiry"

    def _detect_situation_type(self, doctor_text: str, patient_text: str) -> str:
        """Detect therapeutic situation type"""

        # Goal setting situations
        if any(phrase in doctor_text for phrase in ["what do we want", "what do you want"]):
            return "initial_goal_inquiry"

        # Body symptom situations
        if any(word in patient_text for word in ["pain", "ache", "tight", "hurt", "tension"]):
            return "body_symptom_exploration"

        # Present moment awareness
        if any(phrase in doctor_text for phrase in ["right now", "even talking about", "what do you notice"]):
            return "present_moment_awareness"

        # Future vision building
        if "we want you to be" in doctor_text:
            return "future_vision_building"

        # Emotional pattern inquiry
        if "how do you know when" in doctor_text:
            return "emotional_pattern_inquiry"

        return "general_therapeutic_inquiry"

    def _analyze_client_presentation(self, patient_text: str) -> List[str]:
        """Analyze how client presents in this exchange"""
        presentations = []

        if any(word in patient_text for word in ["peaceful", "calm", "happy"]):
            presentations.append("clear_goal_stated")

        if any(word in patient_text for word in ["work", "boss", "job"]):
            presentations.append("work_related_stress")

        if any(word in patient_text for word in ["pain", "ache", "hurt"]):
            presentations.append("physical_symptoms")

        if "yes" in patient_text and ("want" in patient_text or "that" in patient_text):
            presentations.append("accepts_vision")

        if any(phrase in patient_text for phrase in ["don't know", "not sure", "maybe"]):
            presentations.append("vague_response")

        return presentations if presentations else ["general_response"]

    def _assess_exchange_outcome(self, doctor_text: str, patient_text: str) -> str:
        """Assess what was achieved in this exchange"""

        if "yes" in patient_text and any(word in patient_text for word in ["want", "completely", "exactly"]):
            return "vision_accepted"

        if any(word in patient_text for word in ["peaceful", "calm"]) and "want" in patient_text:
            return "goal_stated"

        if any(word in patient_text for word in ["ache", "tight", "heavy"]):
            return "body_awareness_activated"

        if "right now" in doctor_text and patient_text:
            return "present_moment_awareness_established"

        return "information_gathered"

    def _create_embedding_tags(self, doctor_text: str, patient_text: str, trt_labels: Dict) -> List[str]:
        """Create tags for embedding and retrieval"""
        tags = []

        # Add stage/substate tags
        tags.extend([trt_labels["stage"], trt_labels["substate"]])

        # Add content-based tags
        if any(word in patient_text for word in ["peaceful", "calm"]):
            tags.extend(["peaceful_goal", "calm_goal"])

        if any(word in patient_text for word in ["work", "job"]):
            tags.extend(["work_stress", "job_pressure"])

        if any(word in patient_text for word in ["pain", "ache"]):
            tags.extend(["body_symptoms", "physical_pain"])

        if "right now" in doctor_text:
            tags.extend(["present_moment", "immediate_awareness"])

        if "how do you know" in doctor_text:
            tags.extend(["pattern_inquiry", "how_do_you_know_technique"])

        # Add Dr. Q style tags
        tags.extend(["dr_q_style", "trt_methodology"])

        return list(set(tags))  # Remove duplicates

    def _create_rag_contexts(self, trt_labels: Dict, situation_type: str, dr_q_technique: str) -> List[str]:
        """Create specific contexts for RAG retrieval"""
        contexts = []

        # Stage-specific contexts
        if trt_labels["substate"] == "1.1_goal_and_vision":
            contexts.extend([
                "client_states_goal_needs_vision",
                "initial_goal_clarification",
                "dr_q_goal_setting_approach"
            ])

        if trt_labels["substate"] == "1.2_problem_and_body":
            contexts.extend([
                "problem_construction_with_body_awareness",
                "dr_q_somatic_inquiry",
                "present_moment_body_focus"
            ])

        # Technique-specific contexts
        if dr_q_technique == "how_do_you_know_inquiry":
            contexts.append("dr_q_how_do_you_know_technique")

        if dr_q_technique == "present_moment_body":
            contexts.append("dr_q_present_moment_body_awareness")

        # Situation-specific contexts
        contexts.append(f"dr_q_{situation_type}")

        return contexts

    def process_session_file(self, txt_file_path: str, session_name: str) -> Dict:
        """Process complete session file"""
        exchanges = self.extract_exchanges_from_txt(txt_file_path)
        labeled_exchanges = []

        for i, exchange in enumerate(exchanges):
            exchange["exchange_id"] = f"{session_name}_{i+1:03d}"
            labeled_exchange = self.label_exchange(exchange)
            labeled_exchanges.append(labeled_exchange)

        return {
            "session_name": session_name,
            "total_exchanges": len(labeled_exchanges),
            "exchanges": labeled_exchanges
        }

    def create_embedding_dataset(self, session_data: Dict) -> List[Dict]:
        """Create dataset ready for embedding"""
        embedding_dataset = []

        for exchange in session_data["exchanges"]:
            # Create multiple embedding entries for different retrieval strategies

            # Main content embedding
            embedding_dataset.append({
                "id": f"{exchange['exchange_id']}_content",
                "content": f"Doctor: {exchange['doctor_input']}\nPatient: {exchange['patient_response']}",
                "metadata": {
                    "exchange_id": exchange["exchange_id"],
                    "session": session_data["session_name"],
                    "type": "therapeutic_exchange",
                    **exchange["therapeutic_labels"]
                },
                "tags": exchange["embedding_tags"],
                "retrieval_contexts": exchange["rag_retrieval_contexts"]
            })

            # Dr. Q technique embedding (for technique-specific retrieval)
            if exchange["therapeutic_labels"]["dr_q_technique"] != "general_inquiry":
                embedding_dataset.append({
                    "id": f"{exchange['exchange_id']}_technique",
                    "content": exchange['doctor_input'],
                    "metadata": {
                        "exchange_id": exchange["exchange_id"],
                        "session": session_data["session_name"],
                        "type": "dr_q_technique",
                        "technique": exchange["therapeutic_labels"]["dr_q_technique"],
                        "situation": exchange["therapeutic_labels"]["situation_type"]
                    },
                    "tags": [exchange["therapeutic_labels"]["dr_q_technique"]] + exchange["embedding_tags"],
                    "retrieval_contexts": exchange["rag_retrieval_contexts"]
                })

        return embedding_dataset


def main():
    processor = TRTTranscriptProcessor()

    # Process each session with new paths
    sessions = [
        ("data/raw_transcripts/session_01.txt", "session_01"),
        ("data/raw_transcripts/session_02.txt", "session_02"),
        ("data/raw_transcripts/session_03.txt", "session_03")
    ]

    all_embedding_data = []

    for txt_file, session_name in sessions:
        print(f"Processing {session_name}...")

        # Process session
        session_data = processor.process_session_file(txt_file, session_name)

        # Create embedding dataset
        embedding_data = processor.create_embedding_dataset(session_data)
        all_embedding_data.extend(embedding_data)

        # Save labeled exchanges in organized structure
        with open(f"data/processed_exchanges/{session_name}_labeled_exchanges.json", 'w') as f:
            json.dump(session_data, f, indent=2)

        print(f"Created {len(session_data['exchanges'])} labeled exchanges")

    # Save complete embedding dataset
    with open("data/processed_exchanges/complete_embedding_dataset.json", 'w') as f:
        json.dump(all_embedding_data, f, indent=2)

    print(f"Total embedding entries: {len(all_embedding_data)}")
    print("Ready for embedding and RAG system!")

if __name__ == "__main__":
    main()