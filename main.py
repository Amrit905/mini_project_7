import json
import os

'''File Configuration'''
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT_FILE = os.path.join(BASE_DIR, "students_input.json")

OUTPUT_FILE = os.path.join(BASE_DIR, "students_valid.json")

ERROR_LOG_FILE = os.path.join(BASE_DIR, "import_errors.txt")

REQUIRED_FIELDS = ("student_id","name","department","marks")



'''Write Rejected recoprds or format/file error'''
def write_error_log(errors):

    try:
        with open(ERROR_LOG_FILE, "w", encoding="utf-8") as file:

            file.write("STUDENT RECORD IMPORT ERROR LOG\n")
            file.write("=" * 55 + "\n\n")

            if errors:
                file.writelines(
                    error + "\n" for error in errors
                )
            else:
                file.write("No errors found.\n")

        return True

    except PermissionError:
        print("Permission denied while writing the error log.")
        return False

    except OSError as error:
        print("Unable to write error log:", error)
        return False



'''Read Input'''
def read_file(input_path):
    print("\nImport Started:", input_path)
    
    try:
        with open(input_path,'r') as file:
            
            data =json.load(file)
            
    except FileNotFoundError:
        
        message =f"Input file not found: {input_path}"
        print("\nError:",message)
        write_error_log(message)
        return None
    
    except PermissionError:
        
        message = f"Permission denied: {input_path}"
        print("\nError:", message)
        write_error_log([message])
        return None
    
    except json.JSONDecodeError as error:
        
        message = ("Malformed JSON file. "f"Line {error.lineno}, column {error.colno}: {error.msg}")
        
        
        print("\nJSON parsing error:", message)
        print("No valid output file has been written.")
        write_error_log([message])
        return None
    
    except OSError as error:
        
        message = f"File reading error: {error}"
        print("\nError:", message)
        write_error_log([message])
        return None
    
    else:

        # JSON parsing completed successfully.
        if not isinstance(data, list):

            message = "The top-level JSON data must be a list."

            print("\nInvalid input format:", message)
            write_error_log([message])
            return None
        
        print("\nInput file read successfully.")
        print("Total records found:", len(data))

        # print("Input file read and parsed successfully.")

        return data 
    
    
    finally:
        print("Input file reading operation finished.")


#RECORD VALIDATION
def validate_record(records):
    
    # Each record must be a dictionary.
    if not isinstance(records, dict):

        raise TypeError(
            "Each student record must be a dictionary."
        )
    
    student_id = records["student_id"]
    name = records["name"]
    
    department = records["department"]
    marks = records["marks"]
    
    if not isinstance(student_id, str):
        raise TypeError("student_id must be a string.")

    if not isinstance(name, str):
        raise TypeError("name must be a string.")

    if not isinstance(department, str):
        raise TypeError("department must be a string.")

    # Validate non-empty fields.
    if not student_id.strip():
        raise ValueError("student_id cannot be empty.")

    if not name.strip():
        raise ValueError("name cannot be empty.")

    if not department.strip():
        raise ValueError("department cannot be empty.")

    # Marks must be a list.
    if not isinstance(marks, list):

        raise TypeError("marks must be a list.")

    # Exactly three marks are required.
    if len(marks) != 3:

        raise StudentRecordError(
            "marks must contain exactly 3 values."
        )

    # Validate every mark.
    for index, mark in enumerate(marks):

        # bool is a subclass of int in Python,
        # so it must be rejected explicitly.
        if isinstance(mark, bool):

            raise StudentRecordError(
                f"Mark {index + 1} cannot be a boolean."
            )

        if not isinstance(mark, (int, float)):

            raise StudentRecordError(
                f"Mark {index + 1} must be numeric."
            )

        if not 0 <= mark <= 100:

            raise StudentRecordError(
                f"Mark {index + 1} must be between 0 and 100."
            )

    # Return a clean record containing only required fields.
    return {
        "student_id": student_id.strip(),
        "name": name.strip(),
        "department": department.strip(),
        "marks": marks
    }
    

'''Custom Exception'''
class StudentRecordError(Exception):
    pass


#Records Processing
def process_records(records):

    valid_records = []
    errors = []
    accepted_ids = set()

    rejected_count = 0

    print("\nStarting record validation...")
    print("-" * 55)

    for record_number, record in enumerate(records, start=1):

        try:

            student = validate_record(record)

            student_id = student["student_id"]

            # Reject duplicate student IDs.
            if student_id in accepted_ids:

                raise StudentRecordError(
                    f"Duplicate student ID: {student_id}"
                )

        except KeyError as error:

            rejected_count += 1

            message = (
                f"Rejected record {record_number}: "
                f"missing required field {error}."
            )

            errors.append(message)
            print(message)

        except TypeError as error:

            rejected_count += 1

            message = (
                f"Rejected record {record_number}: "
                f"data type error - {error}"
            )

            errors.append(message)
            print(message)

        except ValueError as error:

            rejected_count += 1

            message = (
                f"Rejected record {record_number}: "
                f"invalid value - {error}"
            )

            errors.append(message)
            print(message)

        except IndexError as error:

            rejected_count += 1

            message = (
                f"Rejected record {record_number}: "
                f"index error - {error}"
            )

            errors.append(message)
            print(message)

        except StudentRecordError as error:

            rejected_count += 1

            message = (
                f"Rejected record {record_number}: {error}"
            )

            errors.append(message)
            print(message)

        else:

            # This block runs only when validation succeeds.
            valid_records.append(student)
            accepted_ids.add(student_id)

            print(
                f"Accepted: {student_id} - {student['name']}"
            )

    print("-" * 55)

    return valid_records, errors, rejected_count



#SAVE VALID RECORDS
def save_valid_records(valid_records):

    try:

        with open(OUTPUT_FILE,"w",encoding="utf-8") as file:

            json.dump(valid_records,file,indent=4)

        print("\nValid records saved successfully.")

        return True

    except PermissionError:

        print("\nPermission denied while saving valid records.")
        return False

    except OSError as error:

        print("\nUnable to save valid records:", error)
        return False


# ============================================================
#                    MAIN FUNCTION
# ============================================================

def main():

    print("=" * 65)
    print("       RELIABLE STUDENT RECORDS IMPORT & VALIDATION TOOL")
    print("=" * 65)

    input_path = input(
        "\nEnter input JSON file path "
        "(press Enter for students_input.json): "
    ).strip()

    if input_path == "":
        input_path = DEFAULT_INPUT_FILE

    # Convert the supplied path into an absolute path.
    input_path = os.path.abspath(input_path)

    # Read and parse the source file first.
    records = read_file(input_path)

    # None means the input could not be safely processed.
    if records is None:

        print("\nImport stopped because input processing failed.")
        return

    # Validate records only after successful JSON parsing.
    valid_records, errors, rejected_count = process_records(
        records
    )

    # Save accepted records.
    output_saved = save_valid_records(valid_records)

    # Save rejected-record explanations.
    log_saved = write_error_log(errors)

    # Final summary.
    print("\n" + "=" * 65)
    print("                    IMPORT SUMMARY")
    print("=" * 65)

    print("Total input records :", len(records))
    print("Accepted records    :", len(valid_records))
    print("Rejected records    :", rejected_count)


    if output_saved:
        print("Valid output        :", OUTPUT_FILE)
    else:
        print("Valid output        : Could not be saved.")

    if log_saved:
        print("Error log           :", ERROR_LOG_FILE)
    else:
        print("Error log           : Could not be saved.")

    print("=" * 65)
    print("\nImport completed.")
    


if __name__ =="__main__":
    main()