from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification
from rapidfuzz import process as rf_process
from rapidfuzz import fuzz
import pandas as pd
import spacy
import re
import os
import csv
from presidio_analyzer import AnalyzerEngine, EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts,NlpEngineProvider
from faker import Faker


class TransformerRecognizer(EntityRecognizer):

    def __init__(self,
        model_id_or_path,
        mapping_labels,
        aggregation_strategy="simple",
        supported_language="fi",
        ignore_labels=["O", "MISC"]):

        # inits transformers pipeline for given mode or path
        self.pipeline = pipeline("token-classification", model=model_id_or_path, aggregation_strategy=aggregation_strategy, ignore_labels=ignore_labels)
        # map labels to presidio labels
        self.label2presidio = mapping_labels
        # passes entities from model into parent class
        super().__init__(supported_entities=list(self.label2presidio.values()), supported_language=supported_language)

    def load(self) -> None:
        """No loading is required."""
        pass

    def analyze(self, text: str, entities = None, nlp_artifacts: NlpArtifacts = None):
        """
        Extracts entities using Transformers pipeline
        """
        results = []

        predicted_entities = self.pipeline(text)
        if len(predicted_entities) > 0:
            for e in predicted_entities:
                if(e['entity_group'] not in self.label2presidio):
                    continue
                converted_entity = self.label2presidio[e["entity_group"]]
                if converted_entity in entities or entities is None:
                    results.append(RecognizerResult(entity_type=converted_entity, start=e["start"], end=e["end"], score=e["score"]))
        return results


