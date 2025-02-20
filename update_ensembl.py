import gzip
import re
import requests

# URL of the latest GTF file from GENCODE (GRCh38.p13)
GTF_URL = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_39/gencode.v39.annotation.gtf.gz"
GTF_FILE = "gencode.v39.annotation.gtf.gz"
OUTPUT_FILE = "all_genes.txt"
OUTPUT_DICT_FILE = "all_genes_dict.txt"

# Function to download the GTF file
def download_gtf(url, filename):
    print("Downloading GTF file... This may take a few minutes.")
    response = requests.get(url, stream=True)
    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print("Download complete.")

# Function to extract gene IDs and names
def extract_genes(gtf_filename, output_filename, output_filename_dict):
    gene_pattern = re.compile(r'gene_id "([^"]+)";.*?gene_name "([^"]+)";')
    
    dict_gene = {}
    with gzip.open(gtf_filename, "rt") as f, open(output_filename, "w") as out_file:
        for line in f:
            if line.startswith("#"):
                continue  # Skip header
            columns = line.strip().split("\t")
            if columns[2] == "gene":  # Only process gene lines
                match = gene_pattern.search(columns[8])
                if match:
                    gene_id, gene_name = match.groups()
                    out_file.write(f"{gene_id} ({gene_name})\n")
                    dict_gene[gene_name] = gene_id 
    with open(output_filename_dict, "w") as out_file:
        out_file.write(str(dict_gene))
    print(f"Extraction complete. Data saved to {output_filename}")

# Run the functions
download_gtf(GTF_URL, GTF_FILE)
extract_genes(GTF_FILE, OUTPUT_FILE, OUTPUT_DICT_FILE)
