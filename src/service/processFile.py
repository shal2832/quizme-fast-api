
from fastapi.responses import JSONResponse

def chunk_file(file, chunk_size):
    """
    Generator that yields chunks of the file.
    
    :param file: The file to be chunked.
    :param chunk_size: The size of each chunk in bytes.
    """
    # while True:
    #     chunk = file.read(chunk_size)
    #     if not chunk:
    #         break
    #     yield chunk

    return JSONResponse(content={"message": "File processed successfully", "file" : file.filename}, status_code=200)