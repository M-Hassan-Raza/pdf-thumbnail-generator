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

def create_uniform_thumbnail(pdf_path, output_dir, target_width=400, target_height=300, dpi=200):
    """
    Convert the first page of a PDF to a WebP thumbnail with consistent dimensions
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the thumbnail
        target_width: Target width for the thumbnail
        target_height: Target height for the thumbnail
        dpi: DPI for PDF rendering (higher = better quality but larger file)
    """
    filename = os.path.basename(pdf_path)
    output_filename = f"{to_snake_case(filename)}.webp"
    output_path = os.path.join(output_dir, output_filename)
    
    # Convert only the first page of the PDF
    try:
        pages = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
        if not pages:
            print(f"Failed to convert {pdf_path} - no pages found")
            return False
            
        # Get the first page
        img = pages[0]
        
        # Step 1: Calculate aspect ratios
        target_ratio = target_width / target_height
        img_ratio = img.width / img.height
        
        # Step 2: Create a blank white image with the target dimensions
        thumbnail = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        
        # Step 3: Resize the image while maintaining aspect ratio
        if img_ratio > target_ratio:
            # Image is wider than target - resize based on height
            new_height = target_height
            new_width = int(img_ratio * new_height)
            resized = img.resize((new_width, new_height), Image.LANCZOS)
            # Center crop the width
            left = (new_width - target_width) // 2
            thumbnail.paste(resized.crop((left, 0, left + target_width, new_height)), (0, 0))
        else:
            # Image is taller than target - resize based on width
            new_width = target_width
            new_height = int(new_width / img_ratio)
            resized = img.resize((new_width, new_height), Image.LANCZOS)
            # Center crop the height
            top = (new_height - target_height) // 2
            thumbnail.paste(resized.crop((0, top, new_width, top + target_height)), (0, 0))
        
        # Step 4: Save as optimized WebP
        thumbnail.save(output_path, format="WEBP", optimize=True, quality=85)
        print(f"Created thumbnail: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return False

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
    success_count = 0
    failed_count = 0
    
    for filename in os.listdir(source_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(source_dir, filename)
            if create_uniform_thumbnail(pdf_path, thumbnail_dir):
                success_count += 1
            else:
                failed_count += 1
    
    print(f"\nSummary:")
    print(f"- Successfully processed: {success_count} PDFs")
    print(f"- Failed to process: {failed_count} PDFs")
    print(f"- Thumbnails saved to: {thumbnail_dir}")
    print(f"- Thumbnail dimensions: 400x300 pixels (matches your website requirements)")

if __name__ == "__main__":
    main()