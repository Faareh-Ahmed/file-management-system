import json
import os
from colorama import Style

from colorama import Fore

class FileSystem:
    def __init__(self):
        self.data_file = "OEL_OS.json"
        if os.path.exists(self.data_file) and os.path.getsize(self.data_file) > 0:
            with open(self.data_file, "r") as f:
                try:
                    self.directory = json.load(f)
                except json.JSONDecodeError:
                    print("Error: Invalid JSON data in the file. Using default directory structure.")
                    self.directory = {"/": {}}
        else:
            # Self Directory is our Main Directory Data structure
            self.directory = {"/": {"type": "directory"}}  # Initialize with root directory
        
        # Current Path keeps us updated about the Path on which we are currently present in our File Management System
        self.current_path = "/"  # Current directory starts from root
        # Current Directory is a Temporary Data Structure that is responsible for doing changes and then reflect back the changes to the Main directory
        self.current_directory=self.directory[self.current_path]
        # print("Iniital Directory ", self.directory)
        print("Current Path ", self.current_path)

    # This method Updates the Main Directory, by refleceted the changes done in the Current Directory datastructure
    def update_directory(self,temp):
        """
        Updates the directory structure based on changes in the current_directory.

        This function dynamically traverses the directory structure using the
        current_path and updates the corresponding dictionary in self.directory
        to reflect the changes in current_directory.
        """
        print(" current path ",self.current_path)
        
        current_dict = self.directory
        current_dict = current_dict.get('/') #since we start from the Root "/"
        current_path_parts = self.current_path.strip("/").split("/")  # Split path into parts separated by /
        # print("current Path part: ",current_path_parts)
        # print("Current Disct: ",current_dict)

        # Iterate through path parts, updating dictionaries
        for part in current_path_parts:
            # print("Part: ",part)
            if part:  # Skip empty parts 
                current_dict = current_dict.get(part)  # Get nested sub dictionary
                # print("inside If: ", current_dict)
                if current_dict is None:
                    raise ValueError(f"Invalid path: Directory '{part}' not found")

        # Update the final dictionary with the current_directory contents
        current_dict.update(self.current_directory)
        # Save the updated directory structure to the file
        self.save_state()


    # Method to dump the changes done in Main directory
    def save_state(self):
        with open(self.data_file, "w") as f:
            json.dump(self.directory, f)

    # Method to Create a File in existing Directory
    def create(self, name):

        # Check if the file already exists in the current directory
        if name in self.current_directory:
            print(f"File or directory already exists at path '{self.current_path}'.")
            return

        # Create the file in the current directory
        self.current_directory[name] = {'type': 'file', 'content': '', 'size': 0}
        temp=self.current_path
        # Update the Main dictioary content by reflecting the changes done in the Current Directory
        self.update_directory(temp)
        self.save_state()
        print(f"File '{name}' created in directory '{self.current_path}'.")


    # Method to delete the File from Current Directory (Not tested)
    def delete(self, name):
        if name not in self.current_directory:
            print("File does not exist.")
            return

        del self.current_directory[name]
        temp=self.current_path
        # Update the Main dictioary content by reflecting the changes done in the Current Directory
        self.update_directory(temp)
        self.save_state()
        print(f"File '{name}' deleted from directory '{self.current_path}'.")


    # Method to create the directory
    def mkdir(self, name):
        if name in self.current_directory:
            print(f"{name} already exists in current Path {self.current_path}")
            return

        # Set the type for the new directory
        new_directory = {"type": "directory"}

        self.current_directory[name] = new_directory
        temp=self.current_path
        self.update_directory(temp)
        self.save_state()
        print(f"Directory '{name}' created in directory '{self.current_path}'.")


    # Method to Change the working directory
    def chDir(self, dirName):
    # Check if the directory path starts with '/'
        if dirName.startswith('/'):
            # If it starts with '/', set the current_path to root '/'
            self.current_path = '/'
            self.current_directory=self.current_directory[self.current_path]
            # Remove the leading '/' from the path
            dirName = dirName[1:]

        # Handle moving to the parent directory
        if dirName == "..":
            # If already at the root directory, cannot move further up
            if self.current_path == '/':
                print("Already at the root directory.")
                return
            # Remove the last directory from the current_path
            # print("Before cutting :\n",self.current_path)
            self.current_path = '/'.join(self.current_path.split('/')[:-2]) + '/'
            # print("After cutting :\n",self.current_path)
            # Set the current_directory accordingly
            if self.current_path == '/':
                self.current_directory = self.directory['/']
            else:
                current_dict = self.directory["/"]
                current_path_parts = self.current_path.strip("/").split("/")
                # print("Current Path parts:\n",current_path_parts)
                for part in current_path_parts:
                    if part:  # Skip empty parts 
                        current_dict = current_dict.get(part)  # Get nested sub dictionary
                        if current_dict is None:
                            raise ValueError(f"Invalid path: Directory '{part}' not found")
                self.current_directory = current_dict
        else:
            # Split the directory path by '/'
            dirs = dirName.split('/')
    

            # Iterate through each directory in the path
            for d in dirs:
                # Check if the directory exists in the current directory
                if d not in self.current_directory:
                    print(f"Icorrect Path.")
                    return
                # Update current_path to the next directory
                self.current_path += f"{d}/"
                # Update self.directory to the next directory
                # print(self.current_directory)
                self.current_directory = self.current_directory[d]
                # print(self.current_directory)
        print(f"Changed directory to '{self.current_path}'.")

    
    def move(self,source,target):
        # Check if the source File exists in the current Directory
        if source not in self.current_directory:
            print(f"{source} not Present in current Path: {self.current_path}")
            return
        
        # Get the file content before deleting it from the current directory
        file_content = self.current_directory[source]
        # Remove the source File from current Directory
        del self.current_directory[source]
        # Store the original source directory path
        original_path = self.current_path
        original_directory = self.current_directory     

        # Now we need to update our current Path to the Target Place
        if target.startswith('/'):
            # If it starts with '/', set the current_path to root '/'
            self.current_path = '/'
            self.current_directory=self.directory[self.current_path]
            # Remove the leading '/' from the path
            target = target[1:]

        # Split the directory path by '/'
        dirs = target.split('/')

        # Iterate through each directory in the path
        for d in dirs:
            # Check if the directory exists in the current directory
            if d not in self.current_directory:
                print(f"Icorrect Path.")
                return
            # Update current_path to the next directory
            self.current_path += f"{d}/"
            # Update self.directory to the next directory
            # print(self.current_directory)
            self.current_directory = self.current_directory[d]
            # print(self.current_directory)
        print(f"Changed directory to '{self.current_path}'.")


        # Add the file to the target directory
        self.current_directory[source] = file_content
        # Add the Source file to this target directory
        # self.current_directory.update(source)
        temp=self.current_path
        self.update_directory(temp)
        self.save_state()
        
        # After Moving the File from source to target
        # we now maintain the original current path to the source directory
        # Restore the original current path to the source directory
        self.current_path = original_path
        self.current_directory = original_directory
        print(f"{source} Moved into the path {target}")

        print("Moved Successful")

    
