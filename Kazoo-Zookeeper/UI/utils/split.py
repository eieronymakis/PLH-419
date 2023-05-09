import os

def split_file(file_path, num_chunks):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    num_lines = len(lines)
    lines_per_chunk = num_lines // num_chunks

    files = []

    basename = os.path.basename(file_path)
    prefix = os.path.splitext(basename)[0]

    for i in range(num_chunks):
        start_idx = i * lines_per_chunk
        end_idx = (i+1) * lines_per_chunk if i < num_chunks-1 else num_lines
        chunk = lines[start_idx:end_idx]


        with open(os.path.dirname(__file__)+'/../shared/'+prefix+'_chunk_'+str(i+1)+'.txt', 'w')as f:
            f.writelines(chunk)
            files.append(prefix+'_chunk_'+str(i+1)+'.txt')
    
    return files
        
