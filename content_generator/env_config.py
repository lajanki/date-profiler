import os


# Set the pattern for determining which data files to read
# for prefix extraction and content creation.
# When running on App Engine, use full set of files.
# When running locally, use a smaller enumeration of files.
if os.getenv("GAE_APPLICATION"):
    FILE_ENUMERATE_PATTERN = "*"
else:
    FILE_ENUMERATE_PATTERN = "*1*"
