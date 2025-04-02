import os
import re
import sys
from pdf2image import convert_from_path
from PIL import Image

def to_snake_case(name):
    """Convert string to snake_case"""
    # Remove file extension first
    name = os.path.splitext(name)[0]
    # Replace spaces/special chars with underscores
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    # Replace any non-alphanumeric with underscore and convert to lowercase
    return re.sub(r'[^a-zA-Z0-9]', '_', s2).lower()

def create_thumbnail(pdf_path, output_dir, dpi=200, size=(800, 800)):
    """
    Convert the first page of a PDF to a WebP thumbnail
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the thumbnail
        dpi: DPI for PDF rendering (higher = better quality but larger file)
        size: Maximum width and height of the thumbnail
    """
    filename = os.path.basename(pdf_path)
    output_filename = f"{to_snake_case(filename)}.webp"
    output_path = os.path.join(output_dir, output_filename)
    
    # Convert only the first page of the PDF
    pages = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
    if pages:
        # Get the first page
        img = pages[0]
        # Resize while maintaining aspect ratio
        img.thumbnail(size)
        # Convert to WebP with optimization
        img.save(output_path, format="WEBP", optimize=True, quality=80)
        print(f"Created thumbnail: {output_path}")
    else:
        print(f"Failed to convert {pdf_path}")

def main():
    # Get source directory from command line argument or use current directory
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    else:
        source_dir = "."  # Current directory (catalogs)
    
    # Ensure the path exists
    if not os.path.exists(source_dir):
        print(f"Error: Directory '{source_dir}' does not exist.")
        sys.exit(1)
    
    # Create thumbnail directory if it doesn't exist
    thumbnail_dir = os.path.join(source_dir, "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    # Process all PDF files in the source directory
    pdf_count = 0
    for filename in os.listdir(source_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(source_dir, filename)
            create_thumbnail(pdf_path, thumbnail_dir)
            pdf_count += 1
    
    print(f"Processed {pdf_count} PDF files from {source_dir}")
    print(f"Thumbnails saved to {thumbnail_dir}")

if __name__ == "__main__":
    main()