# This method displays the filenames and directories present in the current path
    def display(self):
        """
        List the contents of the current directory.
        """
        if len(self.current_directory) == 1 and 'type' in self.current_directory:
            print("Directory is empty.")
            return

        print("Contents of current directory:")
        for item, data in self.current_directory.items():
            if item == "type":
                continue
            # print(f"Item: {item}, Data: {data}")
            if data['type'] == 'file':
                print(f"{Fore.BLUE}{item}{Style.RESET_ALL}")
            elif data['type'] == 'directory':
                print(f"{Fore.GREEN}{item}{Style.RESET_ALL}")


# This method opens the File with a Mode and passes to the File class for read write operations
    def open(self, fName, mode):
        if fName not in self.current_directory:
            print("File does not exist.")
            return None
        return File(self.current_directory[fName], mode)
    


class File:
    def __init__(self, file_data, mode):
        self.file_data = file_data
        self.mode = mode

    def write_to_file(self, text, write_at=None):
        if self.mode == "append":
            self.file_data['content'] += text
            self.file_data['size'] += len(text)
        elif self.mode == "write_at":
            if write_at is None:
                write_at = len(self.file_data['content'])  # Default to end of file
            if write_at < 0 or write_at > len(self.file_data['content']):
                print("Invalid write_at position.")
                return
            self.file_data['content'] = self.file_data['content'][:write_at] + text + self.file_data['content'][write_at:]
            self.file_data['size'] = len(self.file_data['content'])
        else:
            print("Invalid mode specified.")

    def read_from_file(self, start=None, size=None):
        if start is None and size is None:
            return self.file_data['content']
        elif start is not None and size is None:
            return self.file_data['content'][start:]
        elif start is not None and size is not None:    
            return self.file_data['content'][start:start+size]
        else:
            print("Invalid arguments provided.")


    def close(self):
        # Perform any cleanup if needed
        pass




