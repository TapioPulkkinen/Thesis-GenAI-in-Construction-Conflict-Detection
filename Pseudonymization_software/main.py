import os
import csv
import json
import warnings

from memory import RunTimeMemory
from pdf_anonymizer import PDFAnonymizer
from readers import FileReader, DirReader
from entity_recognizer import TextEntityFinder


class SimpleFileWriter:

    @staticmethod
    def save_files(files_dict, folder_path):
        if folder_path.startswith('"') or folder_path.endswith('"'):
            folder_path = folder_path.strip('"')
        if not os.path.isdir(folder_path):
            print("Incorrect folder path! Saving wasn't completed!")
            return False
        try:  # TODO: check file type and if pdf write proper pdf
            replacements = {
                'Ã„': 'Ä',  # Example of a common misencoding for Ä
                'Ã–': 'Ö',  # Example of a common misencoding for Ö
                'Ã¤': 'ä',  # Example of a common misencoding for ä
                'Ã¶': 'ö',  # Example of a common misencoding for ö
                'Ã…': 'Å',  # Example of a common misencoding for Å
                'Ã¥': 'å',  # Example of a common misencoding for Å
            }
            for file_name, file_content in files_dict.items():
                # Add prefix to the file name
                anonymized_file_name = f"auto_anom_{file_name}"
                full_file_path = os.path.join(folder_path, anonymized_file_name)
                path_root, _ = os.path.splitext(full_file_path)
                full_file_path = path_root + '.txt'
                for incorrect, correct in replacements.items():
                    file_content = file_content.replace(incorrect, correct)
                with open(full_file_path, 'w', encoding='utf-8') as file:
                    file.write(file_content)
            return True
        except Exception as e:
            print(f"Saving files resulted following error and wasn't completed: {e}")
            return False

    @staticmethod
    def save_keys_to_csv(keys_dict, csv_file):
        # Specify the CSV file name
        if not csv_file.endswith(".csv"):
            csv_file = csv_file + '.csv'
        try:
            # Determine the headers from the first item, assuming all items have the same structure
            headers = ['file_name', 'original_value', 'replaced_value']
            with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                for file_name, replacements in keys_dict.items():
                    for original_value, replaced_value in replacements.items():
                        writer.writerow([file_name, original_value, replaced_value])

            print(f"CSV file '{csv_file}' has been created successfully.")
            return True
        except Exception as e:
            print(f"Saving keys resulted following error and wasn't completed: {e}")
            return False



