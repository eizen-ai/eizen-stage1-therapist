"""
Process All Raw Transcripts into Labeled Exchanges for RAG
Automatically identifies Dr. Q (DOCTOR) vs Patient and creates embeddings
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple


class TranscriptProcessor:
    """Process raw transcripts into labeled exchanges"""

    def __init__(self):
        self.exchanges = []
        self.stats = {
            "total_files": 0,
            "total_exchanges": 0,
            "files_processed": [],
            "files_failed": []
        }

    def process_all_transcripts(self, transcript_dirs: List[str]) -> List[Dict]:
        """Process all transcripts from multiple directories"""

        all_transcript_files = []

        # Collect all transcript files
        for directory in transcript_dirs:
            if os.path.exists(directory):
                for file in Path(directory).glob("*.txt"):
                    all_transcript_files.append(str(file))

        print(f"Found {len(all_transcript_files)} transcript files")
        self.stats["total_files"] = len(all_transcript_files)

        # Process each file
        for file_path in all_transcript_files:
            print(f"\nProcessing: {os.path.basename(file_path)}")
            try:
                exchanges = self.process_single_transcript(file_path)
                self.exchanges.extend(exchanges)
                self.stats["files_processed"].append(os.path.basename(file_path))
                print(f"  ✅ Extracted {len(exchanges)} exchanges")
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.stats["files_failed"].append(os.path.basename(file_path))

        self.stats["total_exchanges"] = len(self.exchanges)
        return self.exchanges

    def process_single_transcript(self, file_path: str) -> List[Dict]:
        """Process a single transcript file"""

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse into lines
        lines = content.split('\n')

        exchanges = []
        current_doctor_lines = []
        current_patient_lines = []

        last_speaker = None
        exchange_id = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect speaker
            if line.startswith('[DOCTOR]') or line.startswith('[THERAPIST]'):
                # If we have accumulated patient lines, save the exchange
                if current_doctor_lines and current_patient_lines:
                    exchange = self._create_exchange(
                        current_doctor_lines,
                        current_patient_lines,
                        file_path,
                        exchange_id
                    )
                    if exchange:
                        exchanges.append(exchange)
                        exchange_id += 1

                    # Reset patient lines for next exchange
                    current_patient_lines = []

                # Extract doctor's text
                doctor_text = re.sub(r'^\[(DOCTOR|THERAPIST)\]:\s*', '', line).strip()
                if doctor_text:
                    current_doctor_lines.append(doctor_text)
                last_speaker = 'doctor'

            elif line.startswith('[PATIENT]') or line.startswith('[CLIENT]'):
                # Extract patient's text
                patient_text = re.sub(r'^\[(PATIENT|CLIENT)\]:\s*', '', line).strip()
                if patient_text:
                    current_patient_lines.append(patient_text)
                last_speaker = 'patient'

            else:
                # Continuation of previous speaker
                if last_speaker == 'doctor' and line:
                    current_doctor_lines.append(line)
                elif last_speaker == 'patient' and line:
                    current_patient_lines.append(line)

        # Don't forget the last exchange
        if current_doctor_lines and current_patient_lines:
            exchange = self._create_exchange(
                current_doctor_lines,
                current_patient_lines,
                file_path,
                exchange_id
            )
            if exchange:
                exchanges.append(exchange)

        return exchanges

    def _create_exchange(self, doctor_lines: List[str], patient_lines: List[str],
                        file_path: str, exchange_id: int) -> Dict:
        """Create a labeled exchange from doctor and patient lines"""

        # Join lines into single strings
        doctor_input = ' '.join(doctor_lines).strip()
        patient_response = ' '.join(patient_lines).strip()

        if not doctor_input or not patient_response:
            return None

        # Auto-detect therapeutic context
        labels = self._auto_label_exchange(doctor_input, patient_response)

        # Generate embedding tags
        tags = self._generate_tags(doctor_input, patient_response, labels)

        # Generate RAG retrieval contexts
        rag_contexts = self._generate_rag_contexts(doctor_input, patient_response, labels)

        exchange = {
            "exchange_id": f"{Path(file_path).stem}_{exchange_id:03d}",
            "source_file": os.path.basename(file_path),
            "doctor_input": doctor_input,
            "patient_response": patient_response,
            "therapeutic_labels": labels,
            "embedding_tags": tags,
            "rag_retrieval_contexts": rag_contexts
        }

        return exchange

    def _auto_label_exchange(self, doctor_input: str, patient_response: str) -> Dict:
        """Automatically label the exchange based on content"""

        doctor_lower = doctor_input.lower()
        patient_lower = patient_response.lower()

        # Detect TRT stage
        stage = "stage_1_safety_building"  # Default

        # Detect substate
        substate = "unknown"

        if any(phrase in doctor_lower for phrase in ["what do we want", "what do you want", "focus on today", "get better"]):
            substate = "1.1_goal_and_vision"
            situation = "initial_goal_inquiry"
            technique = "goal_clarification"

        elif any(phrase in doctor_lower for phrase in ["peaceful", "calm", "lighter", "at ease", "grounded", "does that make sense"]):
            if "?" in doctor_input:
                substate = "1.1_goal_and_vision"
                situation = "future_self_vision_building"
                technique = "vision_acceptance_check"
            else:
                substate = "1.1_goal_and_vision"
                situation = "future_self_vision_building"
                technique = "detailed_outcome_state_description"

        elif any(phrase in doctor_lower for phrase in ["where", "what kind of", "sensation", "ache", "tight", "sharp"]):
            substate = "1.2_problem_and_body"
            situation = "body_symptom_present_inquiry"
            technique = "specific_somatic_questioning"

        elif any(phrase in doctor_lower for phrase in ["how do you know", "what's happening in that moment"]):
            substate = "1.2_problem_and_body"
            situation = "emotional_pattern_inquiry"
            technique = "how_do_you_know_questioning"

        elif any(phrase in doctor_lower for phrase in ["you're feeling", "even you just talking", "right now"]):
            substate = "1.2_problem_and_body"
            situation = "present_moment_body_awareness"
            technique = "present_moment_somatic_observation"

        else:
            substate = "general_therapeutic_exchange"
            situation = "general_therapeutic_inquiry"
            technique = "general_dr_q_approach"

        # Detect client presentation
        if "i don't know" in patient_lower:
            presentation = "client_uncertain_or_confused"
        elif any(word in patient_lower for word in ["yes", "exactly", "completely", "that's right"]):
            presentation = "client_agreement_or_acceptance"
        elif any(word in patient_lower for word in ["chest", "head", "leg", "stomach", "body"]):
            presentation = "body_awareness_present"
        elif any(word in patient_lower for word in ["peaceful", "calm", "better", "want to feel"]):
            presentation = "goal_statement"
        else:
            presentation = "general_response"

        return {
            "trt_stage": stage,
            "trt_substate": substate,
            "situation_type": situation,
            "dr_q_technique": technique,
            "client_presentation": presentation
        }

    def _generate_tags(self, doctor_input: str, patient_response: str, labels: Dict) -> List[str]:
        """Generate embedding tags for RAG retrieval"""

        tags = []

        # Add technique tags
        tags.append(labels["dr_q_technique"])
        tags.append(labels["situation_type"])

        # Add keyword tags from doctor input
        doctor_lower = doctor_input.lower()
        if "goal" in doctor_lower or "want" in doctor_lower:
            tags.append("goal_setting")
        if "peaceful" in doctor_lower or "calm" in doctor_lower:
            tags.append("peaceful_goal")
        if "body" in doctor_lower or "where" in doctor_lower:
            tags.append("body_inquiry")
        if "sensation" in doctor_lower or "ache" in doctor_lower:
            tags.append("somatic_inquiry")
        if "how do you know" in doctor_lower:
            tags.append("how_do_you_know")
        if "right now" in doctor_lower or "feeling that" in doctor_lower:
            tags.append("present_moment")

        # Add keyword tags from patient response
        patient_lower = patient_response.lower()
        if "i don't know" in patient_lower:
            tags.append("i_dont_know_response")
        if any(word in patient_lower for word in ["yes", "exactly", "completely"]):
            tags.append("affirmative_response")
        if any(word in patient_lower for word in ["chest", "head", "leg", "body"]):
            tags.append("body_location_mentioned")

        return tags

    def _generate_rag_contexts(self, doctor_input: str, patient_response: str, labels: Dict) -> List[str]:
        """Generate RAG retrieval contexts"""

        contexts = []

        # Add technique-based contexts
        contexts.append(f"dr_q_{labels['dr_q_technique']}")
        contexts.append(labels['situation_type'])

        # Add specific retrieval contexts
        doctor_lower = doctor_input.lower()
        patient_lower = patient_response.lower()

        if "what do we want" in doctor_lower:
            contexts.append("dr_q_triple_goal_question")
        if "i don't know" in patient_lower:
            contexts.append("client_says_i_dont_know")
        if "where" in doctor_lower and ("body" in doctor_lower or any(w in doctor_lower for w in ["chest", "head", "leg"])):
            contexts.append("dr_q_body_location_inquiry")
        if "how do you know" in doctor_lower:
            contexts.append("dr_q_how_do_you_know_technique")

        return contexts

    def save_exchanges(self, output_file: str):
        """Save all exchanges to JSON file"""

        output_data = {
            "metadata": {
                "total_exchanges": len(self.exchanges),
                "source_files": self.stats["files_processed"],
                "processing_stats": self.stats
            },
            "exchanges": self.exchanges
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved {len(self.exchanges)} exchanges to {output_file}")

    def print_stats(self):
        """Print processing statistics"""

        print("\n" + "=" * 80)
        print("TRANSCRIPT PROCESSING STATISTICS")
        print("=" * 80)
        print(f"Total files found: {self.stats['total_files']}")
        print(f"Files processed successfully: {len(self.stats['files_processed'])}")
        print(f"Files failed: {len(self.stats['files_failed'])}")
        print(f"Total exchanges extracted: {self.stats['total_exchanges']}")

        if self.stats['files_failed']:
            print(f"\n⚠️ Failed files:")
            for file in self.stats['files_failed']:
                print(f"  - {file}")

        print("\n✅ Processing complete!")


def main():
    """Main processing function"""

    print("=" * 80)
    print("PROCESSING ALL DR. Q TRANSCRIPTS")
    print("=" * 80)

    # Define directories to search
    transcript_dirs = [
        "data/raw_transcripts",
        "data/Session Transcripts",
        "data/transcripts"  # In case you add more here
    ]

    # Initialize processor
    processor = TranscriptProcessor()

    # Process all transcripts
    processor.process_all_transcripts(transcript_dirs)

    # Save to file
    output_file = "data/processed_exchanges/all_dr_q_exchanges.json"
    os.makedirs("data/processed_exchanges", exist_ok=True)
    processor.save_exchanges(output_file)

    # Print statistics
    processor.print_stats()

    print(f"\n📁 Output saved to: {output_file}")
    print("\nNext step: Run embedding_and_retrieval_setup.py to rebuild RAG with new exchanges")


if __name__ == "__main__":
    main()
