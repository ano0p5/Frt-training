import os
import dropbox

def get_dropbox_client():
    token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not token:
        raise EnvironmentError("Missing Dropbox access token. Set it as an environment variable.")
    return dropbox.Dropbox(token)

def upload_file(client, local_file, remote_path):
    try:
        with open(local_file, "rb") as f:
            print(f"Transferring {local_file} to {remote_path}...")
            client.files_upload(f.read(), remote_path)
        print(f"Successfully uploaded: {remote_path}")
    except Exception as e:
        print(f"Failed to upload {local_file}. Reason: {str(e)}")

def sync_folder_to_dropbox(directory, destination):
    client = get_dropbox_client()

    for subdir, _, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(subdir, filename)
            relative_path = os.path.relpath(full_path, directory)
            remote_path = f"{destination}/{relative_path}".replace("\\", "/")
            upload_file(client, full_path, remote_path)

if __name__ == "__main__":
    source_folder = "/home/anoop/frt/soft_reelly/soft_reely_images"
    target_folder = "/softreelly_images"
    sync_folder_to_dropbox(source_folder, target_folder)

    source_folder_pdfs = "/home/anoop/frt/soft_reelly/soft_reelly_pdf"
    target_folder_pdfs = "/softreelly_pdfs"
    sync_folder_to_dropbox(source_folder_pdfs, target_folder_pdfs)