class PseudoProcess:

    def __init__(self, max_depth_for_dir=11, find_ents=True, pseudonym_ents=True):
        self.memory = RunTimeMemory()
        self.file_reader = FileReader(memory=self.memory)
        self.entity_finder = TextEntityFinder(memory=self.memory)
        self.pdf_anonymizer = PDFAnonymizer(memory=self.memory)
        self.max_depth = max_depth_for_dir
        self.find_entities = find_ents
        self.pseudonymize_entities = pseudonym_ents


    def reset_memory(self):
        self.memory.clear_memory()

    def _construct_temp_text_chunks(self, path):
        one_data = self.memory.file_data[path]
        #text_chunks = ["".join(item['text'] for content in page['content'] for item in [content] if item['type'] == 'text') for page in one_data]
        text_chunks = []
        text = "\n".join([item['text'].strip() for page in one_data for item in page['content'] if item['type'] == 'text'])
        text_chunks = [row for row in text.split("\n\n") if len(row) > 1]
        return text_chunks

    def find_entities_in_memory(self, text_chunks):
        if not text_chunks:
            raise Exception("Error: No data available for finding entities.")
        for chunk in text_chunks:
            self.entity_finder.find_entities(text=chunk)

    def finding_process(self, read_from_path, read_only=False):
        if read_from_path.startswith('"') or read_from_path.endswith('"'):
            read_from_path = read_from_path.strip('"')
        try:
            if self.is_path_single_file(read_from_path):
                files_list = [read_from_path]
            else:
                files_list = DirReader().get_all_files_from_dir(path=read_from_path, max_depth=self.max_depth)
            self.memory.file_paths = files_list
            for ind, path in enumerate(self.memory.file_paths):
                try:
                    if not self.file_reader.process_file(path):
                        print(f"file in {path} needs ocr handling")
                        continue
                    if not read_only:
                        text_chunks = self._construct_temp_text_chunks(path=path)
                        self.find_entities_in_memory(text_chunks)
                except Exception as err:
                    warnings.warn(str(err))
                    self.memory.log_file_errors[path] = str(err)
                finally:
                    print(f"{ind+1}. file handled from total of {len(self.memory.file_paths)} files.")
        except Exception as err:
            raise Exception(f"PseudoProcess - finding entities error: {err}")

    def is_path_single_file(self, read_from_path):
        if os.path.isfile(read_from_path):
            return True
        elif os.path.isdir(read_from_path):
            return False
        else:
            raise NotADirectoryError("PseudoProcess: Path is not a file or a directory!")

    def check_file_type(self, path):
        if not isinstance(path, str):
            raise ValueError("Check_file_type: Path must be string!")
        if not os.path.isfile(path):
            return "Unknown"
        else:
            return os.path.splitext(path)[1]

    def pseudonym_process(self, save_path):
        print(f"{len(self.memory.file_data)} < 1 or {len(self.memory.found_entities)} < 1:")
        if len(self.memory.file_data) < 1 or len(self.memory.found_entities) < 1:
            raise ValueError("No data for pseudonymize text.")
        self.pdf_anonymizer.set_save_path(save_path)

        try:
            self.pdf_anonymizer.replace_words()
        except Exception as err:
            raise Exception(f"PseudoProcess - finding entities error: {err}")

    def ready_to_read_and_pseudo(self):
        if len(self.memory.found_entities) < 1:
            return False
        return True


def display_menu():
    print("\n-----Main menu:-----") # todo improve instructions
    print("0. Initialize system (reset memory)")
    print("1. Read files and/or find entities")
    print("2. Pseudonymize files")
    print("3. Review, export, and import entities")
    print("4. Read and pseudonymize files")
    #print("5. See, add, update to_keep-/false_pos-list")
    #print("6. Anonymize texts")
    #print("7. Visualize anonymized files")
    #print("8. Save anonymized files")
    #print("9. Visualize keys")
    #print("10. Save keys")
    #rint("11. **Test similarity matching.**")
    #rint("12. **Export raw data entities**")
    #print("13. Anonymize and save PDF files to original format")
    print("99. Stop the process")
    choice = input("Select an option: ").strip()
    print()
    return choice

