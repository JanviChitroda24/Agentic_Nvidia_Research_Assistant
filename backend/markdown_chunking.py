import re
import json

def chunk_markdown_by_headers(markdown_text, ideal_word_count=500, min_content_chars=200):
    """
    Splits the markdown content into chunks based on headers and content size.
    Merges headers with small content until sufficient content is accumulated.
    
    Parameters:
        markdown_text (str): The full markdown text to be chunked.
        ideal_word_count (int): Ideal word count for a chunk (default is 500).
        min_content_chars (int): Minimum content size between headers (default is 200).
    
    Returns:
        List[Dict]: A list of chunk dictionaries with header metadata.
    """
    # Define the threshold to split: 1.5 * ideal_word_count
    split_threshold = int(1.5 * ideal_word_count)
    
    # Regex to match markdown headers at the beginning of a line.
    header_pattern = re.compile(r'^(#{1,6})\s*(.+)$', re.MULTILINE)
    
    # Find all header matches with their start positions.
    matches = list(header_pattern.finditer(markdown_text))
    
    # If no header is found, treat the entire text as one chunk.
    if not matches:
        return [{
            'header': None,
            'level': None,
            'content': markdown_text.strip()
        }]
    
    # Create segments with headers and their content
    segments = []
    for idx, match in enumerate(matches):
        start_index = match.start()
        end_index = matches[idx + 1].start() if idx + 1 < len(matches) else len(markdown_text)
        header_line = match.group(0).strip()
        header_level = len(match.group(1))
        content = markdown_text[start_index:end_index].strip()
        
        # Calculate the actual content size (excluding the header)
        content_without_header = content[len(header_line):].strip()
        content_length = len(content_without_header)
        
        segments.append({
            'header': header_line,
            'level': header_level,
            'content': content,
            'content_without_header': content_without_header,
            'content_length': content_length,
        })
    
    # Improved merging logic - keep merging until we have enough content
    final_chunks = []
    current_merged_chunk = None
    current_merged_headers = []
    current_merged_content = ""
    current_content_length = 0
    
    for segment in segments:
        # If we don't have a current chunk or the current segment has small content
        if current_merged_chunk is None:
            # Start a new merged chunk
            current_merged_chunk = {
                'header': segment['header'],
                'level': segment['level'],
            }
            current_merged_headers = [segment['header']]
            current_merged_content = segment['content']
            current_content_length = segment['content_length']
        else:
            # Always merge if the content is too small
            if segment['content_length'] < min_content_chars or current_content_length < min_content_chars:
                # Add to the current merged chunk
                current_merged_headers.append(segment['header'])
                current_merged_content += "\n\n" + segment['content']
                current_content_length += segment['content_length']
            else:
                # We have enough content in the current chunk, so finalize it
                current_merged_chunk['content'] = current_merged_content
                current_merged_chunk['merged_headers'] = current_merged_headers
                final_chunks.append(current_merged_chunk)
                
                # Start a new chunk with this segment
                current_merged_chunk = {
                    'header': segment['header'],
                    'level': segment['level'],
                }
                current_merged_headers = [segment['header']]
                current_merged_content = segment['content']
                current_content_length = segment['content_length']
    
    # Add the last chunk if there's any
    if current_merged_chunk is not None:
        current_merged_chunk['content'] = current_merged_content
        current_merged_chunk['merged_headers'] = current_merged_headers
        final_chunks.append(current_merged_chunk)
    
    # Check if any chunks are too large and need splitting
    result_chunks = []
    for chunk in final_chunks:
        words = chunk['content'].split()
        if len(words) > split_threshold:
            # Split into two parts (roughly equal halves)
            mid_point = len(words) // 2
            part1_text = " ".join(words[:mid_point])
            part2_text = " ".join(words[mid_point:])
            
            # Keep the same header information for both parts
            result_chunks.append({
                'header': chunk['header'],
                'level': chunk['level'],
                'content': part1_text,
                'merged_headers': chunk['merged_headers'],
                'part': 1
            })
            result_chunks.append({
                'header': chunk['header'],
                'level': chunk['level'],
                'content': part2_text,
                'merged_headers': chunk['merged_headers'],
                'part': 2
            })
        else:
            result_chunks.append(chunk)
    
    return result_chunks

# --- Main Section ---
# if __name__ == "__main__":
#     file_path = "/Users/janvichitroda/Documents/Janvi/NEU/Big_Data_Intelligence_Analytics/Assignment 5/Part 1/Janvi_Personal/2020_First_Quarter.md"
    
#     with open(file_path, "r", encoding="utf-8") as f:
#         sample_markdown = f.read()
    
#     # Get chunks from the markdown content with more aggressive merging for small content sections
#     chunks = chunk_markdown_by_headers(sample_markdown, min_content_chars=200)

#     output_file = "/Users/janvichitroda/Documents/Janvi/NEU/Big_Data_Intelligence_Analytics/Assignment 5/Part 1/Janvi_Personal/2020_First_Quarter.json"

#     # Write the chunks list to the JSON file
#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(chunks, f, ensure_ascii=False, indent=4)

#     print(f"Chunks successfully saved to {output_file}")