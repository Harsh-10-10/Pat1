import re

def extract_proposals(input_file, output_file):
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file  was not found.")
        return

    
    pattern = re.compile(r"(-{50,}\s+Prop\.# Proposal.*?)(?=\n\s*-{50,}|</TABLE>)",re.DOTALL)
    proposal_blocks = pattern.findall(content)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            
            f.write("\n\n".join(proposal_blocks))
            f.write("\n--------------------------------------------------------------------------------------------------------------------------")

        print(f" proposal tables extracted to '{output_file}'")
    except IOError as e:
        print(f"Error: Could not write to the file , Reason: {e}")

if __name__ == '__main__':
    input_filename = 'appleton_npx 1 1.txt'
    output_filename = 'proposals.txt'

    extract_proposals(input_filename, output_filename)