def main():
    print("WELCOME!")
    print("Let's start testing!")
    first_time = True
    process = ""
    while True:
        choice = display_menu()

        # TODO: choose whatever to prioritize speed or accuracy

        if choice == "0":
            if first_time:
                print("Initializing...\n")
                process = PseudoProcess()
                first_time = False
            else:
                process.reset_memory()


        elif choice == "1":
            if first_time:
                print("Initializing...\n")
                process = PseudoProcess()
                first_time = False
            read_only = False
            if input("Do you want to read files only? y if yes, anything else if no. Ans: ").lower() == "y":
                read_only = True
            file_path = input("Enter the file or folder path: ")
            process.finding_process(file_path, read_only=read_only)
            print("Process ready")

        elif choice == "2":
            if first_time:
                print("Action not allowed. Please either initialize process or read data files")
                continue
            print("Paste/type here path to folder where you want to save anonymized files.\n Type 'done' to return without saving.")
            folder_path = input("Path: ")
            if folder_path.startswith('"') or folder_path.endswith('"'):
                folder_path = folder_path.strip('"')
            while folder_path != 'done' and not os.path.isdir(folder_path):
                print("Incorrect path. Try again")
                folder_path = input("Paste/type path: ")
                if folder_path.startswith('"') or folder_path.endswith('"'):
                    folder_path = folder_path.strip('"')
            if folder_path == 'done':
                print("Returning without saving.")
                continue
            process.pseudonym_process(save_path=folder_path)

        elif choice == "3":
            action_prompt = """
                        \nPlease choose an action for entities:
                        1. Export entities to CSV for you to modify them
                        2. Import entities from CSV to use corrected ones 
                        3. Done
                        Your choice: """

            while True:
                choice = input(action_prompt).strip()
                if choice == '1':
                    if not process.memory.found_entities or len(process.memory.found_entities) == 0:
                        print("No entities found. Please find entities first.")
                        continue
                    filename = input("Enter filename for export (default: entities.csv): ").strip() or 'entities.csv'
                    process.entity_finder.export_raw_words_to_csv(filename)
                elif choice == '2':
                    print("NOTE! File must be a .csv file that you have exported previously or a similar file")
                    filename = input("Enter filepath to import from (default: entities.csv): ").strip() or 'entities.csv'
                    if process.entity_finder.import_entities_from_csv(filename):
                        # Optionally validate the imported entities here
                        pass
                elif choice == '3':
                    break
                else:
                    print("Invalid choice. Please try again.")
            print(f"\nEntities exported/imported.")

        elif choice == '4':
            if first_time:
                print("Action not allowed. Please either initialize process or read data files")
                continue
            if not process.ready_to_read_and_pseudo():
                print("No entities in memory. Add them first or use other method.")
                continue
            read_path = input("Enter the file or folder path for reading: ")
            if read_path.startswith('"') or read_path.endswith('"'):
                read_path = read_path.strip('"')
            print("Paste/type here path to folder where you want to save anonymized files.\n Type 'done' to return without saving.")
            folder_path = input("Path: ")
            if folder_path.startswith('"') or folder_path.endswith('"'):
                folder_path = folder_path.strip('"')
            while folder_path != 'done' and not os.path.isdir(folder_path):
                print("Incorrect path. Try again")
                folder_path = input("Paste/type path: ")
                if folder_path.startswith('"') or folder_path.endswith('"'):
                    folder_path = folder_path.strip('"')
            if folder_path == 'done':
                print("Returning without saving.")
                continue
            process.finding_process(read_path, read_only=True)
            process.pseudonym_process(save_path=folder_path)
            print("Process ready")

        elif choice == '99':
            # Stop the process
            print("Process stopped.")
            break
        else:
            print("Invalid option. Please select a valid number from menu options.")






