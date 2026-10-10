| Case | Exit | Outcome |
|---|---:|---|
| save_txt | 0 | Saved successfully |
| save_csv | 0 | Saved successfully |
| save_xlsx | 0 | Saved successfully |
| missing_profile | 0 | Saved successfully |
| save_batch | 0 | Saved successfully |
| slash_txt_batch | 1 | FileNotFoundError: [Errno 2] No such file or directory: 'a/b.txt' |
| slash_csv_batch | 1 | FileNotFoundError: [Errno 2] No such file or directory: 'a/b.csv' |
| slash_xlsx_batch | 1 | OSError: Cannot save file into a non-existent directory: 'a' |
| missing_output_parent | 1 | FileNotFoundError: [Errno 2] No such file or directory: 'nonexistent/results.txt' |
| output_is_directory | 1 | IsADirectoryError: [Errno 21] Is a directory: 'directory' |
| read_only_output | 1 | PermissionError: [Errno 13] Permission denied: 'readonly/results.txt' |
| folder_is_file | 1 | FileExistsError: [Errno 17] File exists: 'blocked' |
