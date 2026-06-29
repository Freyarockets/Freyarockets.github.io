extends Node

# Google Drive download links
var drive_link_1 = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID_1"
var drive_link_2 = "https://drive.google.com/uc?export=download&id=YOUR_FILE_ID_2"

# Output file paths
var output_path_1 = "user://downloaded_file_1.zip"
var output_path_2 = "user://downloaded_file_2.zip"

func _ready():
	download_files()

func download_files():
	print("Starting downloads...")
	
	# Download first file
	if download_file(drive_link_1, output_path_1):
		print("File 1 downloaded successfully to: ", output_path_1)
	else:
		print("Failed to download file 1")
	
	# Download second file
	if download_file(drive_link_2, output_path_2):
		print("File 2 downloaded successfully to: ", output_path_2)
	else:
		print("Failed to download file 2")

func download_file(url: String, output_path: String) -> bool:
	var http_request = HTTPRequest.new()
	add_child(http_request)
	
	# Connect signals
	http_request.request_completed.connect(self._on_download_complete.bind(output_path))
	
	# Make the request
	var error = http_request.request(url)
	
	if error != OK:
		print("Error making request: ", error)
		http_request.queue_free()
		return false
	
	# Wait for completion (blocking approach for simplicity)
	await http_request.request_completed
	
	http_request.queue_free()
	return true

func _on_download_complete(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray, output_path: String):
	if result == HTTPRequest.RESULT_SUCCESS and response_code == 200:
		# Save the file
		var file = FileAccess.open(output_path, FileAccess.WRITE)
		if file:
			file.store_buffer(body)
			print("File saved to: ", output_path)
		else:
			print("Failed to save file to: ", output_path)
	else:
		print("Download failed. Response code: ", response_code)