def legacy_main():
    file_reader = FileReader(chunking=True, chunk_max_length=1000, chunk_endings=['\n', ' '])
    anom_service = TextEntityFinder()
    text_dict = {}
    anom_text = {}
    anom_keys = {}

    print("Welcome!\nFirst import your old entities to keep replacements up-to-date.\nThe file should be in .csv format "
          "and structured similarly than the files you can export from here. \nIf you don't import entities before you "
          "find new ones, the replacements might overlap. \nType 1 to import old entities.\nType 2 if understood that "
          "old entities must be imported before finding new ones.")
    while True:
        ack = input("1 or 2: ").strip()
        if ack == '1':
            print("NOTE! File must be a .csv file that you have exported previously or a similar file")
            filename = input("Enter filepath to import from: ").strip() or 'entities.csv'
            anom_service.import_entities_from_csv(filename)
            break
        elif ack == '2':
            break
        else:
            print("Invalid choice. Please try again.")
    print("\nIf you have list of false-positive entities or want to keep some entities, use option 5 first!")

    while True:
        choice = display_menu()

        if choice == '1':
            # Read files
            file_path = input("Enter the file or folder path: ")
            chunking = input("Enable chunking? Yes is recommended. (yes/no): ").lower() == 'yes' or ''
            file_reader.set_chunking_enabled(chunking)
            text_dict = file_reader.read_file_or_folder(file_path)
            print(f"\nNumber of files read: {len(text_dict)}")
            print(f"These files needs OCR reading: {RunTimeMemory.needs_ocr}")

        elif choice == '2':
            # Find entities from files
            if not text_dict:
                print("No files have been read yet. Please read files first.")
                continue
            print("\nStarting to find the entities...")
            for ind, name in enumerate(text_dict, start=1):  # TODO: performance update -> use multi CPU for chunks or files https://superfastpython.com/python-use-all-cpu-cores/
                if isinstance(text_dict[name], list):
                    for piece in text_dict[name]:
                        anom_service.find_entities(piece)
                else:
                   anom_service.find_entities(text_dict[name])
                print(f"Processed {ind} files from total of {len(text_dict)}.")
            print(f"Found {len(anom_service.found_words)} entities from files.")

        elif choice == '3':
            # Review and correct entities
            anom_service.display_found_entities()
            action_prompt = """
            \nPlease choose an action for entities:
            1. Export entities to CSV for you to modify them
            2. Import entities from CSV to use corrected ones 
            3. Done
            Your choice: """

            while True:
                choice = input(action_prompt).strip()
                if choice == '1':
                    if not anom_service.found_words or len(anom_service.found_words) == 0:
                        print("No entities found. Please find entities first.")
                        continue
                    filename = input("Enter filename for export (default: entities.csv): ").strip() or 'entities.csv'
                    anom_service.export_raw_words_to_csv(filename)
                elif choice == '2':
                    print("NOTE! File must be a .csv file that you have exported previously or a similar file")
                    filename = input("Enter filepath to import from (default: entities.csv): ").strip() or 'entities.csv'
                    if anom_service.import_entities_from_csv(filename):
                        # Optionally validate the imported entities here
                        pass
                elif choice == '3':
                    break
                else:
                    print("Invalid choice. Please try again.")
            print(f"\nEntities exported/imported.")

        elif choice == '4':
            # Visualize entities
            anom_service.display_found_entities()

        elif choice == '5':
            # Add/update to keep list
            while True:
                print(f"\nCurrent list of to_keep words: {anom_service.to_keep_list}")
                print("Do you want to add more values i.e. extend the current list? \n"
                      "Or do you want to update the list i.e. overwrite it? Or return to the main menu?")
                add_up = input("1. Add more\n2. Update/overwrite\n3. Return\nOption: ")

                if add_up == '1':
                    new_words = input("Enter new words to add (separated by commas): ")
                    new_words_list = [word.strip() for word in new_words.split(',')]
                    anom_service.set_update_to_keep_list(new_words_list, method='add')
                    print(f"\nUpdated list of to_keep words: {anom_service.to_keep_list}")
                    break
                elif add_up == '2':
                    new_words = input("Enter new words to overwrite the current list (separated by commas): ")
                    new_words_list = [word.strip() for word in new_words.split(',')]
                    anom_service.set_update_to_keep_list(new_words_list, method='update')
                    print(f"\nUpdated list of to_keep words: {anom_service.to_keep_list}")
                    break
                elif add_up == '3':
                    print("Returning to the main menu.")
                    break
                else:
                    print("Invalid option selected. Please choose either 1, 2, or 3.")

        elif choice == '6': # TODO user should know that this is for all but
            # Anonymize texts
            for name, text_content in text_dict.items():
                text = "".join(text_content) if isinstance(text_content, list) else text_content
                anom_text[name], anom_keys[name] = anom_service.anonymize_text(text)
            print("\nAnonymization done.")

        elif choice == '7':
            # Visualize anonymized files
            visualize_results(anom_text)

        elif choice == '8':  # TODO use six automatically before this
            # Save anonymized files
            if not anom_text:
                print("No anonymized text to save. Anonymize text first!")
                continue
            print("Paste/type here path to folder where you want to save anonymized files.\n Type 'done' to return without saving.")
            folder_path = input("Path: ")
            if folder_path.startswith('"') or folder_path.endswith('"'):
                folder_path = folder_path.strip('"')
            while folder_path != 'done' and not os.path.isdir(folder_path):
                print("Incorrect path. Try again")
                folder_path = input("Paste/type path: ")
                if folder_path.startswith('"') or folder_path.endswith('"'):
                    folder_path = folder_path.strip('"')
            if folder_path == 'done':
                print("Returning without saving.")
                continue
            if SimpleFileWriter().save_files(anom_text, folder_path=folder_path):
                print("Anonymized files saved.")
            else:
                print("Anonymized files NOT saved.")
                visualize_results(anom_text)

        elif choice == '9':
            # Visualize keys
            visualize_results(anom_keys)

        elif choice == '10':
            # Save keys
            csv_file = 'keys_from_files.csv'
            user_name = input(f"Give name for file where keys will be saved. Press enter to use {csv_file}.\nFile name: ")
            if user_name:
                csv_file = user_name
                if not csv_file.endswith(".csv"):
                    csv_file = csv_file + '.csv'
            if SimpleFileWriter().save_keys_to_csv(anom_keys, csv_file):
                print("Keys saved.")
            else:
                visualize_results(anom_keys)

        elif choice == '11':
            # Test stuff
            #false_pos_res = anom_service.automated_manipulation_for_ents()
            print("\nSorry, as this will be implemented in the future, only the results will be exported but this doesn't "
                  "affect to the actual list of entities. This is because of problems with accuracy in automatic entity "
                  "recognition.")
            #print(f"False-positive result: \n{false_pos_res}")
            fixed_list = anom_service.try_to_map_similar_entities(entities=anom_service.found_words.copy())
            anom_service.export_raw_words_to_csv(filename="results_of_autom_ent_manipulation.csv", test_ents=fixed_list)
            #print("Saving completed: ", )

        elif choice == '12':
            csv_file = 'found_entities_raw.csv'
            user_name = input(f"Give name for file where raw data will be saved. Press enter to use {csv_file}.\nFile name: ")
            if user_name:
                csv_file = user_name
                if not csv_file.endswith(".csv"):
                    csv_file = csv_file + '.csv'
            anom_service.export_raw_words_to_csv(filename=csv_file)

        elif choice == '13':
            # Save anonymized pdf files to original format
            if not anom_service.found_words or len(anom_service.found_words) == 0:
                print("No found entities. Find or import them first.")
                continue
            if len(file_reader.pdf_file_paths) == 0:
                print("No pdf files detected. Read pdf files first to memory.")
                continue
            if len(file_reader.pdf_file_paths) < len(text_dict):
                print(f"NOTE! Detected that there is {len(text_dict) - len(file_reader.pdf_file_paths)} files other than "
                      f"pdf-files. This will only apply to the pdf files! Handle other files with methods 6 and 8.")

            print("Paste/type here path to folder where you want to save anonymized files.\n Type 'done' to return without saving.")
            folder_path = input("Path: ")
            if folder_path.startswith('"') or folder_path.endswith('"'):
                folder_path = folder_path.strip('"')
            while folder_path != 'done' and not os.path.isdir(folder_path):
                print("Incorrect path. Try again")
                folder_path = input("Paste/type path: ")
                if folder_path.startswith('"') or folder_path.endswith('"'):
                    folder_path = folder_path.strip('"')
            if folder_path == 'done':
                print("Returning without saving.")
                continue
            pdfanonymizer = PDFAnonymizer(pdf_paths=file_reader.pdf_file_paths, replacements=anom_service.found_words, save_path=folder_path)
            pdfanonymizer.replace_words()

        elif choice == '99':
            # Stop the process
            print("Process stopped.")
            break
        else:
            print("Invalid option. Please select a valid number from menu options.")


def visualize_results(data):
    """
    Visualizes different types of data (entities, anonymized texts, or keys) in a clear and readable format.

    Parameters:
    - data: The data to visualize. Could be entities, anonymized texts, or keys.
    """
    if not data:
        print("No data to visualize.")
        return

    # Check if the data is for entities (list or dict of lists)
    if all(isinstance(v, list) for v in data.values()):
        print("\nVisualizing Entities:")
        for name, entities in data.items():
            print(f"\nFile: {name}")
            for entity in entities:
                print(f" - Entity: {entity}")

    # Check if the data is for anonymized texts or keys (dict of strings or dict of dicts)
    elif all(isinstance(v, str) for v in data.values()):
        print("\nVisualizing Anonymized Texts:")
        for name, text in data.items():
            print(f"\nFile: {name}")
            print("Text:")
            print(text[:500] + "..." if len(text) > 500 else text)  # Print a snippet for long texts
    elif all(isinstance(v, dict) for v in data.values()):
        print("\nVisualizing Keys or Detailed Data:")
        for name, details in data.items():
            print(f"\nFile: {name}")
            for key, value in details.items():
                print(f" - {key}: {value}")
    else:
        print("\nUnknown data format.")



if __name__ == "__main__":
    main()
