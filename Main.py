import re
import pandas as pd




def extract_company_headers(input_file):
    with open(input_file, "r", encoding="utf-8") as file:   
        text = file.read()      # read the file as string

    pattern = re.compile(
        r"\n\s*(?P<Company>[A-Z0-9 .,()&\-]+?)\s+Agenda Number:\s+(?P<Agenda>\d+).*?"
        r"Security:\s+(?P<Security>\S+).*?"
        r"Meeting Type:\s+(?P<MeetingType>.*?)\s+"
        r"Meeting Date:\s+(?P<MeetingDate>.*?)\s+"
        r"Ticker:\s+(?P<Ticker>.*?)\s+"
        r"ISIN:\s+(?P<ISIN>\S+)",
        re.DOTALL
    )
    data = pattern.findall(text)
    columns = ["Company Name", "Agenda Number", "Security", "Meeting Type", "Meeting Date", "Ticker", "ISIN"]
    df_headers = pd.DataFrame(data, columns=columns)    # dataframe
    print("Company headers  is extracted.")
    return df_headers

def extract_proposals(proposals_file):
    with open(proposals_file, "r", encoding="utf-8") as file:
        lines = file.readlines()    # read the entire file as list 

    rough_data = [] # 
    company_id = 0 # initializes acounter to assign the ID to each company 
    JUNK_PATTERNS = [ "* Management", "----", "</TABLE>"]  

    for line in lines:
        line_clean = line.strip()
        
        if not line_clean or any(junk in line_clean for junk in JUNK_PATTERNS):
            continue
            
        is_header_line_1 = "Prop.#" in line and "Proposal" in line
        is_header_line_2 = line_clean.startswith("Type") and line_clean.endswith("Management")

        if is_header_line_1:
            company_id += 1 
            continue
        elif is_header_line_2:
            continue
        
        if company_id == 0: # edge case junk line that fails both boolean expression
            continue
            
        record = {
            'IDs': company_id,
            'Prop.#': line[0:7].strip(),
            'Proposal': line[7:58].strip(),
            'Proposal Type': line[58:72].strip(),
            'Proposal Vote': line[72:95].strip(),
            'For/Against Management': line[95:].strip()
        }
        if not record['Proposal Type'] and not record['Proposal Vote']: # adjustment
            record['Proposal'] = line[7:].strip()
        rough_data.append(record)

    return rough_data

def post_process_proposals(rough_data):

    final_data = []
    is_in_director_list = False
    for record in rough_data:
        if record['Prop.#']:
            is_in_director_list = False
        if record['Prop.#'] and record['Proposal'].strip().upper() == 'DIRECTOR':
            is_in_director_list = True
            
        if not final_data:
            final_data.append(record)
            continue
            
        if not record['Prop.#']:
            if is_in_director_list:
                final_data.append(record)
            else:
                final_data[-1]['Proposal'] += ' ' + record['Proposal']
        else:
            final_data.append(record)

    for record in final_data:
        record['Proposal'] = ' '.join(record.get('Proposal', '').split())
        if record['Proposal'].upper() == 'DIRECTOR':
            record['Proposal Type'] = ''
            record['Proposal Vote'] = ''
            record['For/Against Management'] = ''
            
    df_proposals = pd.DataFrame(final_data)
    df_proposals['IDs'] = df_proposals['IDs'].ffill().astype(int)
    return df_proposals

def merge_and_save(df_proposals, df_headers, output_file="final_merged_data.xlsx"):
    
    df_headers['IDs'] = range(1, len(df_headers) + 1)
    final_df = pd.merge(df_proposals, df_headers, on='IDs', how='left')

    
    final_df = final_df[['IDs', 'Company Name', 'Ticker', 'Meeting Date', 'Meeting Type', 'Security', 'ISIN', 'Agenda Number', 'Prop.#',
                          'Proposal', 'Proposal Type', 'Proposal Vote', 'For/Against Management']]
    
    final_df.to_excel(output_file, index=False)
    print(f"Merged data saved to '{output_file}'.")

def main():
    input_file = "appleton_npx 1 1.txt"
    proposals_file = "proposals.txt"
    output_file = "final_merged_data.xlsx"

    
    df_headers = extract_company_headers(input_file)
    rough_proposals = extract_proposals(proposals_file)
    df_proposals = post_process_proposals(rough_proposals)
    merge_and_save(df_proposals, df_headers, output_file)

if __name__ == "__main__":
    main()

