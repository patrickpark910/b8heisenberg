import os
import re

def extract_keff_values():
    """
    Reads all text files in a directory, extracts keff values and records them
    along with the filename.
    
    Args:
        directory (str): Path to the directory containing text files
    
    Returns:
        list: List of tuples containing (filename, keff_value)
    """
    # List to store results
    directory = "./outputs"
    results = []
    
    # Check if directory exists
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return results
    
    # Pattern to match "keff = " followed by a value
    pattern = r"track-length keff = ([\d.]+)"
    
    # Go through all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # Check if it's a file (not a subdirectory) and has a text extension
        # Modify this condition if you're looking for specific file extensions
        if os.path.isfile(file_path) and filename.endswith(('.o')):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Search for the pattern
                    match = re.search(pattern, content)
                    if match:
                        keff_value = match.group(1)
                        results.append((filename, keff_value))
                        print(f"File: {filename}, keff = {keff_value}")
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
    
    return results

def write_results_to_file(results, output_file="keff_results.csv"):
    """
    Writes the results to a CSV file.
    
    Args:
        results (list): List of tuples containing (filename, keff_value)
        output_file (str): Name of the output file
    """
    if not results:
        print("No results to write.")
        return
    
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            # Write header
            file.write("Filename,keff value\n")
            
            # Write data
            for filename, keff_value in results:
                file.write(f"{filename},{keff_value}\n")
                
        print(f"Results written to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    import sys
    
    # Extract keff values from files in the directory
    results = extract_keff_values()
    
    # Output file name (optional command line argument)
    output_file = sys.argv[2] if len(sys.argv) > 2 else "keff_results.csv"
    
    # Write results to file
    write_results_to_file(results, output_file)
    
    # Print summary
    print(f"\nSummary: Found keff values in {len(results)} files.")