class TextEntityFinder:
    DEFAULT_ANONYM_ENTITIES = ["EMAIL_ADDRESS", "LOC", "LOCATION", "GPE", "NRP", "NORP", "PERSON", "PHONE_NUMBER", "URL", "ORG", "ORGANIZATION"]
    to_censor_ents = ["EMAIL_ADDRESS", "LOCATION", "PERSON", "PHONE_NUMBER", "ORGANIZATION"]
    kansallisarkisto_mapping = {'PERSON': 'PERSON', 'ORG': 'ORGANIZATION', 'NORP': 'NRP', 'LOC': 'LOCATION','GPE': 'LOCATION'}
    configuration = {"nlp_engine_name": "spacy", "models": [{"lang_code": "fi", "model_name": "fi_core_news_lg"}]}
    available_models = ["Kansallisarkisto/finbert-ner", "iguanodon-ai/bert-base-finnish-uncased-ner"]
    finnish_entity_mapping = {"EMAIL_ADDRESS":"SÄHKÖPOSTIOSOITE", "LOCATION":"SIJAINTI", "NRP":"HENK_KUVAUS",
                              "PERSON":"HENKILÖ", "PHONE_NUMBER":"PUHELINNUMERO", "URL":"URL", "ORGANIZATION":"YRITYS",}


    def __init__(self, memory, model_ind=0):
        self.memory = memory
        self.configuration = TextEntityFinder.configuration
        self.fin_model = TextEntityFinder.available_models[model_ind]
        if self.fin_model == "Kansallisarkisto/finbert-ner":
            self.mapping_labels = TextEntityFinder.kansallisarkisto_mapping
        else:
            self.mapping_labels = {"PER": "PERSON", 'LOC': 'LOCATION', 'ORG': "ORGANIZATION"}
        self.lang = 'fi'

        # method and model initialization
        self.spacy_nlp = spacy.load("fi_core_news_lg", disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"])  # disable other than ner for performance
        self.tokenizer = AutoTokenizer.from_pretrained(self.fin_model)
        self.ner_model = AutoModelForTokenClassification.from_pretrained(self.fin_model)
        self.trans_nlp = pipeline("token-classification", model=self.ner_model, tokenizer=self.tokenizer, aggregation_strategy="simple")
        self.trad_provider = NlpEngineProvider(nlp_configuration=self.configuration)
        self.trad_nlp_engine = self.trad_provider.create_engine()
        self.trad_analyzer = AnalyzerEngine(nlp_engine=self.trad_nlp_engine, supported_languages=[self.lang])
        self.comp_provider = NlpEngineProvider(nlp_configuration=self.configuration)
        self.comp_nlp_engine = self.comp_provider.create_engine()
        # Pass the created NLP engine and supported_languages to the AnalyzerEngine
        self.comp_analyzer = AnalyzerEngine(nlp_engine=self.comp_nlp_engine, supported_languages=self.lang)
        self.transformers_recognizer = TransformerRecognizer(self.fin_model, self.mapping_labels)
        self.comp_analyzer.registry.add_recognizer(self.transformers_recognizer)

        self.faker = Faker('fi_FI')
        # variables
        self.to_keep_list = []  # list of words to keep in text
        self.false_positive_words = []  # automatically removed false positives
        # Result variables
        self.found_words = self.memory.found_entities  # [{'UID': text+entity_type, 'word': text, 'entity_type': entity_type, 'ner_method': ner_method, 'score':score, 'replacement': replacement}]
        self.replacements = []  #
        self.entity_counters = {}  # To keep track of entity counts {type: int}

    def set_update_to_keep_list(self, to_keep_words, method='add'):
        if type(to_keep_words) != list:
            print("\nIncorrect type! To add words, pass them as list!")
            return
        if method == 'add':
            # Ensure only unique words are added
            unique_words = set(to_keep_words) - set(self.to_keep_list)
            self.to_keep_list.extend(unique_words)
            self.to_keep_list.sort()  # Sort the list after adding new words
        elif method == 'update':
            self.to_keep_list = sorted(list(set(to_keep_words)))
        else:
            print(Warning(ValueError("Unsupported method specified. Use 'add' or 'update'.")))
            return
        # Now, filter self.found_words to remove any items with words in the to_keep list
        self.found_words = [item for item in self.found_words if item['word'] not in self.to_keep_list]

    def remove_duplicate_entities(self):
        unique = {}
        for item in self.found_words:
            key = (item['word'], item['entity_type'])
            if key not in unique:
                unique[key] = item
        self.found_words = list(unique.values())

    def _get_fake_var(self, entity_type):
        """Generate fake data based on the entity type using the Finnish locale."""
        company_ends = ['Oyj', 'As Oy', 'Oy', 'ry', 'Ky', 'Osk', 'Tmi']
        if entity_type == "EMAIL_ADDRESS":
            return self.faker.email().lower()
        elif entity_type == "LOCATION":
            return self.faker.city().lower()
        elif entity_type == "PERSON":
            return self.faker.name().lower()
        elif entity_type == "PHONE_NUMBER":
            return self.faker.phone_number().lower()
        elif entity_type == "URL":
            return self.faker.url().lower()
        elif entity_type == "ORGANIZATION":
            comp = self.faker.company()
            try:
                ending = comp.split(" ")[-1]
                if ending in company_ends:
                    return comp
                else:
                    return f"{comp} {self.faker.company_suffix()}".lower()
            except Exception:
                return f"{comp} {self.faker.company_suffix()}".lower()
        else:
            return "Unknown_type"

    def generate_fake_data(self, entity_type, org):
        """Generate fake data based on the entity type using the Finnish locale."""
        new = self._get_fake_var(entity_type)
        ind = 0
        while new == org:
            if ind > 50:
                return "^pseudonymized_var"
            ind += 1
            new = self._get_fake_var(entity_type)
        return "^" + new.lower()

    def create_replacement(self, one):
        curr_type = one['entity_type']
        if curr_type in self.DEFAULT_ANONYM_ENTITIES:
            fake_data = self.generate_fake_data(curr_type, one.get('word', None))
            while fake_data in self.replacements:
                fake_data = self.generate_fake_data(curr_type, one.get('word', None))
            self.replacements.append(fake_data)
            return fake_data
        else:
            print(Warning(f"WARNING! Unknown entity type {curr_type} in {one}!"))
            return "Unknown_type"

    def legacy_create_replacement(self, one):
        curr_type = one['entity_type']
        if curr_type in TextEntityFinder.DEFAULT_ANONYM_ENTITIES:
            if curr_type in self.entity_counters:
                ind = 1
                rep_try = f"{TextEntityFinder.finnish_entity_mapping[curr_type]}_{self.entity_counters[curr_type] + ind}".lower()
                while rep_try in self.replacements:
                    rep_try = f"{TextEntityFinder.finnish_entity_mapping[curr_type]}_{self.entity_counters[curr_type] + ind}".lower()
                    ind += 1
                self.entity_counters[curr_type] += 1
                self.replacements.append(rep_try)
                return rep_try
            else:
                self.entity_counters[curr_type] = 1
                rep = f"{TextEntityFinder.finnish_entity_mapping[curr_type]}_{self.entity_counters[curr_type]}".lower()
                self.replacements.append(rep)
                return rep
        else:
            print(Warning(f"WARNING! Unknown entity type {curr_type} in {one}!"))
            return "Unknown_type"


    def find_entities(self, text, faker_replacements=True, safe_approach=True, better_accu_more_fp=True, confidence_score:int=0.5):
        comb_words = []
        # Combined method -analyzer
        temp_analyzer_results = self.comp_analyzer.analyze(text=text, entities=TextEntityFinder.DEFAULT_ANONYM_ENTITIES, allow_list=self.to_keep_list, language=self.lang)
        # Restructuring anonymizer results
        for obj in [entity.to_dict() for entity in temp_analyzer_results]:
            entity = self.mapping_labels[obj['entity_type']] if obj['entity_type'] in self.mapping_labels else obj['entity_type']
            one_word = text[obj['start']:obj['end']].strip()
            comb_words.append({'UID': one_word + entity, 'word': one_word,'entity_type': entity,
                               "ner_method": 'comp_method', 'score': obj['score']})

        if better_accu_more_fp:
            comb_words.extend(self.presidio_ner_method(text, only_allowed=['EMAIL_ADDRESS', 'PHONE_NUMBER']))
            # comb_words.extend(self.spacy_ner_method(text))
            # comb_words.extend(self.trans_based_ner_method(text))

        comb_words.sort(key=lambda x: len(x['word']), reverse=True)
        for one in comb_words:
            if one['entity_type'] in TextEntityFinder.to_censor_ents and one['word'] not in self.to_keep_list:
                if one['score'] is None or one['score'] > confidence_score:  # Set confidence score to filter false-positives
                    if len(one['word']) > 3:  # To rule out short words
                        if one['UID'] not in [sec['UID'] for sec in self.found_words]:
                            one['replacement'] = self.create_replacement(one) if faker_replacements else self.legacy_create_replacement(one)
                            self.found_words.append(one)
        if safe_approach:
            self.export_raw_words_to_csv("safe_approach_file.csv")
        return comb_words

    def spacy_pattern_method(self, text):
        pass  # for future

    def spacy_ner_method(self, text):
        doc = self.spacy_nlp(text)
        words = []
        for ent in doc.ents:
            to_use_label = self.mapping_labels[ent.label_] if ent.label_ in self.mapping_labels else ent.label_
            words.append({'UID': ent.text.strip() + to_use_label, 'word': ent.text.strip(), 'entity_type': to_use_label,
                          "ner_method": 'spacy', 'score': None})
        return words

    def presidio_ner_method(self, text, only_allowed:list=None):
        result = self.trad_analyzer.analyze(text=text, language='fi')
        words = []

        for obj in [entity.to_dict() for entity in result]:
            if only_allowed:
                if obj['entity_type'] in only_allowed:
                    entity = self.mapping_labels[obj['entity_type']] if obj['entity_type'] in self.mapping_labels else obj['entity_type']
                    one_word = text[obj['start']:obj['end']].strip()
                    words.append({'UID': one_word + entity, 'word': one_word,'entity_type': entity,
                                  "ner_method": 'presidio', 'score': obj['score']})
            else:
                entity = self.mapping_labels[obj['entity_type']] if obj['entity_type'] in self.mapping_labels else obj['entity_type']
                one_word = text[obj['start']:obj['end']].strip()
                words.append({'UID': one_word + entity, 'word': one_word, 'entity_type': entity,
                              "ner_method": 'presidio', 'score': obj['score']})

        return words

    def trans_based_ner_method(self, text):  # makes no difference, thus no worth using with comp-method
        """NER Transformers PIPELINE"""
        transformer_res = self.trans_nlp(text)
        words = []
        for obj in transformer_res:
            entity = self.mapping_labels[obj['entity_group']] if obj['entity_group'] in self.mapping_labels else obj['entity_group']
            one_word = text[obj['start']:obj['end']].strip()
            words.append({'UID': one_word + entity, 'word': one_word,'entity_type': entity,
                          "ner_method": 'transformer', 'score': obj['score']})
        return words

    @staticmethod
    def normalize_word(word):
        """Normalize a word by removing special characters and handling split words."""
        normalized = re.sub(r'[\-\s]+', '', word)  # Remove hyphens and spaces
        return normalized.lower()  # Convert to lowercase to standardize

    def try_to_map_similar_entities(self, entities, similarity_threshold=75):
        """
        Find and update entities with similar words based on fuzzy matching,
        including similarity scores.

        Parameters:
        entities (list of dicts): The list of entities to process.
        similarity_threshold (float): The threshold for considering words as similar (default 95).

        Returns:
        list of dicts: Updated list of entities with similar entities having the same replacement
                       and including similarity score and similarity score with.
        """
        # Normalize words for all entities
        for index, entity in enumerate(entities):
            entity['normalized_word'] = self.normalize_word(entity['word'])
            if (index + 1) % 100 == 0:
                print(f"{index + 1} entities checked")

        # Map each unique normalized word to the best replacement found, including similarity score
        word_to_info = {}
        for index, entity in enumerate(entities):
            word = entity['normalized_word']
            # Use process.extract to find matches above the similarity threshold
            matches = rf_process.extract(word, [e['normalized_word'] for e in entities if e['normalized_word'] != word],
                                      scorer=fuzz.WRatio, score_cutoff=similarity_threshold, limit=1)

            if matches:
                best_match = matches[0]
                matched_word = best_match[0]
                similarity_score = best_match[1]
                word_to_info[word] = {'replacement': entity['replacement'],
                                      'similarity_score': similarity_score,
                                      'similarity_score_with': matched_word}

            if (index + 1) % 100 == 0:
                print(f"{index + 1} unique words processed")

        # Update entities with the best replacement and similarity info for similar words
        for entity in entities:
            normalized_word = entity['normalized_word']
            if normalized_word in word_to_info:
                entity['replacement'] = word_to_info[normalized_word]['replacement']
                entity['similarity_score'] = word_to_info[normalized_word]['similarity_score']
                entity['similarity_score_with'] = word_to_info[normalized_word]['similarity_score_with']
            else:
                # Ensure all entities have these fields for consistency
                entity['similarity_score'] = None
                entity['similarity_score_with'] = None
            # del entity['normalized_word'] # don't delete while testing

        print("Similarity matching process finished")
        return entities


    def export_entities_to_csv(self, filename='entities.csv', test_ents=None):
        if not filename.endswith(".csv"):
            filename = filename + '.csv'
        if test_ents:
            ents = test_ents
        else:
            ents = self.found_words
        try:
            fieldnames = ['word', 'entity_type', 'replacement']  # Define the fieldnames you want in the CSV
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for word_info in ents:
                    # Filter out keys not in fieldnames
                    filtered_word_info = {k: v for k, v in word_info.items() if k in fieldnames}
                    writer.writerow(filtered_word_info)
            print(f"Entities exported to {filename}. Please modify this file and then import it back.")
        except Exception as e:
            print(Warning("Entities couldn't be exported due to this error: ", e))

    def export_raw_words_to_csv(self, filename='raw_entities.csv', test_ents=None):
        if not filename.endswith(".csv"):
            filename = filename + '.csv'
        if test_ents:
            ents = test_ents
        else:
            ents = self.found_words
        if 'safe' not in filename and len(ents) == 0:
            print("No entities to print.")
            return
        try:
            df = pd.DataFrame(self.found_words)
            df.to_csv(filename, sep=',', index=False, encoding='utf-8')
            if 'safe' not in filename:
                print(f"Entities exported to {filename}. Please modify this file and then import it back.")
        except Exception as e:
            print(Warning("Entities couldn't be exported due to this error: ", e))

    def import_entities_from_csv(self, filename='entities.csv', replace=False):  # TODO try-except logic and option to extend/replace
        if not os.path.exists(filename):
            print(f"No such file: {filename}")
            return False
        try:
            if replace:
                self.memory.found_entities = []
                self.found_words = self.memory.found_entities
            with open(filename, newline='', encoding='utf-8') as file:
                dict_reader = csv.DictReader(file)
                for row in dict_reader:
                    # Check if UID is not found in any of the dictionaries within self.found_words
                    try:
                        if not any(sec.get('UID') == row['UID'] for sec in self.found_words):
                            # Update entity_counters
                            entity_type = row['entity_type']
                            if entity_type in self.entity_counters:
                                self.entity_counters[entity_type] += 1
                            else:
                                self.entity_counters[entity_type] = 1
                            self.replacements.append(row['replacement'])
                            self.found_words.append(row)  # Append the whole dictionary
                    except KeyError:
                        if not any(sec.get('UID') == row['UID'] for sec in self.found_words):
                            # Update entity_counters
                            entity_type = row['entity_type']
                            if entity_type in self.entity_counters:
                                self.entity_counters[entity_type] += 1
                            else:
                                self.entity_counters[entity_type] = 1
                            self.replacements.append(row['replacement'])
                            self.found_words.append(row)  # Append the whole dictionary
            print("\nEntities imported successfully.")
            return True
        except Exception as e:
            print(f"\nEntities couldn't be imported due to this error: {e}")


    def display_found_entities(self):
        print("\nFound entities are:")
        if len(self.found_words) == 0:
            print("No entities listed yet. Please find entities or import them first.")
        else:
            for i, word_info in enumerate(self.found_words, start=1):
                print(f"{i}. {word_info['word']} ({word_info['entity_type']}) - Replacement: {word_info.get('replacement', 'N/A')} (Method: {word_info.get('ner_method', 'N/A')})")

    def anonymize_text(self, text):
        anonymizated_text = text
        key_dict = {}  # {actual:replacement}

        for one in self.found_words:
            subs, repl = one['word'], one['replacement']
            # Check if the word is already processed
            if subs in key_dict:
                continue
            # Perform a case-sensitive replacement without compiling a regex for each word
            anonymizated_text = anonymizated_text.replace(subs, repl)
            key_dict[subs] = repl
        return anonymizated_text, key_dict

