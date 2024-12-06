import subprocess
import sys
import os
import stat
from dotenv import load_dotenv


class ScriptRunner:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.error_message = "Usage: update_app.py BASH_SCRIPT_FILE_NAME.sh BRANCH_NAME REPOSITORY_NAME"
        self.environment = os.environ.get('ENVIRONMENT')
        self.file_name = os.getenv(
            'BASH_SCRIPT_FILE_NAME', 'updateApplication.sh')
        self.repository_name = os.getenv('REPOSITORY_NAME')
        self.branch_name = self.get_branch_name()

    def get_branch_name(self):
        if self.environment == 'testing':
            return os.getenv('TESTING_BRANCH_NAME', 'testing')
        return os.getenv('MAIN_BRANCH_NAME')

    def validate_inputs(self):
        """Ensure that the necessary environment variables are set."""
        if not self.file_name or not self.branch_name or not self.repository_name:
            print("Error: BASH_SCRIPT_FILE_NAME, BRANCH_NAME, and REPOSITORY_NAME environment variables are required.")
            print(self.error_message)
            sys.exit(1)

    def check_file_exists(self):
        """Check if the script file exists."""
        if not os.path.isfile(self.file_name):
            print(f"Error: The file '{self.file_name}' does not exist.")
            print(self.error_message)
            sys.exit(1)

    def ensure_executable(self):
        """Ensure the script file has execution permission."""
        if not self.file_name.startswith('./'):
            self.file_name = f'./{self.file_name}'

        file_stat = os.stat(self.file_name)
        if not bool(file_stat.st_mode & stat.S_IXUSR):
            print(
                f"{self.file_name} does not have execution rights. Granting execution permission.")
            os.chmod(self.file_name, file_stat.st_mode | stat.S_IXUSR)

    def run_script(self):
        """Run the bash script with the provided branch and repository name."""
        try:
            result = subprocess.run(
                [self.file_name, self.branch_name, self.repository_name],
                check=True,
                text=True,
                capture_output=True
            )
            # Print the output of the bash script
            print(f"{self.file_name[2:]} script output:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            # Handle any errors during script execution
            print(f"An error occurred while running the bash script: {e}")
            print(f"Error output: {e.stderr}")

    def run(self):
        """Main function to validate inputs and run the script."""
        # Print the environment for user awareness
        print(f"Running script in environment: {self.environment}")

        self.validate_inputs()
        self.check_file_exists()
        self.ensure_executable()
        self.run_script()


# Main entry point
if __name__ == "__main__":
    runner = ScriptRunner()  # Initialize the class
    runner.run()  # Run the script execution process