def print_commands():
    print("Available commands:")
    print("cd <directory_name> - Change directory")
    print("mkdir <directory_name> - Create a new directory")
    print("create <file_name> - Create a new file")
    print("write <file_name> - Write to a file")
    print("read <file_name> - Read from a file")
    print("delete <file_name> - Delete a file")
    print("move <source_path> <destination_path> - Move a file or directory")
    print("ls - List contents of current directory")
    print("exit - Exit the program")




# Initialize file system
fs = FileSystem()

while True:
    command = input("Enter a command (type 'help' for available commands): ").split()

    if not command:
        continue

    if command[0] == "help":
        print_commands()
    elif command[0] == "cd":
        if len(command) != 2:
            print("Usage: cd <directory_name>")
        else:
            fs.chDir(command[1])
    elif command[0] == "mkdir":
        if len(command) != 2:
            print("Usage: mkdir <directory_name>")
        else:
            fs.mkdir(command[1])
    elif command[0] == "create":
        if len(command) != 2:
            print("Usage: create <file_name>")
        else:
            fs.create(command[1])
    elif command[0] == "write":
        if len(command) != 2:
            print("Usage: write <file_name>")
        else:
            file_name = command[1]
            mode = input("Choose write mode ('append' or 'write_at'): ")
            if mode not in ["append", "write_at"]:
                print("Invalid write mode specified.")
                continue
            file_obj = fs.open(file_name, mode)
            text = input("Enter text to write: ")
            file_obj.write_to_file(text)
            # After writing to the file, update the directory structure
            fs.update_directory(fs.current_path)
            file_obj.close()

    elif command[0] == "read":
        if len(command) != 2:
            print("Usage: read <file_name>")
        else:
            file_name = command[1]
            mode = input("Choose read mode ('start', 'size', or 'full'): ")
            if mode not in ["start", "size", "full"]:
                print("Invalid read mode specified.")
                continue
            if mode == "start":
                # Read from Start Position entered by user till EOF
                start = int(input("Enter start position: "))
                file_obj = fs.open(file_name, "read")
                print(file_obj.read_from_file(start))
                file_obj.close()
            elif mode == "size":
                # Read from Specified Start point and Read upto Size defined
                start = int(input("Enter start position: "))
                size = int(input("Enter size: "))
                file_obj = fs.open(file_name, "read")
                print(file_obj.read_from_file(start, size))
                file_obj.close()
            else:  # mode == "full" means that read full file Sequentially
                file_obj = fs.open(file_name, "read")
                print(file_obj.read_from_file())
                file_obj.close()


    elif command[0] == "delete":
        if len(command) != 2:
            print("Usage: delete <file_name>")
        else:
            fs.delete(command[1])
    elif command[0] == "move":
        if len(command) != 3:
            print("Usage: move <source_path> <destination_path>")
        else:
            fs.move(command[1], command[2])
    elif command[0] == "ls":
        fs.display()
    elif command[0] == "exit":
        print("Exiting the program.")
        break
    else:
        print("Invalid command. Type 'help' for available commands.")

