import pandas as pd

file_path = 'cleaned_boarding_data.xlsx'
df = pd.read_excel(file_path)

travel_doc_person_map = {}

discrepancies = []

def check_person_consistency(row):
    travel_doc = row['TravelDoc']
    personal_details = {
        'FirstName': row['FirstName'],
        'LastName': row['LastName'],
        'PassengerSex': row['PassengerSex'],
        'PassengerBirthDate': row['PassengerBirthDate']
    }

    if travel_doc in travel_doc_person_map:
        stored_details = travel_doc_person_map[travel_doc]
        
        for field in personal_details:
            if personal_details[field] != stored_details[field]:
                discrepancies.append({
                    'TravelDoc': travel_doc,
                    'Field': field,
                    'ExpectedValue': stored_details[field],
                    'InconsistentValue': personal_details[field]
                })
    else:
        travel_doc_person_map[travel_doc] = personal_details

def split_full_name(full_name):
    name_parts = full_name.split()
    if len(name_parts) == 3:
        return {
            'LastName': name_parts[0],
            'FirstName': name_parts[1],
            'SecondName': name_parts[2]
        }
    else:
        print("oshibka")
        return None

def check_person_consistency_sirens(row):
    travel_doc = row['TravelDoc']
    
    
    full_name_details = split_full_name(row['FullName'])
    
    if full_name_details is None:
        print(f"Problem with FullName format for TravelDoc {travel_doc}: '{row['FullName']}' does not split into 3 parts.")
        return
    
    
    personal_details = {
        **full_name_details
    }
 
    if travel_doc in travel_doc_person_map:
        stored_details = travel_doc_person_map[travel_doc]
        
        for field in personal_details:
            if personal_details[field] != stored_details[field]:
                discrepancies.append({
                    'TravelDoc': travel_doc,
                    'Field': field,
                    'ExpectedValue': stored_details[field],
                    'InconsistentValue': personal_details[field]
                })
    else:
        travel_doc_person_map[travel_doc] = personal_details

df.apply(check_person_consistency, axis=1)

if discrepancies:
    print(f"Discrepancies found for {len(discrepancies)} instance(s):")
    for discrepancy in discrepancies:
        print(f"\nTravelDoc: {discrepancy['TravelDoc']}")
        print(f"Field: {discrepancy['Field']}")
        print(f"Expected: {discrepancy['ExpectedValue']}, Found: {discrepancy['InconsistentValue']}")
else:
    print("No discrepancies found. All TravelDocs are consistently used by the same person.")